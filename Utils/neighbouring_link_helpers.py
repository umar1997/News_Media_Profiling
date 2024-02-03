

def check_neighbour_link_is_social_media(news_article_url):

    if not news_article_url.startswith("http"):
        return True, news_article_url
    if ("twitter.com" in news_article_url) or ("facebook.com" in news_article_url) or  ("instagram.com" in news_article_url) or ("youtube.com" in news_article_url):
        return True, news_article_url
    if "?share=" in news_article_url:
        news_article_url = news_article_url.split("?share=")[0]
        return False, news_article_url



from Utils.url_validation import URLValidation
def check_neighbour_link_is_not_child_article(news_data, news_article_url, home_url, not_child_counter):
    not_child_counter += 1
    base_path , _ = URLValidation.extract_url_parts(news_article_url)

    if base_path and (home_url not in news_article_url): 
        news_data["neighbouring_path"].append(base_path)

    return not_child_counter, news_data



import trafilatura
from bs4 import BeautifulSoup
def check_neighbour_links_in_child_articles(news_article_url, news_data, DOWNLOAD_FAILED):
    try:
        downloaded_raw_html = trafilatura.fetch_url(news_article_url)
        if downloaded_raw_html == None:
            news_data["error"] = DOWNLOAD_FAILED
            return news_article_url, news_data
    except Exception as e:
        print("Error Reason: {}".format(e))
        raise Exception(f"Error in func(check_neighbour_links_in_child_articles - 1)")

    try:
        soup = BeautifulSoup(downloaded_raw_html, 'html.parser')
        all_links = soup.find_all('a')
        for link in all_links:
            href = link.get('href')
            is_social_media = ("twitter.com" in news_article_url) or ("facebook.com" in news_article_url) or ("instagram.com" in news_article_url) or ("youtube.com" in news_article_url)
            if (href == None) or (not href.startswith("http")) or (is_social_media):
                continue
            else:
                if ('http' in href) and ('://' in href):
                    is_child_news_article = check_child_news_article(news_source_url, href)
                    if not is_child_news_article:
                        base_path , _ = URLValidation.extract_url_parts(href)
                        if base_path and (home_url not in href):
                            news_data["neighbouring_path"].append(base_path)
        return news_article_url, news_data
    except Exception as e:
        print("Error Reason: {}".format(e))
        raise Exception(f"Error in func(check_neighbour_links_in_child_articles - 2)")
                        
