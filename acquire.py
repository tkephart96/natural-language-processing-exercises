"""
Acquire data by webscraping

Functions:
- get_header
- get_blog_articles
- get_all_blog_articles
- get_shorts
"""

##### IMPORTS #####

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from pprint import pprint
from requests import get
import requests
import random
import os

##### FUNCTIONS #####

def get_header():
    """
    The function returns a randomly selected user agent header for web scraping purposes.
    :return: a dictionary with a single key-value pair, where the key is 'User-Agent' and the value is a
    randomly chosen user agent string from a list of user agents.
    """
    # random list
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Chrome/91.0.4472.124",
        "Mozilla/4.5 (compatible; HTTrack 3.0x; Windows 98)"
        ]
    # pick random
    random_user_agent = random.choice(user_agents)
    return {'User-Agent': random_user_agent}

def get_blog_articles(blogs_list=None,from_cache=True):
    """
    This function retrieves Codeup blog articles either from a cached CSV file or by scraping the
    website, and returns a pandas DataFrame containing the article titles and content.
    
    :param blogs_list: A list of URLs for Codeup blog articles. If not provided, the function will
    scrape the Codeup blog page to generate this list
    :param from_cache: A boolean parameter that determines whether to read the data from a cached CSV
    file or to scrape the data from the website, defaults to True (optional)
    :return: The function `get_blog_articles` returns a pandas DataFrame containing the title and
    content of blog articles from the Codeup website. If `from_cache` is set to `True`, it returns the
    cached DataFrame from a CSV file. If `from_cache` is `False` or there is no cached data, it scrapes
    the website for the blog articles and returns a new DataFrame.
    """
    filename = 'codeup_blogs.csv'
    if from_cache == True:
        return pd.read_csv(filename)
    else:
        # if you dont have a url list for codeup blogs
        if blogs_list is None:
            # get page
            blog_page = requests.get('https://codeup.com/blog/',headers=get_header())
            # soup it
            blog_soup = BeautifulSoup(blog_page.content, 'html.parser')
            # list of urls for blogs
            blogs_list = [
                element["href"]
                for element in blog_soup.find_all('a', class_='more-link')
                ]
        # empty list for appending
        blogs = []
        # go thru each url
        for url in blogs_list:
            # get the web page
            response = requests.get(url,headers=get_header())
            # make a soup from it
            soup = BeautifulSoup(response.content,'html.parser')
            # get content div
            soup_div = soup.find_all('div',class_='entry-content')
            # soup it as well for now
            soups = BeautifulSoup(f'{soup_div[0]}','html.parser')
            # make blank content and join all paragraphs
            content = ''.join(element.text for element in soups.find_all('p'))
            # make blog into dict
            blog = {
                'title':soup.title.text,
                'content':content
                }
            # append to list of blogs
            blogs.append(blog)
            # make df from dict
            blogs_df = pd.DataFrame(blogs)
            # cache data locally
            blogs_df.to_csv(filename, index=False)
        return blogs_df

def get_all_blog_articles(from_cache=True):
    """
    This function scrapes all blog articles from the Codeup website and returns them as a pandas
    dataframe, with the option to cache the data locally.
    
    :param from_cache: A boolean parameter that determines whether to read the data from a cached file
    or scrape the data from the website. If set to True, the function will read the data from a cached
    file. If set to False, the function will scrape the data from the website, defaults to True
    (optional)
    :return: a pandas DataFrame containing the titles and content of all blog articles from the Codeup
    website. If the data is already cached locally in a CSV file, the function reads the file and
    returns the DataFrame. If not, the function scrapes the website to obtain the data, saves it to a
    CSV file, and returns the DataFrame.
    """
    filename = 'codeup_blogs.csv'
    if from_cache == True:
        return pd.read_csv(filename)
    else:
        # blank list for appending
        blogs = []
        # get front blog page blogs
        blog_page = requests.get('https://codeup.com/blog/',headers=get_header())
        # make a soup
        blog_soup = BeautifulSoup(blog_page.content, 'html.parser')
        # list urls for blogs
        blogs_list = [
            element["href"]
            for element in blog_soup.find_all('a', class_='more-link')
            ]
        # go thru each blog url
        for url in blogs_list:
            # get url webpage
            response = requests.get(url,headers=get_header())
            # soup it
            soup = BeautifulSoup(response.content,'html.parser')
            # get content into empty list
            content = soup.find('div', class_="entry-content").text
            # make blog a dict
            blog = {
                'title':soup.title.text,
                'content':content
                }
            # append to list of blogs
            blogs.append(blog)
        # now do it for all other pages of blogs until we hit the end
        while blog_soup.find('link', {'rel': 'next'}) is not None:
            # get current page
            blog_page = requests.get(blog_soup.find('link', {'rel': 'next'})['href'],headers=get_header())
            # check if good
            if blog_page.status_code == 200:
                # make soup from current page
                blog_soup = BeautifulSoup(blog_page.content, 'html.parser')
                # list urls for blogs
                blogs_list = [
                    element["href"]
                    for element in blog_soup.find_all('a', class_='more-link')
                    ]
                # go thru each blog url
                for url in blogs_list:
                    # get url webpage
                    response = requests.get(url,headers=get_header())
                    # soup it
                    soup = BeautifulSoup(response.content,'html.parser')
                    # get content into empty list
                    content = soup.find('div', class_="entry-content").text
                    # make blog a dict
                    blog = {
                        'title':soup.title.text,
                        'content':content
                        }
                    # append to list of blogs
                    blogs.append(blog)
                continue
            else:
                # if status no good, tell me
                print(f'Error Code: {response.status_code}')
                break
        # make df from dict
        blogs_df = pd.DataFrame(blogs)
        # cache data locally
        blogs_df.to_csv(filename, index=False)
        return blogs_df

# for some reason a lot slower than above
# def get_all_blog_articles():
#     blogs = []
#     blog_page = requests.get('https://codeup.com/blog/',headers=get_header())
#     blog_soup = BeautifulSoup(blog_page.content, 'html.parser')
#     while blog_soup.find('link', {'rel': 'next'}) is not None:
#         if blog_soup.find('link', {'rel': 'prev'}) is not None:
#             blog_page = requests.get(blog_soup.find('link', {'rel': 'next'})['href'],headers=get_header())
#         if blog_page.status_code == 200:
#             blog_soup = BeautifulSoup(blog_page.content, 'html.parser')
#             blogs_list = [
#                 element["href"]
#                 for element in blog_soup.find_all('a', class_='more-link')
#                 ]
#             for url in blogs_list:
#                 response = requests.get(url,headers=get_header())
#                 soup = BeautifulSoup(response.content,'html.parser')
#                 soup_div = soup.find_all('div',class_='entry-content')
#                 soups = BeautifulSoup(f'{soup_div[0]}','html.parser')
#                 content = ''.join(element.text for element in soups.find_all('p'))
#                 blog = {
#                     'title':soup.title.text,
#                     'content':content
#                     }
#                 blogs.append(blog)
#             continue
#         else:
#             print(f'Error Code: {response.status_code}')
#             break
#     return blogs

def get_shorts(from_cache=True):
    """
    This function retrieves news shorts from the website inshorts.com for categories such as business,
    sports, technology, and entertainment, and returns a pandas dataframe of the titles, content, and
    category of each short.
    
    :param from_cache: A boolean parameter that determines whether to read the data from a cached file
    or to scrape the data from the website, defaults to True (optional)
    :return: a pandas DataFrame containing news shorts from various categories such as business, sports,
    technology, and entertainment. The DataFrame has columns for title, content, and category. If the
    `from_cache` parameter is set to `True`, the function reads the data from a local CSV file,
    otherwise it scrapes the data from the internet and caches it locally.
    """
    filename = 'india_shorts.csv'
    if from_cache == True:
        return pd.read_csv(filename)
    else:
        # empty list for appending
        shorts = []
        # base url
        shorts_url = 'https://inshorts.com/en/read/'
        # some of the categories
        categories = ['business','sports','technology','entertainment']
        # check each category
        for cat in categories:
            # get cat webpage
            shorts_get = requests.get(shorts_url+cat,get_header())
            # soup it
            soup = BeautifulSoup(shorts_get.content,'html.parser')
            # get range from len of list of titles on souped page
            for i in range(len([div.find('span').text for div in soup.find_all('div',class_='news-card-title')])):
                # make dict from each title and content from list of them from souped page
                short = {
                    'title':[div.find('span').text for div in soup.find_all('div',class_='news-card-title')][i],
                    'content':[div.find('div').text for div in soup.find_all('div',class_='news-card-content')][i],
                    'category':cat.capitalize()
                    }
                # append to list
                shorts.append(short)
        # make df from dict
        shorts_df = pd.DataFrame(shorts)
        # cache data locally
        shorts_df.to_csv(filename, index=False)
        return shorts_df