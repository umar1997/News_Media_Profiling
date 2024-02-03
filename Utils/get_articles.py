import os
import sys
import time
import json

import requests
from tqdm import tqdm
from datetime import datetime

import newspaper
import trafilatura
from bs4 import BeautifulSoup

from Utils.url_validation import URLValidation, check_child_news_article
from Utils.article_retriever_helpers import *
from Utils.neighbouring_link_helpers import check_neighbour_link_is_social_media, check_neighbour_link_is_not_child_article, check_neighbour_links_in_child_articles

def get_templates():

    template_data = {
        "news_id": None,
        "news_source_url": "",
        "title":"",
        "news_source_text": "",
        "neighbouring_path": [],
        "social_media":{
            "twitter":"",
            "facebook":"",
            "instagram":"",
            "youtube":""
        },
        "error": ""
    }

    return template_data

INVALID_URL = '<INVALID_URL>'
DOWNLOAD_FAILED = '<DOWNLOAD_FAILED>'
EXPIRED_URL = '<EXPIRED_URL>'
TIMEOUT_URL = '<TIMEOUT_URL>'
EMPTY_DATA = '<EMPTY_DATA>'

def get_neighbouring_links(news_source_url, home_url, total_articles, news_data, news_source_profile, url_validator):

    not_child_counter = 0
    for news_article_url in total_articles:

        is_social_media , news_article_url = check_neighbour_link_is_social_media(news_article_url)
        if is_social_media:
            continue

        is_child_news_article = check_child_news_article(news_source_url, news_article_url)
        if not is_child_news_article:
        not_child_counter, news_data = check_neighbour_link_is_not_child_article(news_data, news_article_url, home_url, not_child_counter)
            continue

        is_valid_url = url_validator.run_validation(news_article_url)
        if is_valid_url:

        else:
            news_data["error"] = INVALID_URL

    news_data["neighbouring_path"] = list(set(news_data["neighbouring_path"]))
    if not_child_counter == len(total_articles):
        news_data["error"] = EXPIRED_URL
    if abs(not_child_counter - len(total_articles)) <= 3:
        news_data["error"] = EXPIRED_URL
    
    return news_data



def article_retriever(config_path, news_source_list):


    with open('output.log', 'w') as log_file:
        sys.stdout = log_file
        
        url_validator = URLValidation()

        index = 1
        for news_source_key, news_source_value in tqdm(news_source_list.items()):
            
            news_source_url = news_source_key
            template_data = get_templates()
            news_data = template_data.copy()

            print("************* {} *************".format(index))
            print('News Source: {}'.format(news_source_url))

            with open(config_path["news_website_data_path"], 'r') as f:
                news_source_profile = json.load(f)

    #############################################################################################
            with open(config_path["old_news_website_data_path"], 'r') as f:
                old_news_source_profile = json.load(f)
            
            if (news_source_url in old_news_source_profile):
                article_expired, news_data = get_previosly_retrieved_data(news_data, news_source_url, index, news_source_profile, old_news_source_profile)
                if article_expired:
                    news_data["error"] = EXPIRED_URL
                
                write_to_data(config_path, news_source_url, news_source_profile, news_data)
                index += 1
                continue
    #############################################################################################

            # Already been scraped
            if news_source_url in news_source_profile:
                print('Info: News Source already has been scraped: {}\n'.format(news_source_url))
                index += 1
                continue

            else: 

                # Append http:// if url doesn't have it and validate if valid url (from Utils.url_validation)
                is_valid_url = URLValidation.is_string_an_url(news_source_url)

                news_data = template_data.copy()
                news_data["news_id"] = index
                news_data["news_source_url"] = news_source_url
                news_data["news_source_normalized"] = home_url
                news_data["title"] = ""
                news_data["news_source_text"] = ""

                # Get article links embedded in the website
                if not is_valid_url:
                    news_data["error"] = INVALID_URL
                    print("News Source: {} Error: {} ".format(news_source_url, news_data["error"]))
                    write_to_data(config_path, news_source_url, news_source_profile, news_data)
                    index += 1
                    continue
                else:

                    # newspaper3k
                    news_data, total_articles = get_from_newspaper3k(news_source_url, news_data)

                    # Trafilatura to Download
                    result, downloaded_raw_html = get_from_trafilatura(news_source_url, news_data)

                    if result:
                        result = result.replace('null','None')
                        result = eval(result)
                        
                        news_data["title"] = "" if result["title"] == None else result["title"]
                        news_data["news_source_text"] = "" if result["text"] == None else result["text"]
                    else:
                        news_data["title"] = ""
                        news_data["news_source_text"] = ""
                        news_data["error"] = EMPTY_DATA

                    # BeautifulSoup                          
                    if downloaded_raw_html:
                        total_articles, news_data = get_from_beautifulsoup(news_data, downloaded_raw_html, total_articles)
                    else:
                        news_data["error"] = DOWNLOAD_FAILED
    
                    total_articles = list(total_articles)
                    news_data = get_neighbouring_links(news_source_url, home_url, total_articles, news_data, news_source_profile, url_validator)

                    write_to_data(config_path, news_source_url, news_source_profile, news_data)
                    index+= 1

                    time.sleep(5)
        
    sys.stdout = sys.__stdout__
        

