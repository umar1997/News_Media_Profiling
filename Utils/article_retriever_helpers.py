def get_home_url(news_source_url):
    # Get base url for news_source_url
    if "://" in news_source_url:
        home_url = news_source_url.split('://')[-1] # e.g cnn.com from https://cnn.com
        home_url = home_url.replace('/','')
        return home_url
    return news_source_url


def get_previosly_retrieved_data(news_data, news_source_url, index, news_source_profile, old_news_source_profile):

    home_url = get_home_url(news_source_url)

    news_data["news_id"] = index
    news_data["news_source_url"] = news_source_url
    news_data["news_source_normalized"] = home_url
    news_data["news_source_text"] = old_news_source_profile[news_source_url]["news_source_content"]["news_source_text"]
    news_data["title"] = old_news_source_profile[news_source_url]["news_source_content"]["title"]
    news_data["social_media"] = old_news_source_profile[news_source_url]["social_media"]
    news_data["neighbouring_path"] = old_news_source_profile[news_source_url]["neighbouring_links_base_path"]
    
    if ("redirected" in old_news_source_profile[news_source_url]) or ("empty_website" in old_news_source_profile[news_source_url]):
        return True, news_data
    return False, news_data

import json
def write_to_data(config_path, news_source_url, news_source_profile, news_data):
    pretty_json_string = json.dumps(news_data, indent=4)
    print(pretty_json_string)

    # Sort function based on news_id 
    news_source_profile[news_source_url] = news_data

    data_list = list(news_source_profile.items())
    sorted_data_list = sorted(data_list, key=lambda x: x[1]["news_id"])
    sorted_data = dict(sorted_data_list)

    with open(config_path["news_website_data_path"], 'w') as file:
        json.dump(sorted_data, file, indent=4)
    print('Success: Written news_source {} to json file.'.format(news_source_url))


import newspaper
def get_from_newspaper3k(news_source_url, news_data):
    total_articles = set()
    try:
        news_source_newspaper3k = newspaper.Article(news_source_url)
        news_source_newspaper3k.download()
        config = newspaper.Config()
        config.memoize_articles = False
        news_source_list_urls = newspaper.build(news_source_url, config)
        total_articles  = set([a.url for a in news_source_list_urls.articles])

    except Exception as e:
        # news_data["error"] = DOWNLOAD_FAILED
        print("Exception: {} \nwith Newspaper3K".format(e))
        raise Exception("Exception: {} \nwith Trafilatura".format(e))

    return news_data, total_articles

def get_from_trafilatura(news_source_url, news_data):
    result, downloaded_raw_html = None, None
    try:
        downloaded_raw_html = trafilatura.fetch_url(news_source_url)
        if downloaded_raw_html == None:
            return result, downloaded_raw_html
        result = trafilatura.extract(downloaded_raw_html, output_format="json", url=news_source_url)
        if result == None:
            return result, downloaded_raw_html

        return result, downloaded_raw_html

    except Exception as e:
        # news_data["error"] = DOWNLOAD_FAILED
        print("Exception: {} \nwith Trafilatura".format(e))
        raise Exception("Exception: {} \nwith Trafilatura".format(e))

from bs4 import BeautifulSoup
def get_from_beautifulsoup(news_data, downloaded_raw_html, total_articles):
    soup = BeautifulSoup(downloaded_raw_html, 'html.parser')
    all_links = soup.find_all('a')
    for link in all_links:
        href = link.get('href')
        if (href is not None):
            if ('http' in href) and ('://' in href):
                total_articles.add(href)
            if "twitter.com" in href:
                news_data["social_media"]["twitter"] = href
            if "facebook.com" in href:
                news_data["social_media"]["facebook"] = href
            if "instagram.com" in href:
                news_data["social_media"]["instagram"] = href
            if "youtube.com" in href:
                news_data["social_media"]["youtube"] = href

    print('Total number of articles for {} found: {}'.format(href, len(total_articles)))
    return total_articles, news_data