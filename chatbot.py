import nltk
import random
import string
import numpy as np
import mysql.connector
import pandas as pd
import time
import datetime
import csv
import smtplib, ssl
import re

# các thư viện hỗ trợ NL ( Natural Language)
import speech_recognition as sr
from nltk.chat.util import Chat, reflections
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from selenium import webdriver
from selenium.webdriver.common.by import By

nltk.download('punkt')
nltk.download('stopwords')

now = datetime.datetime.now()

# danh sách các tiện ích
media_list = [
    'facebook',
    'gmail',
    'instagram',
    'google',
    'telegram',''
    'github',
    'canva',
    'drive.google',
    'chatgpt',
    'deepseek',
    'stackoverflow',
    'youtube',
    'shoppee',
    'lazada',
    'booking',
    'gemini',
    'X',
    'tiktok'
]



conn = mysql.connector.connect(
    host = '127.0.0.1',
    username = 'root',
    password = 'Minh_17102004',
    database = 'taza'
)
cursor = conn.cursor()


def pending_revenue():
    cursor.execute('''SELECT sum(total_price/25000) 
                             FROM orders''')
    revenue = cursor.fetchone()[0]
    return f'Revenue in Pending - $ {round(revenue,2)}'

def customers():
    cursor.execute('''
    SELECT COUNT(user_id) FROM user
    ''')
    customer = cursor.fetchone()[0]
    return f'Total customers - {customer}'

def orders():
    cursor.execute('SELECT COUNT(*) FROM orders')
    orders = cursor.fetchone()[0]
    return f'Total orders - {orders}'

def stock():
    cursor.execute('SELECT SUM(stock) FROM product')
    stock = cursor.fetchone()[0]
    return f'Stock - {stock}'

def report():
    try:
        print("Machine Spirit: Here is your report")
        print('-'*40)
        print(customers())
        print(orders())
        print(stock())
        print(pending_revenue())
        print('-'*40)
        print("Do you want to convert all of this into a Document ?")
    except Exception :
        print("Machine Spirit: Sorry, you didn't connect to database yet, please check your database connection if you have")

def login_email():
    try:
        print("Machine Spirit: provide your email to continue")
        email = input("Enter Text: ")
        print("Machine Spririt: Gmail address confirmed, now send me your password")
        password = input("Enter Text: ")
        # Email set up 
        port = 445
        smtp_server = "smtp.gmail.com"
        context = ssl.create_default_context()
        server  = smtplib.SMTP(smtp_server,port=port)
        server.ehlo()
        server.starttls(context=context)
        server.login(email,password)    
        sending_email_message(email=email,password=password)
        
    except Exception:
        print("Machine Spirit: Sorry, SMTP server is overrided ... ")

def sending_email_message(email,password):
    port = 445
    smtp_server = "smtp.gmail.com"
    context = ssl.create_default_context()
    server  = smtplib.SMTP(smtp_server,port=port)
    server.ehlo()
    server.starttls(context=context)
    server.login(email,password)
    print("Machine Spirit: Now write down your address that you need to send")
    address = input("Enter Address: ")
    matched = re.search(r"@gmail.com",address)
    if matched:
        print("Machine Spirit: Now send to them your context below")
        message = input("Context: ")
        print("Machine Spirit: Context is pending, please wait")
        time.sleep(5)
        try:
            with smtplib.SMTP_SSL(smtp_server,port=port,context=context) as server:
                server.sendmail(email, address, message)
            print("Machine Spirit: Sending completed !!!")
        except Exception:
            print("Machine Spirit: Sorry, SMTP services are looking for problem")
    else:
        print("Machine Spirit: Sorry, your address is uncacceptable") 



def ytb_search(object):
    print('Machine Spirit: Please wait, result is pending ...')
    driver = webdriver.Chrome()
    url = f'https://www.youtube.com/results?search_query={object}'
    driver.get(url=url)
    print('Machine Spirit: Here you are, do enjoy it')

def gg_search(object):
    print('Machine Spirit: Please wait, result is pending ...')
    driver = webdriver.Chrome()
    url = f'https://www.google.com/search?q={object}'
    driver.get(url=url)
    print('Machine Spirit: Here you are, do enjoy it')

def media(): 
    driver = webdriver.Chrome()
    https = 'https://www.'
    driver.get(https+'youtube.com')

def content(obj):
    driver = webdriver.Chrome()
    https = 'https://www.'
    driver.get(https+f'{obj}.com')

def result_search(object):
    try:
        driver = webdriver.Chrome()
        url = f'https://vi.wikipedia.org/wiki/{object}'
        driver.get(url=url)
        driver.implicitly_wait(3)
        textline = driver.find_element(By.XPATH, '//p').text
        print(textline)
    except Exception:
        print(" Machine Spirit: Sorry, I Didn't find any matched results")

template = [
    (r"(hi|hello|hey)", ["Hello!", "Hi there!", "Hey! How can I help you?"]),
    (r"how are you", ["I'm good, thanks for asking!", "I'm a bot, but I'm doing great!"]),
    (r"who are you", ["I'm a Machine Spirit!, alway be your supervisor", "Machine Spirit in your service, My Minister"]),
    (r"bye|goodbye", ["Goodbye!", "See you later!", "Have a great day!"]),
    (r"youtube|open youtube|i want youtube|start youtbe",  ["Understood, Please wait"]),
    (r"thanks|thank u|Thank u|thank you|Thanks", ["yeah, no problem",'Yeah, I appreciate it','You welcome']),
    # (f"help me open {target}",f" i want open {target}",f" can you open {target} ?", ['Acknowledge, content detected, sharing bless to Omnissiah'])
    (r"(.*) your (.*)", ["Why do you ask about my %2?", "Do you want to know more about my %2?"]),
    (r"(.*)", ["Hold on"]),
]

leave = ['bye','goodbye','exit','see ya !']
business = ['revenue','income','pending','total','report','reports']
accepted = ['accept','Accepted','Yeah','yeah','Yes','ya','yes','course','sure']
message = ['message','sending','send','Send','Sending','mail','Mail']


chatbot = Chat(template, reflections=reflections)




def chat():
    print("Hello ! type 'bye' or 'exit' to leave.")
    while True:
        user = input('Enter Text: ')
        if user in leave:
            print("Well Maybe we Can talk for the next time, See you !!!")
            break
        else:
            replies = chatbot.respond(user)
            print(f'Machine Spirit: {replies}')
            if 'Understood, Please wait' in replies:
                time.sleep(5)
                media()
             
            for text in range(len(user.split(" "))):
                
                if user.split(' ')[text] in media_list:
                    print(f'Machine Spirit: Utitlity recieved, {user.split(" ")[text]}')
                    print('Machine Spririt: Acknowledged, Please wait')
                    time.sleep(5)
                    content(user.split(" ")[text])
                if user.split(' ')[text] == "time":
                    print(f"Machine Spirit: It's {now}")
                if user.split(' ')[text] in business:
                    print(f'{report()}')
                if user.split(' ')[text] in ['video','Video','clip','short','music']:
                    print('Machine Spirit: Which one you want to watch ?')
                    result = input('Enter Text: ')
                    if result is None:
                        print('Machine Spirit: Sorry, You need to provide your information ')
                    else:
                        ytb_search(result)
                        
                if user.split(' ')[text] in ['search','Search','find','show','help','detect']:
                    print('Machine Spirit: what do you want to see ?')
                    result = input('Enter Text: ')
                    if result is None:
                        print('Machine Spirit: Sorry, You need to provide your information ')
                    else:
                        gg_search(result)
                
                if user.split(' ')[text] in ['what','What','Tell','tell','more','need','support','?']:
                    print('Machine Spirit: Yeah, Give me a specified detail for this')
                    result = input('Enter Text: ')
                    if result is None:
                        print('Machine Spirit: Sorry, You need to provide your information ')
                    else:
                        result_search(result)
                        # print("Machine Spirit: Do you want to store this information ?")
                        # choice = input("Enter Text: ")
                        # if choice in accepted:
                        #     print("Machine Spirit: Data is in pending, Please wait ...")
                        # else:
                        #     print("Machine Spirit: Okay, If you have any question, please write down and I will help you solve it clearly")

                if user.split(' ')[text] in message:
                    login_email()


if __name__ == "__main__":
    chat()