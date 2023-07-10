import os
import json
from datetime import datetime

from Utils.log import get_logger
from Utils.get_articles import article_retriever


if __name__ == '__main__':

    current_datetime = datetime.now()
    date = current_datetime.strftime("%d-%m-%Y")
    date_time = current_datetime.strftime("%d-%m-%Y_%H:%M")

    Log_Folder = os.path.join(os.getcwd(),'Log_Files')
    file_name =  os.path.join(Log_Folder, "Scrape_Run_" + date_time)

    logger_meta = get_logger(name='META', file_name=file_name, type='meta')
    logger_progress = get_logger(name='PROGRESS', file_name=file_name, type='progress')

    logger_meta.warning('Start Time: {}'.format(date_time))
    logger_object = [logger_meta, logger_progress]

    with open("./config_path.json", 'r') as f:
        config_path = json.load(f)

    with open(config_path["news_sources_path"], 'r') as f:
        news_source_list = json.load(f)

    with open(config_path["news_profiling_data_path"], 'r') as f:
        news_source_profile = json.load(f)

    breakpoint()
    article_retriever(config_path, news_source_list, news_source_profile, logger_object)

    date_time = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    logger_meta.warning('End Time: {}'.format(date_time))