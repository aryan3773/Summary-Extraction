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

#nltk.download('punkt')
#nltk.download('stopwords')


# In[2]:


pegasus_tokenizer = PegasusTokenizer.from_pretrained("human-centered-summarization/financial-summarization-pegasus")
pegasus_model = PegasusForConditionalGeneration.from_pretrained("human-centered-summarization/financial-summarization-pegasus")


# In[3]:


def nest_sentences(document):
    nested = []
    sent = []
    length = 0
    for sentence in nltk.sent_tokenize(document):
        length += len(sentence)
        if length < 1024:
            sent.append(sentence)
            
        else:
            nested.append(sent)
            sent = []
            length = 0
            
    if sent:
        nested.append(sent)

    return nested


# In[4]:


def generate_summary(nested_sentences):
    summaries = []
    
    for nested in nested_sentences:
        input_tokenized = pegasus_tokenizer.encode(' '.join(nested), truncation=True, return_tensors='pt', max_length=512)
        summary_ids = pegasus_model.generate(input_tokenized, length_penalty=3.0, num_beams=5)
        
        output = [pegasus_tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]
        summaries.append(output)
        
    summaries = [sentence for sublist in summaries for sentence in sublist]
    return summaries


# In[5]:


# Functions for generating a summary for a given text file consisting of multiple paragraphs
def summary_generation(text_file):
    file = open(text_file, encoding="utf8")
    paragraphs = file.read().split('\n')
    final_text = ""
    
    try:
        s = 0
        final_file = open(text_file[:-4] + "_pegasus_new" + ".txt", "w")

        for para in paragraphs:
            nested = nest_sentences(para)
            #print("Original piece of text")
            #print(para)
            #print('*'*30 + '\n')

            summ = generate_summary(nested)
            temp = " ".join(summ)
            final_text += temp + '\n'
            #print("Generated summary")
            #print(temp)
            #print('#'*30 + '\n')
            
        final_file.write(final_text + '\n')

    except:
        print("Error")
            
    return final_text;


# In[35]:


# Testing on a sample 
a = summary_generation("19-article-4374996-metlife-inc-met-metlife-acquisition-of-versant-health-conference-call-transcript.txt")
print(a)


# In[ ]:


start = time.time()
directory = 'files'

num = 1
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    
    if os.path.isfile(f):
        a = summary_generation(filename)
        print("Summary generated for", filename, '->', num)
        num += 1;
        
end = time.time()

print("Taken for generating summaries by customized pegasus model", round((end-start)//60, 2), 'minutes')
