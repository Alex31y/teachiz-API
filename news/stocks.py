import requests

# Specify the request parameters
params = {
    'q': 'governo OR politica',
    'country': 'it',
    'lang': 'it',
    'token': '7d01d9ab1dfab08f5b50bec4d7cd0f4b',  # Replace with your GNews API key
}

# GNews API endpoint
url = 'https://gnews.io/api/v4/search'

# Execute the HTTP request to get the article data
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    # Check if there are articles available
    articles = data.get('articles', [])
    if articles:
        for article in articles[:100]:  # Get the first 10 articles
            title = article['title']
            source = article['source']['name']
            url = article['url']
            print(f"Title: {title}")
            print(f"Source: {source}")
            print(f"URL: {url}")
            print("-----------------------")
    else:
        print("No articles found.")
else:
    print(f"Request error: {response.status_code}")
    print(response.content)
