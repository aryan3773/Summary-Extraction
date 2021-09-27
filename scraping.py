#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
time.sleep(10)

import requests
import requests_random_user_agent
import webbrowser

s = requests.Session()
print(s.headers['User-Agent'])
s.proxies = {"http": "http://61.233.25.166:80"}

#r = s.get("http://www.google.com")
#print(r.text)


# In[2]:


# Function for Extracting relevant links

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

    print('Total number of links captured are', len(list_of_links))
    
    # Capturing the complete URL

    url_list = []
    not_retrieved = []
    
    for i in range(len(list_of_links)):
        #print('Starting for', i)
        url = list_of_links[i]
        #print(url) #edgar/data/1326801/0001326801-20-000076.txt

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
            not_retrieved.append(url) 
            print("Can't form a link for", i)
            
        if(i%500 == 0):
            print("Completed till", i)
    print('Not retrieved for', len(not_retrieved), 'documents')
    
    return [url_list, not_retrieved]


# In[3]:


# Function for Extracting relevant links

def get_relevant_documents(url_to_use, file_name):
    r = requests.get(url_to_use, proxies={"http":"http://myproxy:3129"})
    raw_10k = r.text
    document = raw_10k
    a, b, c, d = 0, 0, 0, 0
    
    # Write the regex
    regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|7A|7|8|16)\.{0,1})|(ITEM\s(1A|1B|7A|7|8|16))')
    # Use finditer to math the regex
    matches = regex.finditer(document)
    item_16_raw = ""
    
    try:
        # Create the dataframe
        test_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])

        test_df.columns = ['item', 'start', 'end']
        test_df['item'] = test_df.item.str.lower()

        test_df.replace('&#160;',' ',regex=True,inplace=True)
        test_df.replace('&nbsp;',' ',regex=True,inplace=True)
        test_df.replace(' ','',regex=True,inplace=True)
        test_df.replace('\.','',regex=True,inplace=True)
        test_df.replace('>','',regex=True,inplace=True)

        pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')
        pos_dat.set_index('item', inplace=True)

        item_16_raw = document[pos_dat['start'].loc['item16']:].lower()
        word_list = ['none', 'not applicable', 'n/a', 'exhibits', 'omitted at', 'elected not to', 'not required', 'intentionally left blank', 'not providing']
        if(len(item_16_raw) != 0):
            f = True
            for word in word_list:
                if(word in item_16_raw[:15000]):
                    f = False
                    break
                    
            if(f):
                file = open(file_name + ".txt", "w") 
                file.write(document)
                file.close()
                a += 1
                #print('File made for link')

            else:
                b += 1
                #print('Document contains none or n/a or not applicable')

        else:
            c += 1
            #print('No content in item 16')

    except:
        d += 1
        #print("Could n't match item 16 or facing some other error")
            
    return a


# In[8]:


start = time.time()

p = 1
t = 1

year = 2015
quarter = 'QTR1'

url_2015_Q1, x_Q1 = get_links(2015, 'QTR1')

file = open("00_" + str(year) + "_" + quarter + ".txt", 'w')
for i in url_2015_Q1:
    file.write(i + '\n')

file.write('*'*25 + '\n')
for i in x_Q1:
    file.write(i + '\n')
file.close()
    
useful_url_2015_Q1 = []
not_retrieved_2015_Q1 = []
not_matched_2015_Q1 = []

name = "2015_QTR1_"

for link in url_2015_Q1:
    try:
        a = get_relevant_documents(link, name + str(p))
        if(a == 1):
            p += 1
            useful_url_2015_Q1.append(link)
        else:
            not_matched_2015_Q1.append(link)
            
    except:
        print("Error due to failed connection attempt for" , t)
        not_retrieved_2015_Q1.append(link)
        
    if(t%250 == 0):
        print("Iterated through", t, 'files')
    t += 1
    
file = open("01_" + str(year) + "_" + quarter + ".txt", 'w')
for i in useful_url_2015_Q1:
    file.write(i + '\n')
    
file.write('*'*25 + '\n')
for i in not_retrieved_2015_Q1:
    file.write(i + '\n')
    
file.write('*'*25 + '\n')
file.write('*'*25 + '\n')
for i in not_matched_2015_Q1:
    file.write(i + '\n')
    
file.close()

end = time.time()
print(len(useful_url_2015_Q1))
print('Time taken =', round((end-start)/60, 2), 'minutes')


# In[7]:


start = time.time()

p = 1
t = 1

year = 2015
quarter = 'QTR2'

url_2015_Q2, x_Q2 = get_links(2015, 'QTR2')

file = open("00_" + str(year) + "_" + quarter + ".txt", 'w')
for i in url_2015_Q2:
    file.write(i + '\n')

file.write('*'*25 + '\n')
for i in x_Q2:
    file.write(i + '\n')
file.close()

useful_url_2015_Q2 = []
not_retrieved_2015_Q2 = []
not_matched_2015_Q2 = []

name = "2015_QTR2_"

for link in url_2015_Q2:
    try:
        a = get_relevant_documents(link, name + str(p))
        if(a == 1):
            p += 1
            useful_url_2015_Q2.append(link)
        else:
            not_matched_2015_Q2.append(link)
            
    except:
        print("Error due to failed connection attempt for" , t)
        not_retrieved_2015_Q2.append(link)
        
    if(t%250 == 0):
        print("Iterated through", t, 'files')
    t += 1
    
file = open("01_" + str(year) + "_" + quarter + ".txt", 'w')
for i in useful_url_2015_Q2:
    file.write(i + '\n')
    
file.write('*'*25 + '\n')
for i in not_retrieved_2015_Q2:
    file.write(i + '\n')
    
file.write('*'*25 + '\n')
file.write('*'*25 + '\n')
for i in not_matched_2015_Q2:
    file.write(i + '\n')
    
file.close()

end = time.time()
print(len(useful_url_2015_Q2))
print('Time taken =', round((end-start)/60, 2), 'minutes')


# In[6]:


start = time.time()

p = 1
t = 1

year = 2015
quarter = 'QTR3'

url_2015_Q3, x_Q3 = get_links(2015, 'QTR3')

file = open("00_" + str(year) + "_" + quarter + ".txt", 'w')
for i in url_2015_Q3:
    file.write(i + '\n')

file.write('*'*25 + '\n')
for i in x_Q3:
    file.write(i + '\n')
file.close()

useful_url_2015_Q3 = []
not_retrieved_2015_Q3 = []
not_matched_2015_Q3 = []

name = "2015_QTR3_"

for link in url_2015_Q3:
    try:
        a = get_relevant_documents(link, name + str(p))
        if(a == 1):
            p += 1
            useful_url_2015_Q3.append(link)
        else:
            not_matched_2015_Q3.append(link)
            
    except:
        print("Error due to failed connection attempt for" , t)
        not_retrieved_2015_Q3.append(link)
        
    if(t%250 == 0):
        print("Iterated through", t, 'files')
    t += 1
    
file = open("01_" + str(year) + "_" + quarter + ".txt", 'w')
for i in useful_url_2015_Q3:
    file.write(i + '\n')
    
file.write('*'*25 + '\n')
for i in not_retrieved_2015_Q3:
    file.write(i + '\n')
    
file.write('*'*25 + '\n')
file.write('*'*25 + '\n')
for i in not_matched_2015_Q3:
    file.write(i + '\n')
    
file.close()

end = time.time()
print(len(useful_url_2015_Q3))
print('Time taken =', round((end-start)/60, 2), 'minutes')


# In[4]:


start = time.time()

p = 1
t = 1

year = 2015
quarter = 'QTR4'

url_2015_Q4, x_Q4 = get_links(2015, 'QTR4')

file = open("00_" + str(year) + "_" + quarter + ".txt", 'w')
for i in url_2015_Q4:
    file.write(i + '\n')

file.write('*'*25 + '\n')
for i in x_Q4:
    file.write(i + '\n')
file.close()

useful_url_2015_Q4 = []
not_retrieved_2015_Q4 = []
not_matched_2015_Q4 = []

name = "2015_QTR4_"

for link in url_2015_Q4:
    try:
        a = get_relevant_documents(link, name + str(p))
        if(a == 1):
            p += 1
            useful_url_2015_Q4.append(link)
        else:
            not_matched_2015_Q4.append(link)
            
    except:
        print("Error due to failed connection attempt for" , t)
        not_retrieved_2015_Q4.append(link)
        
    if(t%250 == 0):
        print("Iterated through", t, 'files')
    t += 1
    
file = open("01_" + str(year) + "_" + quarter + ".txt", 'w')
for i in useful_url_2015_Q4:
    file.write(i + '\n')
    
file.write('*'*25 + '\n')
for i in not_retrieved_2015_Q4:
    file.write(i + '\n')
    
file.write('*'*25 + '\n')
file.write('*'*25 + '\n')
for i in not_matched_2015_Q4:
    file.write(i + '\n')
    
file.close()

end = time.time()
print(len(useful_url_2015_Q4))
print('Time taken =', round((end-start)/60, 2), 'minutes')


# In[5]:


print(len(useful_url_2015_Q4))
for i in useful_url_2015_Q4:
    webbrowser.open(i)

