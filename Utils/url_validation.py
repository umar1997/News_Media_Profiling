import re
import string
import validators
from validators import ValidationFailure


def check_child_news_article(parent_url:str, url_string: str) -> bool:
    parent_url = parent_url.replace("www.", "")
    parent_url = parent_url.split("://")[-1]

    dot_index = url_string.find('.', url_string.find('www.') + len('www.')) if "www." in url_string else url_string.find('.')
    url_index = url_string.lower().find(parent_url.lower())
    if url_index == -1 or dot_index == -1:
        return True if parent_url in url_string else False
    if parent_url in url_string:
        if url_index > dot_index:
            return False
        else:
            return True
    

class URLValidation:
    def __init__(self,) -> None:
        
        self.url = None

    @staticmethod
    def is_string_an_url(url) -> bool:
        result = validators.url(url)

        if isinstance(result, ValidationFailure):
            return False
        return result

    @staticmethod
    def extract_url_parts(url):
        dot_index = url.find('.')
        if dot_index != -1:
            url_substring = url[dot_index + 1:]
            slash_index = url_substring.find('/')
            if slash_index != -1:
                main_index = dot_index + 1 + slash_index
                base_url = url[:main_index]
                pathname_url = url[main_index:]
                return base_url, pathname_url
            return url, None
        return None, None



    def validate_url(self, pathname_url_string: str) -> bool:

        pattern = "^[a-zA-Z0-9\/\-\?\=\#]+$"
        # if '#' in pathname_url_string: # In cases where the URL has an extension /#
        #     return False 

        if '.' in pathname_url_string: # In case where url has .pdf or .html
            return False

        if not re.match(pattern, pathname_url_string): # Making sure url only has / - and alphanumeric characters
            return False

        # if '/' in pathname_url_string:
        #     split_on_slashes = pathname_url_string.split('/')
        #     dash_element_list = [item for item in split_on_slashes if item.count('-') > 2]
        #     if not len(dash_element_list): # Making sure a url is a link of a story which is most likely when has dashes in pathname
        #         return False
        # else: return False 

        return True

    def run_validation(self, url):
        try:
            self.url = url
            if self.is_string_an_url(self.url):
                base_url, pathname_url = self.extract_url_parts(self.url)
                if base_url == None:
                    return False # URL is not correct
                if pathname_url == None:
                    return True # base url is correct
                is_valid = self.validate_url(pathname_url)
                return is_valid
            else:
                return False
        except Exception as e:
            print('Issue in URL Validation: {}'.format(url))
            print('Error: {}'.format(e))
            breakpoint()
            # raise Exception("URL is not a valid format")



if __name__ == '__main__':
    # True
    url = 'https://antifascistnews.net/2019/03/13/antifascist-mobilization-leads-two-venues-to-cancel-molyneux-and-southern-event-in-vancouver-bc-free-speechers-turn-to-secret-location-for-march-15/'
    # False
    # url = "https://deepleftfield.info/melanias-plan-to-write-a-memoir-draws-suggestions-for-an-appropriate-title/?share=facebook"
    # url = "https://deepleftfield.info/stephen-millers-wife-announces-birth-of-their-first-child-and-gets-reminded-of-her-husbands-evil/#respond"
    # url = "https://deepleftfield.info/2015/01/"
    print(URLValidation().run_validation(url))
