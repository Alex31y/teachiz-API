import json

# Read the JSON file
file_path = "articoli repubblica.json"

with open(file_path, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Extract titles and add them to a list
title_list = [{"title": item["title"], "url": item["url"]} for item in data]

# Print the list of titles
print(title_list)


import os
import openai

openai.api_key = "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"

def filtrArticolo(articoli):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-16k",
      messages=[
        {
          "role": "user",
          "content": f"dato il seguente insieme di titoli di giornale, restituiscimi una json contenente esclusivamente l'url degli articoli informativi sulla politica e sul governo in ordine di rilevanza alla politica  {title_list}"
        }
      ],
      temperature=1,
      max_tokens=4010,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    che_ha_detto = response['choices'][0]['message']['content']
    return che_ha_detto

# Analizza la stringa JSON
articoli = filtrArticolo(title_list)
print(articoli)
data = json.loads(articoli)

# Estrai gli URL e inseriscili in una lista
url_list = [article['url'] for article in data['articles']]
url_list = url_list[:3]

from bs4 import BeautifulSoup
import requests

def scraper(url):
    print("scraping new url: " + url)
    try:
        response = requests.get(url)
        # Create a BeautifulSoup object from the response text
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract all paragraphs from the page
        paragraphs = soup.find_all('p')

        paragraph_texts = ""
        for paragraph in paragraphs:
            paragraph_texts += paragraph.text
        return paragraph_texts
    except requests.exceptions.ConnectionError as e:
        print("Connection error:", e)
        return "Connection error " + url

from collections import Counter
import re

def summarize(input_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "user",
                "content": f"riassumi il seguente articolo di giornale considerando solo le informazioni chiave più interessanti  {input_text}"
            }
        ],
        temperature=1,
        max_tokens=4010,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    che_ha_detto = response['choices'][0]['message']['content']
    return che_ha_detto

def finale(input_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "user",
                "content": f"riscrivi le seguenti informazioni sotto forma di una panoramica accattivante evidenziando eventuali controversie  {input_text}"
            }
        ],
        temperature=1,
        max_tokens=4010,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    che_ha_detto = response['choices'][0]['message']['content']
    return che_ha_detto

chesidiceoggi = ""
for url in url_list:
    articolo = scraper(url)
    articolo = summarize(articolo)
    chesidiceoggi = chesidiceoggi + articolo

output = finale(chesidiceoggi)
print(output)