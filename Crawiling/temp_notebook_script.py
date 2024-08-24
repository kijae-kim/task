#!/usr/bin/env python
# coding: utf-8

# In[27]:


import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import certifi
import re
import pandas as pd


# In[37]:


class Yes24:
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=self.options)

    def scroll_down(self, times=20):
        for i in range(times):
            self.driver.execute_script(f'window.scrollTo(0, document.body.scrollHeight / {times} * {i})')
            time.sleep(0.1)

    def search(self, word):
        book_list = []

        for page in range(1, 6):  # 1페이지부터 5페이지까지 크롤링
            url = f'https://www.yes24.com/Product/Search?domain=ALL&query={word}&page={page}'
            self.driver.get(url)
            self.driver.implicitly_wait(2)

            self.scroll_down(20)

            xpath = '/html/body/div[1]/div[4]/div/div[2]/section[2]/div[3]/ul'
            title_list = self.driver.find_element(By.XPATH, xpath)
            book_tags = title_list.find_elements(By.CLASS_NAME, 'itemUnit')

            for book in book_tags:
                book_img = book.find_element(By.TAG_NAME, 'img')
                url = book_img.get_attribute('src')
                title = book_img.get_attribute('alt')
                price = book.find_element(By.CLASS_NAME, 'yes_b').text
                author = book.find_element(By.CLASS_NAME, 'info_auth').text
                publisher = book.find_element(By.CLASS_NAME, 'info_pub').text
                info_date = book.find_element(By.CLASS_NAME, 'info_date').text
                goods_no = re.search(r'goods/(\d+)', url).group(1)
                book_list.append({
                    '책제목': title,
                    '가격': price,
                    '저자': author,
                    '출판사': publisher,
                    '출판일': info_date,
                    '이미지로컬경로': url,
                    '판매사이트': f'https://www.yes24.com/Product/Goods/{goods_no}'
                })

        return book_list

    def close(self):
        self.driver.quit()


# In[35]:


# 사용자 입력 받기
search_word = input("검색어를 입력하세요: ")

# 크롤링 실행
yes24_crawler = Yes24(headless=False)  # headless=False로 설정하여 브라우저가 표시되도록 함
books = yes24_crawler.search(search_word)
yes24_crawler.close()


# In[185]:


#mongoDB에 저장
def yes24_to_mongodb(data, db_name='aiproject', collection_name='yes24'):
    ca = certifi.where()
    client = MongoClient(
        'mongodb+srv://99hakssun:OTSCipcH7d2F2Ney@99hakssun.frdhloo.mongodb.net/?retryWrites=true&w=majority&appName=99hakssun',
        tlsCAFile=ca)
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_many(data)


# In[187]:


if books:
    yes24_to_mongodb(books)
    print('Save')
else:
    print('Fail')


# In[195]:


# 검색된 도서 정보를 DataFrame으로 변환
yes24_books_df = pd.DataFrame(books)

yes24_books_df


# In[112]:


class Kyobo:
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=self.options)

    def scroll_down(self, times=20):
        for i in range(times):
            self.driver.execute_script(f'window.scrollTo(0, document.body.scrollHeight / {times} * {i})')
            time.sleep(0.1)

    def search(self, word):
        book_list = []

        for page in range(1, 6):  # 1페이지부터 5페이지까지 크롤링
            url = f'https://search.kyobobook.co.kr/search?keyword={word}&target=total&gbCode=TOT&page={page}'
            self.driver.get(url)
            self.driver.implicitly_wait(2)

            self.scroll_down(20)

            xpath = '/html/body/div[3]/main/section/div/div/div[4]/div[2]/div/div[2]/div[3]/ul'
            title_list = self.driver.find_element(By.XPATH, xpath)
            book_tags = title_list.find_elements(By.CLASS_NAME, 'prod_item')

            for book in book_tags:
                book_img = book.find_element(By.CLASS_NAME, 'prod_img_load')
                url = book_img.get_attribute('src')
                title = book_img.get_attribute('alt')
                price = book.find_element(By.CLASS_NAME, 'price').text
                author = book.find_element(By.CLASS_NAME, 'author.rep').text
                publisher = book.find_element(By.CLASS_NAME, 'prod_publish').text
                info_date = book.find_element(By.CLASS_NAME, 'date').text
                prod_link = book.find_element(By.CLASS_NAME, 'prod_link')
                site = prod_link.get_attribute('href')
            
                book_list.append({
                    '책제목': title,
                    '가격': price,
                    '저자': author +' 외',
                    '출판사': publisher.split('\n')[0],
                    '출판일': info_date,
                    '이미지로컬경로': url,
                    '판매사이트': site
                })

        return book_list

    def close(self):
        self.driver.quit()


# In[183]:


# 사용자 입력 받기
search_word = input("검색어를 입력하세요: ")

# 크롤링 실행
kyobo_crawler = Kyobo(headless=False)  # headless=False로 설정하여 브라우저가 표시되도록 함
kyobo_books = kyobo_crawler.search(search_word)
kyobo_crawler.close()


# In[188]:


#mongoDB에 저장
def kyobo_to_mongodb(data, db_name='aiproject', collection_name='kyobo'):
    ca = certifi.where()
    client = MongoClient(
        'mongodb+srv://99hakssun:OTSCipcH7d2F2Ney@99hakssun.frdhloo.mongodb.net/?retryWrites=true&w=majority&appName=99hakssun',
        tlsCAFile=ca)
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_many(data)


# In[189]:


if kyobo_books:
    kyobo_to_mongodb(kyobo_books)
    print('Save')
else:
    print('Fail')


# In[194]:


# 검색된 도서 정보를 DataFrame으로 변환
kyobo_books_df = pd.DataFrame(kyobo_books)

kyobo_books_df


# In[180]:


# 알라딘
class Aladin:
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=self.options)

    def scroll_down(self, times=20):
        for i in range(times):
            self.driver.execute_script(f'window.scrollTo(0, document.body.scrollHeight / {times} * {i})')
            time.sleep(0.1)

    def search(self, word):
        book_list = []

        for page in range(1, 6):  # 1페이지부터 5페이지까지 크롤링
            url = f'https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=Book&KeyWord={word}&KeyRecentPublish=0&OutStock=0&ViewType=Detail&SortOrder=11&CustReviewCount=0&CustReviewRank=0&KeyFullWord=%ED%8C%8C%EC%9D%B4%EC%8D%AC&KeyLastWord=%ED%8C%8C%EC%9D%B4%EC%8D%AC&CategorySearch=&chkKeyTitle=&chkKeyAuthor=&chkKeyPublisher=&chkKeyISBN=&chkKeyTag=&chkKeyTOC=&chkKeySubject=&ViewRowCount=25&SuggestKeyWord=&page={page}'
            self.driver.get(url)
            self.driver.implicitly_wait(2)

            self.scroll_down(20)

            xpath = '/html/body/div[3]/table/tbody/tr/td[3]/form/div[2]'
            title_list = self.driver.find_element(By.XPATH, xpath)
            book_tags = title_list.find_elements(By.CLASS_NAME, 'ss_book_box')

            for book in book_tags:
                book_img = book.find_element(By.CLASS_NAME, 'front_cover')
                url = book_img.get_attribute('src')
                title = book.find_element(By.CLASS_NAME, 'bo3')
                price = book.find_element(By.CLASS_NAME, 'ss_p2').text
                li_tag = book.find_element(By.CLASS_NAME, 'ss_book_list').text.split('\n')
                
                if len(li_tag) > 2:
                    author = li_tag[2]
                    author_parts = author.split('|')
                    if len(author_parts) < 3 and len(li_tag) > 1:
                        author = li_tag[1]
                        author_parts = author.split('|')
                elif len(li_tag) > 1:
                    author = li_tag[1]
                    author_parts = author.split('|')
                else:
                    author = ''
                    author_parts = []
                publisher = author_parts[1] if len(author_parts) > 1 else '정보 없음'
                info_date = author_parts[2] if len(author_parts) > 2 else '정보 없음'
                site = title.get_attribute('href')
                book_list.append({
                    '책제목': title.text,
                    '가격': price,
                    # 'check' : li_tag,
                    '저자': author_parts[0].strip() if len(author_parts) > 0 else '정보 없음',
                    '출판사': publisher.strip(),
                    '출판일': info_date.strip(),
                    '이미지로컬경로': url,
                    '판매사이트': site
                })


        return book_list

    def close(self):
        self.driver.quit()


# In[181]:


# 사용자 입력 받기
search_word = input("검색어를 입력하세요: ")

# 크롤링 실행
aladin_crawler = Aladin(headless=False)  # headless=False로 설정하여 브라우저가 표시되도록 함
aladin_books = aladin_crawler.search(search_word)
aladin_crawler.close()


# In[191]:


#mongoDB에 저장
def aladin_to_mongodb(data, db_name='aiproject', collection_name='aladin'):
    ca = certifi.where()
    client = MongoClient(
        'mongodb+srv://99hakssun:OTSCipcH7d2F2Ney@99hakssun.frdhloo.mongodb.net/?retryWrites=true&w=majority&appName=99hakssun',
        tlsCAFile=ca)
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_many(data)


# In[192]:


if aladin_books:
    aladin_to_mongodb(aladin_books)
    print('Save')
else:
    print('Fail')


# In[193]:


# 검색된 도서 정보를 DataFrame으로 변환
aladin_books_df = pd.DataFrame(aladin_books)

aladin_books_df


# In[204]:


get_ipython().system('pip install Workbook')


# In[220]:


pip install openpyxl
pip install os


# In[216]:


import pandas as pd
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.utils.dataframe import dataframe_to_rows
import nbformat
from nbconvert import PythonExporter


# In[219]:


import nbformat
from nbconvert import PythonExporter
import os

# Load the notebook
file_path = '/Users/gimgijae/Desktop/KDT/CrawlingTest/CrawlingTest/test.ipynb'
with open(file_path) as f:
    nb = nbformat.read(f, as_version=4)

# Convert the notebook to a Python script
python_exporter = PythonExporter()
python_script, _ = python_exporter.from_notebook_node(nb)

# Save the script to a temporary file
script_path = '/Users/gimgijae/Desktop/KDT/CrawlingTest/CrawlingTest/temp_notebook_script.py'
with open(script_path, 'w') as f:
    f.write(python_script)

# Execute the script and extract dataframes
exec_context = {}
exec(open(script_path).read(), exec_context)

# Extract dataframes
yes24_books_df = exec_context.get('yes24_books_df')
kyobo_books_df = exec_context.get('kyobo_books_df')
aladin_books_df = exec_context.get('aladin_books_df')

# Clean up the temporary script
os.remove(script_path)


# In[38]:


#몽고디비 저장


# In[39]:


#엑셀파일 저장


# In[213]:


yes24_books_df


# In[ ]:




