#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
time.sleep(10)


# In[2]:


import requests
import requests_random_user_agent

s = requests.Session()
print(s.headers['User-Agent'])


# In[3]:


# Item 16 not present
#r = requests.get('https://www.sec.gov/Archives/edgar/data/1288776/000165204416000012/goog10-k2015.htm')

# doc_type = 10-K not found, use table info for finding summary
#r = requests.get('https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926.htm')

# Item 16 returns None as expected and returning texts for other items as well
r = requests.get('https://www.sec.gov/Archives/edgar/data/320193/000032019318000145/0000320193-18-000145.txt')

# Contains item 16
#r = requests.get('https://www.sec.gov/Archives/edgar/data/0001163302/000116330221000013/x-20201231.htm')

# doc_type = 10-K not found, use table info for finding summary, Item-16 not present
#r = requests.get('https://www.sec.gov/Archives/edgar/data/1000045/000156459019023956/nick-10k_20190331.htm')

# Another different type of doc, besides item-16 it has no table of content as well
#r = requests.get('https://www.sec.gov/Archives/edgar/data/1000683/000121390019005351/f10k2018_blondertongue.htm')

raw_10k = r.text


# In[4]:


print(raw_10k[0:2000])


# In[5]:


# Regex to find <DOCUMENT> tags
doc_start_pattern = re.compile(r'<DOCUMENT>')
doc_end_pattern = re.compile(r'</DOCUMENT>')
# Regex to find <TYPE> tag prceeding any characters, terminating at new line
type_pattern = re.compile(r'<TYPE>[^\n]+')


# In[6]:


# Create 3 lists with the span idices for each regex

### There are many <Document> Tags in this text file, each as specific exhibit like 10-K, EX-10.17 etc
### First filter will give us document tag start <end> and document tag end's <start> 
### We will use this to later grab content in between these tags
doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]

### Type filter is interesting, it looks for <TYPE> with Not flag as new line, ie terminare there, with + sign
### to look for any char afterwards until new line \n. This will give us <TYPE> followed Section Name like '10-K'
### Once we have have this, it returns String Array, below line will with find content after <TYPE> ie, '10-K' 
### as section names
doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]


# In[7]:


document = {}

# Create a loop to go through each section type and save only the 10-K section in the dictionary
for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
    if doc_type == '10-K':
        document[doc_type] = raw_10k[doc_start:doc_end]


# In[8]:


# display excerpt the document
document['10-K'][0:500]


# In[9]:


# Write the regex
regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|7A|7|8|16)\.{0,1})|(ITEM\s(1A|1B|7A|7|8|16))')

# Use finditer to math the regex
matches = regex.finditer(document['10-K'])

# Write a for loop to print the matches
for match in matches:
    print(match)


# In[10]:


# Matches
matches = regex.finditer(document['10-K'])

# Create the dataframe
test_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])

test_df.columns = ['item', 'start', 'end']
test_df['item'] = test_df.item.str.lower()

# Display the dataframe
test_df.head()


# In[11]:



# Get rid of unnesesary charcters from the dataframe
test_df.replace('&#160;',' ',regex=True,inplace=True)
test_df.replace('&nbsp;',' ',regex=True,inplace=True)
test_df.replace(' ','',regex=True,inplace=True)
test_df.replace('\.','',regex=True,inplace=True)
test_df.replace('>','',regex=True,inplace=True)

# display the dataframe
test_df.head()


# In[12]:


# Drop duplicates
pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')

# Display the dataframe
pos_dat


# In[13]:



# Set item as the dataframe index
pos_dat.set_index('item', inplace=True)

# display the dataframe
pos_dat


# In[14]:


# Get Item 1a
item_1a_raw = document['10-K'][pos_dat['start'].loc['item1a']:pos_dat['start'].loc['item1b']]

# Get Item 7
item_7_raw = document['10-K'][pos_dat['start'].loc['item7']:pos_dat['start'].loc['item7a']]

# Get Item 7a
item_7a_raw = document['10-K'][pos_dat['start'].loc['item7a']:pos_dat['start'].loc['item8']]

# Get Item 16
item_16_raw = document['10-K'][pos_dat['start'].loc['item16']:pos_dat['start'].loc['item16']]


# In[15]:


print(item_1a_raw[0:1000])
print('*'*50)

item_1a_content = BeautifulSoup(item_1a_raw, 'lxml')
print(item_1a_content.prettify()[0:1000])
print('*'*50)

# Final text after cleaning
print(item_1a_content.get_text("\n\n")[0:5000])


# In[16]:


print(item_16_raw[0:1000])
print('*'*50)

item_16_content = BeautifulSoup(item_16_raw, 'lxml')
print(item_16_content.prettify()[0:1000])
print('*'*50)

# Final text after cleaning
print(item_16_content.get_text("\n\n")[0:1500])

