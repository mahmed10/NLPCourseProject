

import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import os
os.chdir("C:\\Users\\argho\\Pictures\\NLP\\NLPCourseProject-master\\")
#https://bit.ly/2NyxdAG
from bs4 import BeautifulSoup
import requests
from lxml import html
import re

from googlesearch import search

from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
intents = json.loads(open('moviedataset.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


def clean_up_sentence(sentence):
	sentence_words = nltk.word_tokenize(sentence)
	sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
	return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
	# tokenize the pattern
	sentence_words = clean_up_sentence(sentence)
	# bag of words - matrix of N words, vocabulary matrix
	bag = [0]*len(words)
	for s in sentence_words:
		for i,w in enumerate(words):
			if w == s:
				# assign 1 if current word is in the vocabulary position
				bag[i] = 1
				if show_details:
					print ("found in bag: %s" % w)
	return(np.array(bag))

def predict_class(sentence, model):
	# filter out predictions below a threshold
	p = bow(sentence, words,show_details=False)
	res = model.predict(np.array([p]))[0]
	ERROR_THRESHOLD = 0.25
	results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
	# sort by strength of probability
	results.sort(key=lambda x: x[1], reverse=True)
	return_list = []
	for r in results:
		return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
	return return_list

def getResponse(ints, intents_json):
	tag = ints[0]['intent']
	list_of_intents = intents_json['intents']
	for i in list_of_intents:
		if(i['tag']== tag):
			result = random.choice(i['responses'])
			context = i['context']
			tag = i['tag']
			break
	return result, context, tag

def chatbot_response(msg):
	ints = predict_class(msg, model)
	res, con, tag = getResponse(ints, intents)
	return res, con, tag


def getMovieDetails(url):
    data = {}
    r = requests.get(url=url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')

    #page title
    title = soup.find('title')
    data["title"] = title.string

    # rating
    ratingValue = soup.find("span", {"itemprop" : "ratingValue"})
    data["ratingValue"] = ratingValue.string

    # no of rating given
    ratingCount = soup.find("span", {"itemprop" : "ratingCount"})
    data["ratingCount"] = ratingCount.string

    # name
    titleName = soup.find("div",{'class':'titleBar'}).find("h1")
    data["name"] = titleName.contents[0].replace(u'\xa0', u'')

    # additional details
    subtext = soup.find("div",{'class':'subtext'})
    data["subtext"] = ""
    for i in subtext.contents:
        data["subtext"] += i.string.strip()

    # summary
    summary_text = soup.find("div",{'class':'summary_text'})
    data["summary_text"] = summary_text.string.strip()

    credit_summary_item = soup.find_all("div",{'class':'credit_summary_item'})
    data["credits"] = {}
    for i in credit_summary_item:
        item = i.find("h4")
        names = i.find_all("a")
        data["credits"][item.string] = []
        for i in names:
            data["credits"][item.string].append({
                "link": i["href"],
                "name": i.string
            })
    return data

#Creating GUI with tkinter
import tkinter
from tkinter import *


def send():
	msg = EntryBox.get("1.0",'end-1c').strip()
	EntryBox.delete("0.0",END)

	if msg != '':
		ChatLog.config(state=NORMAL)
		ChatLog.insert(END, "You: " + msg + '\n\n')
		ChatLog.config(foreground="#442265", font=("Verdana", 12 ))

		res, con, tag = chatbot_response(msg)
		if con[0] == 'googlesearch_movie':
			ChatLog.insert(END, "Bot: " + res)
			query = msg + "imdb"
			serach_result = next(iter(search(query,num_results=1)))
			if(serach_result[:20] == "https://www.imdb.com"):
				details = getMovieDetails(serach_result)
				ChatLog.insert(END, "Rating of the movie \"" + details['title'].split('-')[0] + "\" (out of 10) is " + details[tag]+ '\n\n')
			else:
				ChatLog.insert(END, "Not found"+ '\n\n')


		elif con[0] == 'googlesearch_dir':
			ChatLog.insert(END, "Bot: " + res)
			query = msg + " imdb"
			serach_result = next(iter(search(query,num_results=1)))
			if(serach_result[:20] == "https://www.imdb.com"):
				details = getMovieDetails(serach_result)
				ChatLog.insert(END, "Director of the movie is \"" + details["credits"]["Director:"][0]["name"] + '\n\n')
			else:
				ChatLog.insert(END, "Not found"+ '\n\n')


		# else:
		# 	ChatLog.insert(END, "Bot: " + res + '\n\n')

		elif con[0] == 'googlesearch_summary':
			ChatLog.insert(END, "Bot: " + res)
			query = msg + " imdb"
			serach_result = next(iter(search(query,num_results=1)))
			if(serach_result[:20] == "https://www.imdb.com"):
				details = getMovieDetails(serach_result)
				ChatLog.insert(END, "Main Plot: \"" + details["summary_text"] + '\n\n')
			else:
				ChatLog.insert(END, "Not found"+ '\n\n')


		else:
			ChatLog.insert(END, "Bot: " + res + '\n\n')	


		ChatLog.config(state=DISABLED)
		ChatLog.yview(END)




base = Tk()
base.title("iBOT")
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)

#Create Chat window
ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)

ChatLog.config(state=DISABLED)

#Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

#Create Button to send message
SendButton = Button(base, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
	bd=0, bg="#32de97", activebackground="#3c9d9b",fg='#ffffff',
	command= send )

#Create the box to enter message
EntryBox = Text(base, bd=0, bg="white",width="29", height="5", font="Arial")
#EntryBox.bind("<Return>", send)


#Place all components on the screen
scrollbar.place(x=376,y=6, height=386)
ChatLog.place(x=6,y=6, height=386, width=370)
EntryBox.place(x=128, y=401, height=90, width=265)
SendButton.place(x=6, y=401, height=90)

base.mainloop()

