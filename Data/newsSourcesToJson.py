import json
import pandas as pd


file_path = './corpus.tsv'
output_file = 'news_sources.json'

dataframe = pd.read_csv(file_path, sep='\t')
df = dataframe.fillna('')
assert len(df) == len(df['source_url'].unique())

data_dict = df.to_dict(orient='records')
json_data = {}

for record in data_dict:
    key = record['source_url']
    del record['source_url'] 
    json_data[key] = record


with open(output_file, 'w') as file:
    json.dump(json_data, file, indent=2)

print('Number of unique news sources: {}'.format(len(json_data.keys())))
print('Saved successfully!')

# json_str = json.dumps(json_data, indent=2)
# print(json_str)