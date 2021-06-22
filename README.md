# Hactivity
A Tool to find subdomains from Hackerone reports of a given company or a search term (xss, ssrf, etc). It can also print out URL and Title of reports.

## Installation:
> Supported Browsers : Google Chrome, Chromium or Firefox.
> By default it uses chromium.

### To Install Hactivity
```
$ git clone https://github.com/Sachin-v3rma/hactivity
$ cd hactivity && pip install -r requirements.txt
$ python3 Hactivity.py -h
```

## Usage:

It searches the hackerone for a given keyword which can be a company name or vulnerabilty type. Hackerone uses javascript/dynamic pages thats why its not possible to fetch large amounts of data quickly. Also don't use like 20,30,100,etc threads, it will burn your poor little PC. It uses multiple browser instances so choose wisely.
> **NOTE : Use Exact Names of company/organization. Example : mailru (For mail.ru)**

### Example usage :

```bash
$ python3 Hactivity.py mailru -l 100
$ python3 Hactivity.py ssrf -r
$ python3 Hactivity.py xss -b firefox -l 50 -t 2
```


| Flag | Description |
|------|-------------|
|-h, --help  |show this help message and exit|
|-l 100      |Fetch data from n number of reports|
|-t 2        |Number of threads (Default : 5)|
|-r          |Find URL and Title only of reports|
|-b [ chrome, chromium, firefox ]          |Browser to use (Default : Chromium)|

<a href="https://www.buymeacoffee.com/sachinvm" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee" height="41" width="174"></a>
