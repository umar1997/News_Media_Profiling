import os
import sys
import json
from datetime import datetime

from Utils.log import get_logger
from Utils.get_articles import article_retriever


if __name__ == '__main__':

 
    current_datetime = datetime.now()
    date_time = current_datetime.strftime("%d-%m-%Y_%H:%M")

    print('Start Time: {}\n'.format(date_time))

    config_path = os.path.join(os.getcwd(), 'config_path.json')
    with open(config_path, 'r') as f:
        config_path = json.load(f)

    with open(config_path["news_sources_path"], 'r') as f:
        news_source_list = json.load(f)

    if not os.path.exists(config_path["news_website_data_path"]):
        empty_data = {}
        with open(config_path["news_website_data_path"], 'w') as file:
            json.dump(empty_data, file)

    article_retriever(config_path, news_source_list)

    date_time = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    print('End Time: {}'.format(date_time))

