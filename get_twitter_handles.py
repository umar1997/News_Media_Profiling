import sys
import json
import time
import multiprocessing

import urllib3
import requests
import httplib2
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from Utils.helpers import append_http

##########################################################################
def get_website_response_request(result_queue, news_src):
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    response = requests.get(news_src, headers=headers, verify=False)
    result_queue.put(response)

def get_website_response_urlib3(result_queue, news_src):
    
    http = urllib3.PoolManager()
    response = http.request('GET', news_src)
    page_source = response.data.decode('utf-8')
    result_queue.put(page_source)

def get_website_response_httplib2(result_queue, news_src):
    
    http = httplib2.Http()
    response, content = http.request(news_src)
    page_source = content.decode('utf-8')
    result_queue.put(page_source)
##########################################################################


def create_list(news_source_list, output_file):

    twitter_objects = []
    for i, (news_src_og, _) in enumerate(news_source_list.items()):

        try:
            with open(output_file, 'r') as json_file:
                news_source_twitter = json.load(json_file)
        except FileNotFoundError:
            news_source_twitter = {}

        # if (i+1) <= 309:
        #     continue
        if news_src_og in list(news_source_twitter.keys()):
            if (news_source_twitter[news_src_og]["twitter_handler"] == "<ERROR>") or (news_source_twitter[news_src_og]["twitter_handler"] == "<EMPTY>") or (news_source_twitter[news_src_og]["twitter_handler"] == "<FIX>"):
                if (news_source_twitter[news_src_og]["twitter_creator"] == "<ERROR>") or (news_source_twitter[news_src_og]["twitter_creator"] == "<EMPTY>") or (news_source_twitter[news_src_og]["twitter_creator"] == "<FIX>"):
                    pass 
            else:
                continue
        else:
            pass

        news_src = append_http(news_src_og)

        print("#"*30)
        print("Item No. {}".format(i+1))
        print("News Source: {}".format(news_src))

        item = {
            "news_src": news_src,
            "id": i+1
        }

        try:
            # response = urllib.request.urlopen(news_src)
            # soup = BeautifulSoup(response, 'html.parser')
            ##########################################################################
            # ignore_scrape = False

            timeout = 50
            result_queue = multiprocessing.Queue()
            
            # # process = multiprocessing.Process(target=get_website_response_request, args=(result_queue,news_src,))
            # # process = multiprocessing.Process(target=get_website_response_urlib3, args=(result_queue,news_src,))
            process = multiprocessing.Process(target=get_website_response_httplib2, args=(result_queue,news_src,))

            process.start()
            process.join(timeout) # Wait for the process to finish or timeout
            if process.is_alive(): # If the process is still running, terminate it
                process.terminate()
                print("{}: Took too long to execute.".format(news_src))
                item['twitter_handler'] = '<EMPTY>'
                item['twitter_creator'] = '<EMPTY>'
                ignore_scrape = True
            else:
                if not result_queue.empty():
                    response = result_queue.get()
                    print("{}: Result retrieved: ".format(news_src))
                else:
                    print("{}: No result retrieved.".format(news_src))
                    item['twitter_handler'] = '<EMPTY>'
                    item['twitter_creator'] = '<EMPTY>'
                    ignore_scrape = True
            ##########################################################################

            # http = httplib2.Http()
            # response, content = http.request(news_src)
            # page_source = content.decode('utf-8')

            ignore_scrape = False
            if not ignore_scrape:
                # if response.status_code == 200: # For requests
                if response.status == 200: # For httplib2

                    # soup = BeautifulSoup(response.content, 'html.parser') # For requests
                    soup = BeautifulSoup(page_source, 'html.parser') # For httplib2

                    if soup.findAll("meta", attrs={"name": "twitter:site"}):
                        twitter_handler = soup.find("meta", attrs={"name": "twitter:site"}).get("content")

                        item['twitter_handler'] = twitter_handler
                        item['twitter_creator'] = twitter_handler

                    elif soup.findAll("meta", attrs={"name": "twitter:creator"}):
                        twitter_creator = soup.find("meta", attrs={"name": "twitter:creator"}).get("content")
                        item['twitter_handler'] = '<EMPTY>'
                        item['twitter_creator'] = twitter_creator

                    elif "twitter" in str(soup):
                        item['twitter_handler'] = '<FIX>'
                        item['twitter_creator'] = '<FIX>'

                    else:
                        item['twitter_handler'] = '<EMPTY>'
                        item['twitter_creator'] = '<EMPTY>'

                else:
                    item['twitter_handler'] = '<ERROR>'
                    item['twitter_creator'] = '<ERROR>'
                    item['issue_type'] = "Status Code: {}".format(response.status_code)

        except Exception as e:
            item['twitter_handler'] = '<ERROR>'
            item['twitter_creator'] = '<ERROR>'
            item['issue_type'] = "Exception Error: {}".format(e)

        time.sleep(2)
        print(item)

        news_source_twitter[news_src_og] = item

        # breakpoint()
        with open(output_file, 'w') as json_file:
            json.dump(news_source_twitter, json_file, indent=4)


def sort_list(input_file):

    with open(input_file, 'r') as f:
        twitter_list = json.load(f)

    data_list = list(twitter_list.items())

    sorted_data_list = sorted(data_list, key=lambda x: x[1]["id"])
    sorted_data = dict(sorted_data_list)

    breakpoint()
    with open(input_file, 'w') as json_file:
        json.dump(sorted_data, json_file, indent=4)


if __name__ == '__main__':

    with open("./config_path.json", 'r') as f:
        config_path = json.load(f)

    with open(config_path["news_sources_path"], 'r') as f:
        news_source_list = json.load(f)

    with open(config_path["twitter_sources_path"], 'r') as f:
        twitter_source_list = json.load(f)

    # create_list(news_source_list, config_path["twitter_sources_path"]) # To Run Scraping

    sort_list(config_path["twitter_sources_path"]) # To Run Sorting
    
