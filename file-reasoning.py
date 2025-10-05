import pandas as pd
import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv('.env')
url_endpoint = os.getenv("URL_ENDPOINT")
model = os.getenv("MODEL")
api_key = os.getenv("API_KEY")

def overview_generator(df, endpoint_url, api_key):
    df_str = df.to_csv(index=False)
    payload = {
        "messages": [
            {"role": "system", "content": "You are a text generator that responsible for generating an overview of the given data. Summarize the data, provide column descriptions, total number of columns (headers), total number of records (do not include header), metadata, statistical data, data relationships, and other insight that you may have analyze see fit for knowledge retrieval purposes. Reply only the result in JSON format with keys: summary, column_descriptions, total_columns, total_rows, etc. Do not add any additional commentary or information outside of the JSON format. Each value must be data enrichment so that it can be easily be parsed by knowledge retrieval systems. Ensure that the data overview is comprehensive and captures the essence of the dataset."},
            {"role": "user", "content": f"Here is the data:\n{df_str}"}
        ],
        "model": model
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(endpoint_url, json=payload, headers=headers)
    result = response.json()
    total_tokens = result.get("usage", {}).get("total_tokens")
    content = result.get("choices", [{}])[0].get("message", {}).get("content")
    response.close()
    return total_tokens, content

def data_extractor(df, endpoint_url, api_key):
    df_str = df.to_csv(index=False)
    payload = {
        "messages": [
            {"role": "system", "content": "You are a text generator that formats each records of the given data into a single proper consistent paragraph (3-5 sentences) with data enrichment so that it can be easily be parsed by knowledge retrieval systems. Reply only the result in JSON format each data as an element of an array named data, and with each key values is equivalent to the records number (e.g. Record 1) and the paragraph is the value. You only have 8192 tokens to work with so make sure all of the record are included. Do not add any additional commentary or information outside of the JSON format."},
            {"role": "user", "content": f"Here is the data:\n{df_str}"}
        ],
        "model": model
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(endpoint_url, json=payload, headers=headers)
    result = response.json()
    total_tokens = result.get("usage", {}).get("total_tokens")
    content = result.get("choices", [{}])[0].get("message", {}).get("content")
    response.close()
    return total_tokens, content

def excel_to_dataframe(file_path):
    df = pd.read_excel(file_path)
    return df

# Example usage:
dataframe = excel_to_dataframe('input/Financial Sample.xlsx')

total_header_tokens, header_content = overview_generator(dataframe, url_endpoint, api_key)
with open('output/response_output.txt', 'w', encoding='utf-8') as f:
    f.write(f"{header_content}")

total_data_tokens, data_content = data_extractor(dataframe, url_endpoint, api_key)
with open('output/data_output.txt', 'w', encoding='utf-8') as f:
    f.write(f"{data_content}")

print("Total Header Tokens:", total_header_tokens)
print("Total Data Tokens:", total_data_tokens)