

def append_http(news_source_key):
    if "http" not in news_source_key:
        news_source_url = "http" + "://" + news_source_key
    else:
        news_source_url = news_source_key
    return news_source_url