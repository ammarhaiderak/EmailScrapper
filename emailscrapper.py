

"""# **Run the Code Here**

Run the cell below and restart the runtime
"""

import logging
import os
import pandas as pd
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
logging.getLogger('scrapy').propagate = False

def get_urls():
    filename=input('Enter the links file name e.g "links.csv": ')
    df = pd.read_csv(filename)
    urls=df['WEBSITE'].to_list()
    print(urls)
    return urls


def ask_user(question):
    response = input(question + ' y/n' + '\n')
    if str(response) == 'y':
        return True
    else:
        return False

def create_file(path):
    response = False
    if os.path.exists(path):
        response = ask_user('File already exists, replace?')
        if response == False: return 
    
    with open(path, 'wb') as file: 
        file.close()


ext='\w+'


class MailSpider(scrapy.Spider):
    
    name = 'email'
    global ext


    def parse(self, response):
        links = LxmlLinkExtractor(allow=()).extract_links(response)
        links = [str(link.url) for link in links]
        links.append(str(response.url))

        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_link) 
            
    def parse_link(self, response):
        
        for word in self.reject:
            if word in str(response.url):
                return

        html_text = str(response.text)
        EMAIL_REGEX = r"""\w+@\w+\.{1}(?!png|jpg|JPG|PNG|JPEG|jpeg)\w+"""
        mail_list = re.findall(EMAIL_REGEX, html_text)
        if len(mail_list)>0:
            print(mail_list)

        dic = {'email': mail_list, 'link': str(response.url)}
        df = pd.DataFrame(dic)
        
        df.to_csv(self.path, mode='a', header=False)
        df.to_csv(self.path, mode='a', header=False)


def get_info(ext, n, language, path, reject=[]):
    
    create_file(path)
    df = pd.DataFrame(columns=['email', 'link'], index=[0])
    df.to_csv(path, mode='w', header=True)
    
    print('Collecting urls...')
    _urls = get_urls()
    
    print('Searching for emails...')
    process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0'})
    process.crawl(MailSpider, start_urls=_urls, path=path, reject=reject)
    process.start()
    
    print('Cleaning emails...')
    df = pd.read_csv(path, index_col=0)
    df.columns = ['email', 'link']
    df = df.drop_duplicates(subset='email')
    df = df.reset_index(drop=True)
    df.to_csv(path, mode='w', header=True)
    
    return df



bad_words = ['facebook', 'instagram', 'youtube', 'twitter', 'wiki', 'paypal']

df = get_info('.com', 300, 'en', 'emailfile.csv', bad_words)
