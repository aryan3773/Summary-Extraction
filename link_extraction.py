#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Importing Libraries

import time
import os
from datetime import datetime
from secedgar.filings import Filing, FilingType
from secedgar.cik_lookup import get_cik_map
time.sleep(10)
# os.getcwd()

import bs4 as bs
import requests
import pandas as pd
import re
time.sleep(10)


# In[2]:


# To avoid 'user limit exceeded'

import requests_random_user_agent

s = requests.Session()
print(s.headers['User-Agent'])


# In[3]:


cik = get_cik_map()['ticker']
print("Total number of companies are", len(cik))

# outputPath = "C:\\Users\\ARYAN\\Desktop\\9th Sem\\Project"


# In[4]:


#  Downloading 10-K files using SEC Library

'''
start = time.time()

total = 0

for idx, ck in enumerate(list(cik.keys())[:11]):
    print(idx, ck, cik[ck])
    
    temp = Filing(cik_lookup = list(cik.keys())[idx],
                filing_type = FilingType.FILING_10K,
                start_date = datetime(2016, 1, 1),
                end_date = datetime(2022, 1, 1),
                user_agent = 'aryanpcm@gmail.com')
    
    try:
        print("Filings found")
        temp.save(outputPath)
        
    except:
        total += 1
        print("No filings found")

end = time.time()
print('Total Time taken -----', round((end-start)/60, 2), 'minutes')'''


# In[4]:


list_of_companies = cik.keys()
lookup_table = cik


# In[5]:


# Checking the content of cik
#cik


# In[32]:


# Extracting relevant links

year = 2020
quarter = 'QTR1'

#get name of all filings 
download = requests.get(f'https://www.sec.gov/Archives/edgar/full-index/{year}/{quarter}/master.idx').content
download = download.decode("utf-8").split('\n')


# In[7]:


# Checking Content of download
print(download[2001:2011])


# In[33]:


# build the first part of the url

filing = '10-K'
list_of_links = []

for item in download:
    company = item
    company = company.strip()
    splitted_company = company.split('|')
    if(len(splitted_company) == 5):
        if(splitted_company[-3] == '10-K'):
            url = splitted_company[-1]
            list_of_links.append(url)
        
print('Total number of links captured are', len(list_of_links))


# In[9]:


# Sample URL creation

url = list_of_links[5]
print(url)

url2 = url.split('-') 
url2 = url2[0] + url2[1] + url2[2]
url2 = url2.split('.txt')[0]
print(url2) #edgar/data/1326801/000132680120000076

to_get_html_site = 'https://www.sec.gov/Archives/' + url
data = requests.get(to_get_html_site).content
data = data.decode("utf-8") 
data = data.split('FILENAME>')
# print(data[1])
data = data[1].split('\n')[0]

url_to_use = 'https://www.sec.gov/Archives/'+ url2 + '/' + data
print(url_to_use)  # Returns a link like https://www.sec.gov/Archives/edgar/data/1001601/000149315219005484/form10-k.htm


# In[10]:


r = requests.get('https://www.sec.gov/Archives/edgar/data/1001601/000149315219005484/form10-k.htm')
raw_10k = r.text


# In[11]:


raw_10k


# In[16]:


# Capturing the complete URL

url_list = []

for i in range(len(list_of_links)):
    print('Starting for', i)
    url = list_of_links[i]
    print(url) #edgar/data/1326801/0001326801-20-000076.txt

    url2 = url.split('-') 
    url2 = url2[0] + url2[1] + url2[2]
    url2 = url2.split('.txt')[0]
    #print(url2) #edgar/data/1326801/000132680120000076
    try:
        to_get_html_site = 'https://www.sec.gov/Archives/' + url
        data = requests.get(to_get_html_site).content
        data = data.decode("utf-8") 
        data = data.split('FILENAME>')
        #print(data[1])
        data = data[1].split('\n')[0]
        url_to_use = 'https://www.sec.gov/Archives/'+ url2 + '/'+data
        #print(url_to_use)
        url_list.append(url_to_use)
        
    except:
        print("Can't form a link")
print(len(url_list))


# In[17]:


# No specific point of termination
print('Loop breaking at', i)


# In[14]:





# In[15]:


# URL index at which loop terminated

url = list_of_links[203]
print(url)

url2 = url.split('-') 
url2 = url2[0] + url2[1] + url2[2]
url2 = url2.split('.txt')[0]
print(url2) #edgar/data/1326801/000132680120000076

to_get_html_site = 'https://www.sec.gov/Archives/' + url
data = requests.get(to_get_html_site).content
data = data.decode("utf-8") 
data = data.split('FILENAME>')
# print(data[1])
data = data[1].split('\n')[0]

url_to_use = 'https://www.sec.gov/Archives/'+ url2 + '/' + data
print(url_to_use)  # Returns a link like https://www.sec.gov/Archives/edgar/data/1001601/000149315219005484/form10-k.htm


# In[15]:


# Inspecting data for ith index
print(data)


# In[20]:


import webbrowser
#webbrowser.open("https://www.sec.gov/Archives/edgar/data/1102432/000147793219001357/vkin_10k.htm")
for i in url_list[:5]:
    webbrowser.open(i)


# In[26]:


# Types of files
temp = []

for item in download:
    company = item
    company = company.strip()
    splitted_company = company.split('|')
    if(len(splitted_company) == 5):
        url = splitted_company[-3]
        temp.append(url)


# In[30]:


temp = list(set(temp))
#print(temp)

for i in temp:
    if('10-K' in i):
        print(i)


# In[36]:


def get_links(year, quarter):
    #get name of all filings 
    download = requests.get(f'https://www.sec.gov/Archives/edgar/full-index/{year}/{quarter}/master.idx').content
    download = download.decode("utf-8").split('\n')

    # build the first part of the url
    list_of_links = []
    for item in download:
        company = item
        company = company.strip()
        splitted_company = company.split('|')
        if(len(splitted_company) == 5): # '1007499|IFS SECURITIES, INC|X-17A-5|2019-06-14|edgar/data/1007499/9999999997-19-005663.txt'
            if(splitted_company[-3] == '10-K'):
                url = splitted_company[-1]
                list_of_links.append(url)

    return len(list_of_links)


# In[43]:


years = [2015, 2016, 2017, 2018, 2019, 2020]
quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
total = 0

for yr in years:
    for qtr in quarters:
        try:
            p = get_links(yr, qtr)
            print('The number of links in yr', yr, 'and Quarter', qtr, 'are', p)
            total += p
            
        except:
            print('Could not access for the year', yr, 'and Quarter', qtr)
            
print(total)


# In[44]:


print('The number of links in yr', 2017, 'and Quarter-3', 'are', get_links(2017, 'QTR3'))

