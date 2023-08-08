import json
import requests

# Sostituisci 'API_KEY' con la tua chiave API ottenuta da News API
API_KEY = 'c85e1ca77cc0492c879ad5670c7e692f'

def get_articoli_newsapi(giornale, giorno):
    base_url = 'https://newsapi.org/v2/everything'

    # Specify the request parameters
    # Here, I am searching for articles related to politics in Italy from Italian sources

    params = {
        'apiKey': API_KEY,
        'domains': giornale,
        'from': giorno,
        'to': giorno,
        'pageSize': 100,
    }
    """
    params = {
        'apiKey': API_KEY,
        'q': 'politica',
        'language': 'it',
        'sortBy': 'publishedAt',  # Sort by relevance
        'pageSize': 100,
    }
    
    
    base_url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'apiKey': API_KEY,
        'country': 'it',
        'category': 'business&general&health&science&technology',
        'pageSize': 100,
    }
    """
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

                #dizionario o mappa? boh
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

    file_name = "articoli " + giornale + " " + giorno + ".json"
    # Open the file in write mode
    with open(file_name, "w", encoding="utf-8") as json_file:
        json.dump(articoloMap, json_file, indent=4, ensure_ascii=False)

    formatted_json = json.dumps(articoloMap, indent=4)

    return formatted_json


# domains: 'ilpost.it', 'repubblica.it'
# data '2023-08-07'
get_articoli_newsapi("ilpost.it", "2023-08-07")