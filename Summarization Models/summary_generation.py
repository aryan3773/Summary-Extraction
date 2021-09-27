#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Importing libraries

# Pegasus trained on topcs like stock, markets, currencies, rate and cryptocurrencies.
from transformers import PegasusTokenizer, PegasusForConditionalGeneration

# BART (not domain specific)
from transformers import BartTokenizer, BartForConditionalGeneration, BartConfig

import nltk
import time
import os


# In[2]:


# Loading the model and the tokenizer 

#Pegasus
pegasus_tokenizer = PegasusTokenizer.from_pretrained("human-centered-summarization/financial-summarization-pegasus")
pegasus_model = PegasusForConditionalGeneration.from_pretrained("human-centered-summarization/financial-summarization-pegasus")

# BART
bart_tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
bart_model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')


# In[5]:


# Functions for generating a summary for a given text file consisting of multiple paragraphs
def summary_generation(text_file, model_name):
    file = open(text_file, encoding="utf8")
    paragraphs = file.read().split('\n')
    final_text = ""
    
    try:
        s = 0
        if(model_name == "pegasus"):
            final_file = open(text_file[:-4] + "_pegasus" + ".txt", "w")

            for para in paragraphs:
                input_ids = pegasus_tokenizer(para, return_tensors="pt", truncation=True).input_ids
                output = pegasus_model.generate(input_ids, num_beams=5, early_stopping=True)

                generated_text = pegasus_tokenizer.decode(output[0], skip_special_tokens=True)
                final_file.write(generated_text + '\n')
                final_text += generated_text + '\n'

        elif(model_name == "bart"):
            final_file = open(text_file[:-4] + "_bart" + ".txt", "w")

            for para in paragraphs:
                inputs = bart_tokenizer([para], return_tensors='pt', truncation=True)
                summary_ids = bart_model.generate(inputs['input_ids'], num_beams=5, early_stopping=True)

                generated_text = [bart_tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]
                final_file.write(generated_text[0] + '\n')
                final_text += generated_text[0] + '\n'
                
    except:
        print("Empty document")
            
    return final_text;


# In[6]:


start = time.time()
a = summary_generation("13-article-4375061-acutus-medical-inc-afib-ceo-vince-burgess-on-q2-2020-results-earnings-call-transcript.txt", 'pegasus')
#b = summary_generation("ab.txt", 'bart')
end = time.time()

print((end-start)/60)


# In[7]:


start = time.time()
directory = 'files'

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    
    if os.path.isfile(f):
        a = summary_generation(filename, 'pegasus')
        print("Summary generated for", filename)
end = time.time()

print("Taken for generating summaries by pegasus model", round((end-start)//60, 2), 'minutes')


# In[8]:


start = time.time()
directory = 'files'

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    
    if os.path.isfile(f):
        a = summary_generation(filename, 'bart')
        print("Summary generated for", filename)
end = time.time()

print("Taken for generating summaries by bart model", round((end-start)//60, 2), 'minutes')
