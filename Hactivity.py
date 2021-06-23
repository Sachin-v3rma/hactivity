#!/bin/python3
"""
Made with <3 by Sachin Verma ( Twitter : @vm_sachin )
Download ChromeWebdriver : https://sites.google.com/a/chromium.org/chromedriver/downloads
Clean up Chrome Processes after run :
                        Windows : taskkill /im chromedriver.exe /f 
                        Linux   : killall chromium
"""
from requests.exceptions import ConnectionError
from selenium import webdriver
from selenium.webdriver.common import service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs4
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
import concurrent.futures, re
import argparse, os ,time

def chrome_driver():
    try:
        os.environ['WDM_LOG_LEVEL'] = '0'
        if browser == 'chrome':
            b_type = ChromeType.GOOGLE
        elif browser == 'chromium':
            b_type = ChromeType.CHROMIUM

        if browser == 'firefox':
            from selenium.webdriver.firefox.options import Options
        else:
            from selenium.webdriver.chrome.options import Options
        options = Options()
        options.headless = True
        if browser == 'firefox':
            from webdriver_manager.firefox import GeckoDriverManager
            from selenium.webdriver.firefox.service import Service
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
        else:
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=b_type).install()), options=options)
        return driver
    except ValueError:
        print('[-] Browser not found !!')

def page_scroll(driver):
    '''
    Visits the page and keeps scrolling to bottom of page until it fetches all reports.
    '''
    while True:
        try:
            WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'ahref daisy-link daisy-link hacktivity-item__publicly-disclosed spec-hacktivity-item-title')]")))
            html = driver.find_element_by_tag_name('html')
            html.send_keys(Keys.END)
            driver.find_element_by_xpath('//div[contains(@class, "loading-indicator__inner")]')
        except NoSuchElementException:
            break
        except (TimeoutException,KeyboardInterrupt):
            pass

def report_finder(url):
    limit_counter = 0
    driver = chrome_driver()
    driver.get(url)
    page_scroll(driver)
    soup = bs4(driver.page_source,'lxml')
    for i in soup.find_all('a',class_='ahref daisy-link daisy-link hacktivity-item__publicly-disclosed spec-hacktivity-item-title'):
        if limit_counter == limit:
            break
        if report == True:
            print(f"{i['href']} : {i.text}")
        report_urls.add(i['href'])
        limit_counter += 1
    driver.quit()

def report_parser(url):     # Fetches the report and finds the subdomains
    driver = chrome_driver()
    driver.get(url)
    try:
        WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, "//*[@class='timeline-container-content spec-vulnerability-information']")))
    finally:
        keywords = []
        reg = re.compile(f'{regexs["http_urls"]}|{regexs["urls"]}')
        soup = bs4(driver.page_source, 'html.parser')
        driver.quit()
        
        # Find URL from Title and Asset
        for i in soup.find_all('div', class_=["report-heading__report-title break-all spec-report-title","text-truncate break-word"]):
            for j in re.split(' |\n|-|\[|\]|\(|\)|:|"|\'', i.text):
                if j != '':
                    keywords.append(j)
            
            {output.add(re.sub('https?://','',k.lower())) for k in re.findall(reg, i.text)}
        
        # Find URL from Report
        for i in soup.find_all('div', class_="timeline-container-content spec-vulnerability-information"):
            hurls = re.findall(regexs["http_urls"], i.text)
            for k in hurls:
                m = re.sub('https?://','',k)
                if re.findall('|'.join(keywords), m, re.IGNORECASE):
                    if len(m.split('.')) > 2:
                        output.add(m.lower())
        
def start(url:set):
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(report_parser, url)

def output_():
    with open ('tld.txt','r') as tld: # Matches results for a valid TLD. Used to filter data for invalid URLs.
        for t in tld.readlines():
            t = f'\.{t.strip()}$'
            for i in output:
                if re.findall(t, i):
                        print(i)

if __name__ == "__main__":
    report_urls = set()
    output = set()
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)
    regexs = {"urls" : "(?:[a-zA-Z0-9@*:._-]{0,}\.)?[a-zA-Z0-9@:_-]{1,}\.[a-zA-Z]{2,5}","http_urls": "(?:https?)://[^,;:()\"\n<>`'/\s]+"}
    
    help_msg = '''
    This Program Scrapes subdomains/domains from Hackerone reports of any given keyword (mailru, xss, ssrf,etc).'''

    arg_parser = argparse.ArgumentParser(description=help_msg, formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument('-r', help='Find URL and Title only of reports', action='store_true',dest='reports')
    arg_parser.add_argument('-l', help='Fetch data from n number of reports', metavar='',type=int, dest='limit')
    arg_parser.add_argument('-t', help='Number of threads (Default : 5)', metavar='', type=int, default=5, dest='threads')
    arg_parser.add_argument('keyword', help='Company Name or Keyword')
    arg_parser.add_argument('-b', help='Browser to use (Default : Chromium)\n• chrome\n• chromium\n• firefox', metavar='', choices=['chrome','chromium','firefox'], default='chromium', dest='browser')
    args = arg_parser.parse_args()
    
    # Input
    threads = args.threads
    report = args.reports
    browser = args.browser
    if args.limit:
        limit = args.limit
    else:
        limit = None
    hacktivity_url = f'https://hackerone.com/hacktivity?querystring={args.keyword}'

    # Start
    try:
        start_time = time.time()
        report_finder(hacktivity_url)
        print(f'[+] Found {len(report_urls)} reports')
        if report == False:
            start(report_urls)
            output_()
        print(f"[+] Finished in {time.time() - start_time} seconds")
    except KeyboardInterrupt:
        print("[-] Exiting")
    except WebDriverException:
        print('[-] Invalid Chromedriver Path')
    except ConnectionError:
        print('[-] Connection Error')
    except Exception:
        pass