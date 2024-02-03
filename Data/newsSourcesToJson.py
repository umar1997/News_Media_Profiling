import json
import pandas as pd
from copy import deepcopy


file_path = './corpus_1.tsv'
output_file = 'news_sources_v1.json'

dataframe = pd.read_csv(file_path, sep='\t')
df = dataframe.fillna('')
assert len(df) == len(df['source_url'].unique())

data_dict = df.to_dict(orient='records')
json_data = {}

for record in data_dict:
    key = record['source_url']
    del record['source_url']
    if (not record['fact']) or (not record['bias']):
        continue
    json_data[key] = record


with open(output_file, 'w') as file:
    json.dump(json_data, file, indent=2)

print('Greener - Number of unique news sources: {}'.format(len(json_data.keys())))
print('Saved successfully!')

##################################################

def convert_name(value):
    return value

# https://github.com/zainmujahid/ChatGPT_domain_rating/blob/main/data/mbfc_ratings.csv
file_path = './corpus_2.csv'
output_file = 'news_sources_v2.json'

df = pd.read_csv(file_path)
columns_to_check = ['factual_reporting', 'bias_rating', 'source']
df.dropna(subset=columns_to_check, how='any', inplace=True)
df.drop_duplicates(subset='source', keep='first', inplace=True)
assert len(df) == len(df['source'].unique()) # 3736
df.fillna('', inplace=True)
data_dict = df.to_dict(orient='records')
json_data = {}

for record in data_dict:
    key = record['source']
    if (not record['factual_reporting']) or (not record['bias_rating']):
        continue
    json_data[key] = {}
    json_data[key]['source_url_normalized'] = record['domain']
    json_data[key]['ref'] = record['mbfclink']
    json_data[key]['fact'] = convert_name(record['factual_reporting'])
    json_data[key]['bias'] = convert_name(record['bias_rating'])

with open(output_file, 'w') as file:
    json.dump(json_data, file, indent=2)

print('MBFC - Number of unique news sources: {}'.format(len(json_data.keys())))
print('Saved successfully!')

##################################################


# Greener 859
output_file = 'news_sources_v1.json'
with open(output_file, 'r') as file:
    data_1 = json.load(file)

# MBFC 3736
output_file = 'news_sources_v2.json'
with open(output_file, 'r') as file:
    data_2 = json.load(file)

final_data = deepcopy(data_1)
for k, v in data_2.items():
    if k not in final_data:
        if k[-1] != ("/"):
            k += "/"
        final_data[k] = v

# Union of Greener and MBFC
output_file = 'news_sources_v3.json'
with open(output_file, 'w') as file:
    json.dump(final_data, file, indent=2)

print('Greener x MBFC - Number of unique news sources: {}'.format(len(final_data.keys())))
print('Saved successfully!')

##################################################

file_path = './corpus_3.xlsx'
output_file = 'news_sources_final.json'

df = pd.read_excel(file_path)
df.drop_duplicates(subset='site', keep='first', inplace=True)
data_dict = df.to_dict(orient='records')

alexa_docs = set([data['site'] for data in data_dict])

filtered_data = {}
for key, v in final_data.items():
    domain = key.replace("wwww.", "")
    domain = domain.split('://')[-1]
    domain = domain.split('/')[0]

    if (domain in alexa_docs) or (v['source_url_normalized'] in alexa_docs):
        filtered_data[key] = v


def append_http(news_source):
    if "http" not in news_source:
        news_source_url = "http" + "://" + news_source
    else:
        news_source_url = news_source
    if news_source_url[-1] != '/':
        news_source_url += '/'
    return news_source_url

final_data = {}
for key, val in filtered_data.items():
    news_source = append_http(key)
    final_data[news_source] = val


# Union of Greener and MBFC which are in Alexa Rank
with open(output_file, 'w') as file:
    json.dump(final_data, file, indent=2)

print('Greener x MBFC x AlexaRank - Number of unique news sources: {}'.format(len(filtered_data.keys())))
print('Greener x MBFC x AlexaRank (Add Http)- Number of unique news sources: {}'.format(len(final_data.keys())))
print('Saved successfully!')


# Corpus 1 - Greener 859
# Corpus 2 - MBFC 3736
# Corpus 3 - AlexaRank 67351

# news_sources_v1 859 - Greener
# news_sources_v2 3736 - MBFC
# news_sources_v3 4506 - MBFC Union Greener
# news_sources_final 2477 - MBFC x Greener x AlexaRank
# news_sources_final 2259 (Add Http) - MBFC x Greener x AlexaRank


output_file = 'news_sources_final.json'
with open(output_file, 'r') as file:
    data_final = json.load(file)

bias_set = set()
fact_set = set()
for key, val in data_final.items():
    fact_set.add(data_final[key]["fact"].lower())
    bias_set.add(data_final[key]["bias"].lower())

print(f"Bias Set Length: {len(bias_set)}")
print(f"Fact Set Length: {len(fact_set)}")

print(f"Fact Set: \n{fact_set}\n")
print(f"Bias Set: \n{bias_set}\n")

bias_filtered_set = []
for b in bias_set:
    if ('right' not in b) and ('left' not in b):
        bias_filtered_set.append(b)

print(bias_filtered_set)
