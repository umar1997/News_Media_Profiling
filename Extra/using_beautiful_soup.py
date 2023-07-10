import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd


# https://towardsdatascience.com/scraping-1000s-of-news-articles-using-10-simple-steps-d57636a49755

# Check Flow
# 1. Check if URL give 200 status code
# 2. Check if content-type is HTML 


def check_status_code(page):
    return page.status_code == 200

def check_content_type(page):
    return page.headers.get("content-type", "unknown") == 'text/html; charset=UTF-8' # 'text/html; charset=utf-8'

def is_javascript_heavy(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    script_tags = soup.find_all('script')
    javascript_count = 0
    
    for script_tag in script_tags:
        if script_tag.get('src') is not None:
            # External JavaScript file
            javascript_count += 1
        else:
            # Inline JavaScript code
            javascript_count += len(script_tag.text.strip())
    
    # Determine if the website is JavaScript heavy based on a threshold value
    threshold = 10  # Adjust this value based on your requirements
    print(javascript_count)
    return javascript_count >= threshold

# def scrape_articles(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     articles = soup.find_all('article')[:10]  # Limit to 10 articles
    
#     scraped_data = []
    
#     for article in articles:
#         headline = article.find('h2').text.strip()
#         author = article.find('p', class_='author').text.strip()
#         content = article.find('div', class_='content').text.strip()
        
#         scraped_data.append({
#             'headline': headline,
#             'author': author,
#             'content': content
#         })
    
#     return scraped_data

if __name__ == '__main__':

    try:
        # url = 'http://deepleftfield.info'
        url = 'https://www.bloomberg.com/middleeast'
        page = requests.get(url)
        breakpoint()
    except:
        error_type, error_obj, error_info = sys.exc_info()      
    
        #print the link that cause the problem
        print ('ERROR FOR LINK: {}'.format(url))
        
        #print error info and line that threw the exception                          
        print (error_type, 'Line:', error_info.tb_lineno)


    soup = BeautifulSoup(page.text, "html.parser")

    links = soup.find_all('a')
