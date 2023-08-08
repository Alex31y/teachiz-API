import json
import requests
from bs4 import BeautifulSoup
import os
import openai
openai.api_key = "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"
API_KEY = 'c85e1ca77cc0492c879ad5670c7e692f'


def json_validator(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False


def get_articoli_newsapi(giornale, data):
    base_url = 'https://newsapi.org/v2/everything'

    # Specify the request parameters
    # Here, I am searching for articles related to politics in Italy from Italian sources

    params = {
        'apiKey': API_KEY,
        'domains': giornale,
        'from': data,
        'to': data,
        'pageSize': 100,
    }
    # Execute the HTTP request to get the article data
    response = requests.get(base_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Check if there are articles available
        if data['totalResults'] > 0:
            articles = data['articles'][:100]  # Get the first 10 articles
            articoloMap = []
            for article in articles:
                title = article['title']
                source = article['source']['name']
                url = article['url']
                description = article['description']
                content = article['content']
                publishedAt = article['publishedAt']

                # dizionario o mappa? boh
                articoloNodo = {
                    "title": title,
                    "source": source,
                    "url": url,
                    "description": description,
                    "content": content,
                    "publishedAt": publishedAt
                }
                articoloMap.append(articoloNodo)
        else:
            print("No articles found.")
    else:
        print(f"Request error: {response.status_code}")
        print(response.content)

    return articoloMap


# domains: 'ilpost.it', 'repubblica.it'
# data '2023-08-07'

def filtrArticolo(articoli):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-16k",
      messages=[
        {
          "role": "user",
          "content": f"dato il seguente insieme di titoli di giornale, restituiscimi una json contenente esclusivamente l'url degli articoli informativi sulla politica e sul governo in ordine di rilevanza alla politica  {articoli}"
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


def summarize(input_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "user",
                "content": f"riassumi il seguente articolo di giornale stando attento a non tralasciare alcun dettaglio  {input_text}"
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


def get_content(giornale, giorno, depth):
    data = get_articoli_newsapi(giornale,giorno)

    # Extract titles and add them to a list
    title_list = [{"title": item["title"], "url": item["url"]} for item in data]
    url_list = [item["url"] for item in title_list]
    # Print the list of titles
    print("articoli og")
    print(url_list)
    articoli = ""
    while not json_validator(articoli):
        articoli = filtrArticolo(title_list)
        print("ci riprovo")
    print("articoli filtrati ")
    print(articoli)
    data = json.loads(articoli)
     #Estrai gli URL e inseriscili in una lista
    url_list = [article['url'] for article in data['articles']]
    depth = int(depth)
    url_list = url_list[:depth] if depth < len(url_list) else url_list

    chesidiceoggi = ""
    articoli = ""
    for url in url_list:
        articolo = scraper(url)
        articolo = summarize(articolo)
        articoli = articoli + "\n\n new articolo\n\n" + articolo
        chesidiceoggi = chesidiceoggi + articolo

    output = "riassunto <br><br>" + finale(chesidiceoggi) + "<br><br><br>articoli<br>" + articoli
    print(output)
    return output


