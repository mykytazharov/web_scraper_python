
##libraries
import requests
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import re
import geopandas
import json
import csv
from itertools import chain


##function to get proxies
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:100]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


## define function to perform scraping
def do_scrape(city, proxy):
    #crowl web-page
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=http://%s' % proxy)
        
    url = "
    driver = webdriver.Chrome('', chrome_options=chrome_options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    #clean data
    all_info=soup.findAll(attrs={"data-react-class" : "app"})
    parkings=json.loads(all_info[0]['data-react-props'])['locations']['all']
    items=[]
    separator = ', '
    
    for d in parkings:
        # print(d)
        if 'name' in d['properties']:
            name = d['properties']['name']
        else:
            name = ""
        if 'capacity' in d['properties']:
            capacity = d['properties']['capacity']
        else:
            capacity = 1
        if 'max_height' in d['properties']:
            max_height = d['properties']['max_height']
        else:
            max_height = ""
        if 'typeid' in d['properties']:
            typeid = d['properties']['typeid']
        else:
            typeid = ""
        if 'city' in d['properties']:
            city = d['properties']['city']
        else:
            city = ""
        if 'prices' in d['properties']:
            if 'entries' in d['properties']['prices']:
                prices = d['properties']['prices']['entries']
                if 'costs' in prices[0]:
                    prices_full=" , ".join(list(map(lambda x: ''+x['amount_text']+' - '+x['duration_text'], prices[0]['costs'])))
                else:
                    prices_full=""
                if 'maxstay_mins' in d['properties']['prices']['entries'][0]:
                    maxstay_mins = d['properties']['prices']['entries'][0]['maxstay_mins']
                else:
                    maxstay_mins=''
            else:
                prices_full = ""
                maxstay_mins=''       
        else:
            prices_full = ""
            maxstay_mins=''
        if 'surface_type' in d['properties']:
            surface_type = d['properties']['surface_type']
        else:
            surface_type = ""
        if 'address' in d['properties']:
            address = separator.join(d['properties']['address'][-2:])
        else:
            address = "" 
        if 'hours' in d['properties']:
            data=d['properties']['hours']['periods']
            if len(data)>=1:
                hours='From '+str(data[0]['from'])+' to '+str(data[0]['to'])+' , '+str(data[0]['day_text'])
            else:
                hours=""
        else:
            hours = ""
        if 'geometries' in d['geometry']:
            longitude = d['geometry']['geometries'][0]['coordinates'][0]
            latitude =  d['geometry']['geometries'][0]['coordinates'][1]
        else:
            hours = ""     
        items.append({
            'name': name,
            'address': address,
            'capacity': capacity,
            'hours': hours,
            'max_height':max_height,
            'maxstay_mins': maxstay_mins,
            'prices': prices_full,
            'surface_type': surface_type,
            'longitude': longitude,
            'latitude': latitude
        })
        
    dataFrame=pd.DataFrame(items)
    return dataFrame


##scrape the data
def crawl_city(city, proxy):
    try:
        data = do_scrape(city, proxy)
        # store DataFrame in list
        appended_data.append(data)
        print("success"+city+proxy)
    except:
        #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
        #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url 
        #print("Skipping. Connnection error" + city)
        print("error"+city+proxy)
        proxies = get_proxies()
        proxy = next(proxy_pool)
        crawl_city(city, proxy)