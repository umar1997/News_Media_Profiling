import json
import newspaper
from datetime import datetime
from newspaper import Article

from Utils.url_validation import URLValidation, check_child_news_article
from Utils.helpers import append_http

def get_templates():

    template_articles = {
            "article_url": "",
            "article_html": "",
            "article_content": "",
        }

    template_data = {
        "news_source": "",
        "news_source_normalized": "",
        "news_source_html": "",
        "news_source_content": "",
        "neighbouring_links_full_path": [],
        "neighbouring_links_base_path": [],
        "articles": {},
        "article_links": [],
        "prev_labels": {}
    }

    return template_data, template_articles

def get_specific_article_data(news_source_key, news_source_url, total_articles, news_data, news_source_profile, logger_object, url_validator, template_articles):

    """
    news_source_key: base URL of news source taken from the list of news source links to scrape
    news_source_url: The URL for the News Source we are scraping
    total_articles: All the articles of that news source
    news_source_profile: The dictionary from .json loaded file 
    logger_object: Contains both loggers
    url_validator: Helps to validate whether the URL is valid or not
    template_articles: The template for articles provided by function 'get_templates()'
    news_data: Data Object for the News Source that is to be written into the .json file for that News Source
    
    """
    logger_meta, logger_progress = logger_object
    for news_source_article in total_articles:
        news_article_url = news_source_article.url

        logger_progress.critical('Article: {}'.format(news_article_url))

        is_valid_url = url_validator.run_validation(news_article_url)
        if is_valid_url:
            article_data = template_articles.copy()
            is_child_news_article = check_child_news_article(news_source_url, news_article_url)
            try:
                news_article = Article(news_article_url)
                if not is_child_news_article:
                    base_path , _ = URLValidation.extract_url_parts(news_article_url)
                    if not base_path: 
                        news_data["neighbouring_links_full_path"].append(news_article_url)
                        news_data["neighbouring_links_base_path"].append(base_path)
                
                # Specififc Article Data
                news_article.download()
                article_data["article_url"] = news_article_url
                news_data["article_links"].append(news_article_url)
                article_data["article_content"] = news_article.text
                # article_data["article_html"] = news_article.html

                if news_article_url not in news_data["articles"]:
                    news_data["articles"][news_article_url] = article_data

                # Adding to existing news_profiling_data.json file
                news_source_profile[news_source_key] = news_data
                
            except Exception as e:
                logger_progress.critical("Failure: Issue with this article URL: {}".format(news_article_url))
                logger_progress.critical("Exception: {}".format(e))
        else:
            continue
            # logger_progress.critical("News Article Invalid: {}".format(news_article_url))

    logger_object = [logger_meta, logger_progress] 
    return news_source_profile, logger_object




def article_retriever(config_path, news_source_list, logger_object):

    logger_meta, logger_progress = logger_object
    url_validator = URLValidation()

    for news_source_key, news_source_value in news_source_list.items():

        template_data, template_articles = get_templates()
        logger_meta.warning('News Source: {}'.format(news_source_key))

        with open(config_path["news_profiling_data_path"], 'r') as f:
            news_source_profile = json.load(f)

        # Check if the news source has been scraped or not and the articles scraped are atleast of count X
        if news_source_key not in news_source_profile : 

            # If the url doesn't have http or https in the beginning then add it
            news_source_url = append_http(news_source_key)

            # Check if url meets the valid criteria
            is_valid_url = URLValidation.is_string_an_url(news_source_url)
            if is_valid_url:

                try:
                    news_data = template_data.copy()

                    news_source = Article(news_source_url)
                    news_source.download()
                    news_data["news_source"] = news_source_url
                    news_data["news_source_normalized"] = news_source_value["source_url_normalized"]
                    news_data["news_source_content"] = news_source.text
                    news_data["prev_labels"] = {"fact": news_source_value["fact"], "bias":news_source_value["bias"]}
                    # news_data["news_source_html"] = news_source.html

                    news_source_urls = newspaper.build(news_source_url, memoize_articles=False)
                    logger_progress.critical('Success: Successfully extracted/downloaded {}'.format(news_source_url))

                    total_articles  = news_source_urls.articles
                    logger_progress.critical('Total number of articles for news source found: {}'.format(len(total_articles)))
                    breakpoint()
                    logger_object = [logger_meta, logger_progress]

                    # Get all articles data
                    news_source_profile, logger_object = get_specific_article_data(news_source_key, news_source_url, total_articles, news_data, news_source_profile, logger_object, url_validator, template_articles)

                    with open('./Data/news_profiling_data.json', 'w') as file:
                        json.dump(news_source_profile, file, indent=4)

                except Exception as e:
                    logger_progress.critical('Failure: Failed to extract/download {}'.format(news_source_url))
                    logger_progress.critical('Error: {}'.format(e))

            else:
                print("{}: is an invalid news source url".format(news_source_url))

            date_time = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
            logger_meta.warning('Current Time: {}\n'.format(date_time))
        else:
            logger_progress.critical('News Source already has been scraped: {}\n'.format(news_source_key))
        

