import re
import requests
from bs4 import BeautifulSoup as bs
import json
from time import sleep
import pandas as pd
import threading 
import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from pprint import pprint

urls = ['https://free-proxy-list.net/',
        'https://www.sslproxies.org/',
        'https://www.proxy-list.download/HTTPS',
        'https://proxylist.geonode.com/api/proxy-list?limit=200&page=1&sort_by=lastChecked&sort_type=desc&protocols=https',
        ]
proxies_lst= []
dataframe_list = []
api_url= []

# proxy extraction
def extraction():
    for url in range(len(urls)):
        soup = bs(requests.get(urls[url]).content, "html.parser")
        soup_str=str(soup)
        print(f'processing with - {urls[url]}')
        if 'table table-striped table-bordered' in soup_str:
            for row in soup.find("table", attrs={"class": "table table-striped table-bordered"}).find_all("tr")[1:]:
                tds = row.find_all("td")
                try:
                    ip = tds[0].text.strip()
                    port = tds[1].text.strip()
                    Https = tds[6].text.strip()
                    host = f"{ip}:{port}"
                    if Https == "yes":
                        proxies_lst.append(host)
                except IndexError:
                    continue
        elif 'table table-bordered table-striped dataTable dtr-inline' in soup_str:
            for row in soup.find("table", attrs={"class": "table table-bordered table-striped dataTable dtr-inline"}).find_all("tr")[1:]:
                tds = row.find_all("td")
                try:
                    ip = tds[0].text.strip()
                    port = tds[1].text.strip()
                    host = f"{ip}:{port}"
                    proxies_lst.append(host)
                except IndexError:
                    continue
        elif 'https://proxylist.geonode.com/api/proxy-list?limit=200&page=1&sort_by=lastChecked&sort_type=desc&protocols=https' == urls[3]:    
            try:
                r = requests.get(urls[3])
                data = r.text
                result = json.loads(data)
                for resultcheck in result['data']:
                    if 'ip' in resultcheck:
                        ip = resultcheck['ip']
                        # print(ip)
                    if 'port' in resultcheck:
                        port = resultcheck['port']
                        # print(port)
                        host = f'{ip}:{port}'
                        proxies_lst.append(host)
            except:
                print('no data in website')
                continue
        else:
            print('No links found')
        print(len(proxies_lst))

# Proxy test processing
def processing():
    n=50
    az=0
    x = [proxies_lst[i:i + n] for i in range(0, len(proxies_lst), n)]
    for i in range(len(x)):
        # print(f'processing proxies_lst with part links - {i} - th list')
        # conversion of extracted proxies for post
        s=str(x[i])
        a=re.sub("'","", s)
        a=re.sub(","," --- ", a)
        a=re.sub(r"[\[\]]","", a)
        a=re.sub("\s\s"," ", a)
        json_data={'proxies':a}
        headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://www.proxynova.com',
        'Referer': 'https://www.proxynova.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        }
                
        proxies ={
                
                # 'https': 'https://110.145.200.50:10000',     
        }
        s = requests.Session()
        response_1 = s.post('https://api.proxynova.com/proxychecker/jobs/', headers=headers, json=json_data,proxies=proxies)
        res = json.loads(response_1.text)
        # print(res)
        # testing of coverted proxies
        task_id =res['task_id']
        url = f'https://api.proxynova.com/proxychecker/jobs/{task_id}'
        response_2 = s.get(url,headers=headers,proxies=proxies)
        # print(url)
        api_url.append(url)
    for j in range(len(api_url)):
        r = requests.get(api_url[j])
        data = r.text
        result = json.loads(data)
        print(f'processed: {api_url[j]}')
        for resultcheck in result['proxies']:
            json_dict ={}
        #ip    
            if 'ip' in resultcheck:
                ip=resultcheck['ip']
        #port
            if 'port' in resultcheck:
                port = resultcheck['port']
        #country code
            if 'country_code' in resultcheck:
                country_code = resultcheck['country_code']
        #country name
            if 'country_name' in resultcheck:
                country_name = resultcheck['country_name']
        #time
            if 'time' in resultcheck:
                time = resultcheck['time']
        #cityName
            if 'cityName' in resultcheck:
                cityName = resultcheck['cityName']
        #status
            if 'status' in resultcheck:
                status = resultcheck['status']

        #saving as dict of list for dataframe conversion 
                name_list=['ip','port','country_code','country_name','cityName','time','status']
                json_dict.__setitem__(name_list[0],ip)
                json_dict.__setitem__(name_list[1],port)
                json_dict.__setitem__(name_list[2],country_code)
                json_dict.__setitem__(name_list[3],country_name)
                json_dict.__setitem__(name_list[4],cityName)
                json_dict.__setitem__(name_list[5],time)
                json_dict.__setitem__(name_list[6],status)
            # print(json_dict)
            dataframe_list.append(json_dict)
            az+=1
        # print('------------------------------------------------------------------------')
    print(az)

# data-frame contanier 
def make_dataframe():
    df = pd.DataFrame(dataframe_list)
    status_df =df[(df['status'] == 1)]
    print(status_df)
    inputn = input('Enter 1 to sort by time:')
    if inputn == '1':
        status_df.sort_values(by=['time'], ascending=True,inplace=True)
        print('--------------sorted--------------')
        print(status_df)

# main driver code
if __name__ == '__main__':
    THREAD_COUNT = 1
    threads = []
    for i in range(THREAD_COUNT):
        thread_A = threading.Thread(target=extraction)
        thread_B = threading.Thread(target=processing)

        thread_A.start()
        threads.append(thread_A)
        thread_A.join()

        thread_B.start()
        threads.append(thread_B)
        thread_B.join()
    make_dataframe()
