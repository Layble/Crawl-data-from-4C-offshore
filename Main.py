# encoding=utf-8

'''
selenium+chromedriver
1、Check chrome and chromedrive version
2、Chrome --- macos: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
                          windows: chrome.exe --remote-debugging-port=
3、Extract URL from 《Detail_urlsURL》 python hqq_spider.py
4、Detail_urls by second_extract_html()
5、《404_url.txt》 and 《detail_err.txt》 have some errors, have to be manually collected
7、《Result.json》 first 500 items have no urls
'''


import os
import json
import time
import regex as re
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def getDriver():
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["pageLoadStrategy"] = "none"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", '127.0.0.1:9222')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver


driver = getDriver()
wait = WebDriverWait(driver, 10)


def download(url):
    driver.get(url)
    for i in range(10):
        html = driver.page_source
        if 'Body_Main_Content_NameLabel' in html:
            break
        else:
            time.sleep(1)
    time.sleep(3.1)
    return html


# Parse the source code
def extract_detail(html, result, url):
    def re_search(html_str, re_str):
        re_result = re.search(re_str, html_str)
        if re_result:
            result = re.sub(r'<.*?>', '', re_result.group())
        else:
            result = ''
        return result
    result['url'] = url
    result['name'] = re_search(html, r'(?<=<div id="Body_Main_Content_NameLabel" class="col-6">).*?(?=</div>)')
    result['country'] = re_search(html, r'(?<=<div id="Body_Main_Content_CountryLabel" class="col-6">).*?(?=</div>)')
    result['development_status'] = re_search(html, r'(?<=<div id="Body_Main_Content_WindFarmStatusLabel" class="col-6">).*?(?=</div>)')
    result['first_power'] = re_search(html, r'(?<=<div id="Body_Main_Content_GeneratingYearLabel" class="col-6">).*?(?=</div>)')
    result['windfarm_capacity'] = re_search(html,
                                  r'(?<=<div id="Body_Main_Content_CapacityMWMaxLabel" class="col-6">).*?(?=</div>)')
    result['max_turbines'] = re_search(html, r'(?<=<div id="Body_Main_Content_NoTurbinesMaxLabel" class="col-6">).*?(?=</div>)')
    result['turbine_model'] = re_search(html, r'(?<=<div id="Body_Main_Content_ModelLabel" class="col-6">).*?(?=</div>)')
    result['mean_windspeed'] = re_search(html, r'(?<=<div id="Body_Main_Content_WindspeedLabel" class="col-6">).*?(?=</div>)')
    result['area'] = re_search(html, r'(?<=<div id="Body_Main_Content_AreaLabel" class="col-6">).*?(?=</div>)')
    result['depth_range'] = re_search(html, r'(?<=<div id="Body_Main_Content_DeveloperDepthLabel" class="col-6">).*?(?=</div>)')
    result['distance_from_shore'] = re_search(html,
                                    r'<div id="Body_Main_Content_developerDistanceLabel" class="col-6">10.500 km</div>')
    json_str = json.dumps(result, ensure_ascii=False)
    with open('Code/Result.json', 'a+') as f:
        f.write(json_str)
        f.write('\n')
    print(json_str)


def second_extract(html, first_url):
    urls = re.findall(r'(?<=<p class="font-weight-bold mb-0"><a href=\').*?(?=\'>)', html)
    result_urls = []
    for url in urls:
        result_urls.append(first_url + url)
        print('SECOND: ', first_url + url)
        with open('Code/Detail_urls', 'a+') as f:
            f.write(first_url + url)
            f.write('\n')
    return result_urls


def second_extract_html():
    url_head = 'https://www.4coffshore.com/windfarms/'
    file_list = os.listdir('Code/list_html')
    for file_name in file_list:
        f = open('Code/list_html/' + file_name)
        html = f.read()
        f.close()
        url = url_head + file_name.replace('.html', '') + '/'
        second_extract(html, url)


def detail_extract_start():
    with open('Code/Detail_urls', 'r') as f:
        for line in f:
            url = line.replace('\n', '')
            print('DOWN URL: %s' % url)
            for i in range(2):   # Each URL max two times
                result = {}
                html = download(url)
                extract_detail(html, result, url)
                if result['name'] == '':
                    if i == 1:
                        break
                    if '404 - Page Not Found' in html:
                        # 404 page cannot be found
                        print('404 Page Not Found： %s' % url)
                        with open('Code/404_url.txt', 'a+') as f:
                            f.write(url)
                            f.write('\n')
                    else:
                        # if verification code
                        with open('Code/detail_err.txt', 'a+') as f:
                            f.write(url)
                            f.write('\n')
                        time.sleep(60)
                else:
                    break
            print('SUCCESS URL: %s' % url)


def start():
    # second_extract_html()   # Docode list，get url hqq_detail_urls
    detail_extract_start()  # Get all information


start()

