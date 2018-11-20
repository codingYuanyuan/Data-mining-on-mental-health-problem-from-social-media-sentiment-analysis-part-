import factories
import random
import uuid
from expects import expect, equal
from expects.matchers.built_in import be_above
from expects.matchers.built_in.have_keys import have_key
from datetime import datetime
import pytest
from requests import *
import json
import conftest


import requests
import json
import nltk
from nltk import word_tokenize
import re
from textblob import TextBlob
from textblob import Word
from os.path import isfile, join
import string
import io
import math, re, string, requests, json
import numpy as np

#nltk.download()
#download all packages


import os
import fnmatch,re
import jsonpickle

from pprint import pprint
import numpy as np

all_files = os.listdir("/directorytotweetsdata/UserTweets")
message = []
ID = []


#
class DataPreprocess():
    def __init__(self,text):
        self.text = text
           
    def Preprocess(self):
        # get rid of url
        self.text = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', self.text)

        # get rid of @user and hashtags
        self.text= self.text.split()
        temp = []
        for i in range(len(self.text)):
            if self.text[i][0] != '@' and self.text[i][0] != '#' and self.text[i][0] != "R":
                temp += [self.text[i]]
        self.text = temp

   
        #tokenize data and change them all to lower case
        sub_all = []
        for i in range(len(self.text)):
            if self.text[i][0] == "'":
                self.text[i-1] = self.text[i-1].join(self.text[i])
            tokens = word_tokenize(self.text[i].lower())
            tokens = [word.split("/") for word in tokens]
            tokens = ["".join(word) for lists in tokens for word in lists]
            tokens = [word for word in tokens if len(word)>0]
            sub_all += tokens
        self.text = sub_all


        #remove punctuations
        for i in range(len(self.text)):
            self.text[i] = "".join(c for c in self.text[i] if c not in string.punctuation)
        self.text = [s for s in self.text if s]

                
    def singularize(self):
        """
        convert the plurals to singulars and the verbs to the first person present.
        """
        temp = [TextBlob(word) for word in self.text]
        self.text = [list(word.words.singularize())[0] for word in temp]
        tempv = [Word(word) for word in self.text]
        self.text = [word.lemmatize("v") for word in tempv]
        
    def get_text(self):
        return self.text




class ANEW:

    def __init__(self,text):
        with io.open("ANEW2010ALL.txt","r",encoding = "utf-8") as f:
            self.anewlexicon = f.read()
        self.text = text
        self.dom = 0
        self.act = 0
        self.anewlex_dict = {}

       
    def make_anewlex_dict(self):
        """
        Convert depressed lexicon file to a dictionary
        """
        self.anewlexicon = self.anewlexicon.split("\n")
        self.anewlexicon = self.anewlexicon[1:]
        for line in self.anewlexicon:
            (Word,Wdnum,ValMn,ValSD,AroMn,AroSD,DomMn,DomSD) = line.split()
            if Word not in self.anewlex_dict:
                self.anewlex_dict[Word] = [("AroMn",AroMn),("DomMn",DomMn)]
            else:
                self.anewlex_dict[Word] = [("AroMn",AroMn),("DomMn",DomMn)]



    def get_act_dom_score(self):
        return self.score

    def set_textanduser(self):
        """
        set tokenized text from the jsonfile and get user list
        also get the combinedic
        """

        text = DataPreprocess(self.text)
        text.Preprocess()
        text.singularize()
        self.text = text.get_text()

    def grade_act_dom_score(self):
        """
        calculating the dominance score and the activation score
        """
        n = 0
        domscore = 0
        actscore = 0
        for word in self.text:
            if word in self.anewlex_dict:
                n+=1
                domscore += float(self.anewlex_dict[word][1][1])
                actscore += float(self.anewlex_dict[word][0][1])
        if n !=0:
            domscore = float(domscore/n)
            actscore = float(actscore/n)
        self.dom = domscore
        self.act = actscore
    def get_score(self):
        print(self.dom,self.act)
        return self.dom, self.act


                        
def get_act_dom_score(tweet):
    a = ANEW(tweet)
    a.make_anewlex_dict()
    a.set_textanduser()
    a.grade_act_dom_score()
    dom, act = a.get_score()
    return dom, act

#

def get_content_data(content,**kwargs):
    attribs = {
        "language_content": content,
        "content_source": random.randint(1, 2),
        "content_handle": uuid.uuid4().hex,
        "content_date": datetime.now().isoformat(),
        "recipient_id": None,
        "content_tags": ['tag1', 'tag2', 'tag3'],
        'language': 'english'
        }
    attribs.update(kwargs)
    return attribs


def get_person_data(content=None):
    person_data = {'name': "John {0} Doe".format(uuid.uuid4().hex), 'person_handle': uuid.uuid4().hex, 'gender': 1}
    if content:
        person_data["content"] = content
    return person_data

def test_create_person_with_content(baseurl, apikey, apisecret,content):
    content_data = get_content_data(content)
    person_data = get_person_data(content_data)
    


    person_api_url = conftest.person_api_url(baseurl)

    auth_headers = conftest.auth_headers(apikey, apisecret)
    

    response = post(person_api_url, json=person_data, headers=auth_headers)
    #help(post(person_api_url, json=person_data, headers=auth_headers))
    

    response_json = json.loads(response.content)
 #   pprint(response_json)
    
 
    expect(response.status_code).to(equal(200))
    expect(response_json["name"]).to(equal(person_data["name"]))
    expect(response_json["contents"][0]).to(have_key("receptiviti_scores"))
    expect(response_json["contents"][0]).to(have_key("liwc_scores"))
    return response_json["contents"][0]["liwc_scores"]['categories']

def liwc(tweet):
    a = test_create_person_with_content("https://app.receptiviti.com","5acff76987cb890520e58c8b", "Zn5YUze5Ilolara0NGGyNkBi68QzAYqc4fEORRHf41A",tweet)
    
    return(a["article"],a["auxverb"],a["conj"],a["adverb"],a["i"],a["we"],a["you"],a["they"],a["prep"],a["function"],a["assent"],a["negate"],a["certain"],a["quant"],a["negemo"],a["posemo"])




#


for i in range(len(all_files)):
    if all_files[i][-4:-1]==".tx":
        tempname = all_files[i]
        ID += [tempname]
        f = open("/directorytotweetsdata/UserTweets/"+all_files[i],encoding = 'utf-8')
        message+= [f.read()]
        f.close()


lingus = []
#print(ID)

for i in range(len(message)):
#    print(i)
    templingus = []
    act = get_act_dom_score(message[i])
    templingus += act
    new = liwc(message[i])
    templingus +=new    

    lingus +=[templingus]

dicti = {}
for i in range(len(ID)):
    dicti[ID[i]] = lingus[i]

outfile = open("output","a")
outfile.write(jsonpickle.encode(dicti))
outfile.close()
