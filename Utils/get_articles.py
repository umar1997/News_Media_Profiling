import newspaper
from newspaper import Article

from Utils.url_validation import URLValidation, check_child_news_article

def get_templates():

    template_articles = {
            "article_url": "",
            "article_html": "",
            "article_text": "",
        }

    template_data = {
        "news_source": "",
        "news_source_normalized": "",
        "news_source_html": "",
        "news_source_content": "",
        "neighbouring_links": [],
        "articles": {},
        "article_links": [],
        "prev_labels": {}
    }

    return template_data, template_articles

def article_retriever(config_path, news_source_list, news_source_profile, logger_object):

    template_data, template_articles = get_templates()
    logger_meta, logger_progress = logger_object
    url_validator = URLValidation()

    for news_source_key, news_source_value in news_source_list.items():

        logger_meta.warning('\nNews Source: {}'.format(news_source_key))

        # Check if the news source has been scraped or not and the articles scraped are atleast of count X
        if news_source_key not in news_source_profile : 

            # If the url doesn't have http or https in the beginning then add it
            if "http" not in news_source_key:
                news_source_url = "http" + "://" + news_source_key
            else:
                news_source_url = news_source_key

            # Check if url meets the valid criteria
            is_valid_url = URLValidation.is_string_an_url(news_source_url)
            if is_valid_url:

                try:
                    news_data = template_data.copy()
                    news_data["news_source"] = news_source_url
                    news_data["news_source_normalized"] = news_source_value["source_url_normalized"]
                    news_data["prev_lables"] = {"fact": news_source_value["fact"], "bias":news_source_value["bias"]}

                    news_source = Article(news_source_url)
                    news_source.download()
                    news_data["news_source_html"] = news_source.html
                    news_data["news_source_content"] = news_source.text
                    news_source_urls = newspaper.build(news_source_url, memoize_articles=False)
                    logger_progress.critical('Success: Successfully extracted/downloaded {}'.format(news_source_url))

                    total_articles  = news_source_urls.articles
                    logger_progress.critical('Total number of articles for news source found: {}'.format(total_articles))

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
                                    if not base_path: article_data["neighbouring_links"].append(news_article_url)
                                news_article.download()
                                article_data["article_links"].append(news_article_url)
                                article_data["news_source_html"] = news_article.html
                                article_data["news_source_content"] = news_article.text
                                
                            except Exception as e:
                                logger_progress.critical("Failure: Issue with this article URL: {}".format(news_article_url))
                                logger_progress.critical("Exception: {}".format(e))
                        else:
                            logger_progress.critical("News Article Invalid: {}".format(news_article_url))
                except Exception as e:
                    logger_progress.critical('Failure: Failed to extract/download {}'.format(news_source_url))
                    logger_progress.critical('Error: {}'.format(e))

            else:
                print("{}: is an invalid news source url".format(news_source_url))
        else:
            logger_progress.critical('News Source already has been scraped: {}'.format(news_source_key))
