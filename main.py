import json
import os
import re
import openai
from bs4 import BeautifulSoup
import requests
import wikipedia
from googlesearch import search
from flask import Flask, jsonify, request, send_from_directory

prompt_tokens_price = 0.0015 / 1000
completion_tokens_price = 0.002 / 1000
costo_complessivo = 0

openai.api_key = "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"


def quanto_pago(response):
    completion_tokens = response['usage']['completion_tokens']
    prompt_tokens = response['usage']['prompt_tokens']
    completion_price = completion_tokens * completion_tokens_price
    prompt_price = prompt_tokens * prompt_tokens_price
    price = completion_price + prompt_price
    #print("completion_price: " + str(completion_price))
    #print("prompt_price: " + str(prompt_price))
    #print("costo chiamata: " + str(price))
    total_tokens = response['usage']['total_tokens']
    # print(total_tokens)
    global costo_complessivo
    costo_complessivo = costo_complessivo + price
    # print("\n\nCosto sessione: " + str(costo_complessivo))
    return costo_complessivo


def LMQuiz(topic, context, num, lang):
    # print("Input - Topic:", topic)
    # print("Input - Context:", context)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"""generate {num} questions about {topic} in language: {lang} using the information in the given text. All of your output must be JSON-formatted. Follow this example [{{"question":"HTML is what type of language?","correct_answer":"Markup Language","incorrect_answers":["Macro Language","Programming Language","Scripting Language"]}},{{"question":"All program codes have to be compiled into an executable file in order to be run. This file can then be executed on any machine.","correct_answer":"False","incorrect_answers":["True"]}}]"""
            },
            {
                "role": "user",
                "content": f"{context}"
            }
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    print(f"Spesa totale:  {quanto_pago(response)}")
    che_ha_detto = response['choices'][0]['message']['content']
    print("Response: ", che_ha_detto)
    return che_ha_detto, quanto_pago(response)


def clean_text(input_text):
    text = ""

    for char in input_text:
        try:
            char.encode('utf-8')
            text += char
        except UnicodeEncodeError:
            pass

    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text


def text_to_chunks(text, chunk_size=4000, overlap_percentage=0):
    chunks = []
    overlap_size = int(chunk_size * overlap_percentage)
    start = 0
    end = chunk_size

    while start < len(text):
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap_size
        end = start + chunk_size
    return chunks


def get_urls(query):
    urls = search(query)
    return urls


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


def web_to_text(query):
    urls = list(get_urls(query))  # Convert the generator object to a list
    wall_of_text = ""
    counter = 0
    while len(wall_of_text) < 5000:  # Add this condition to check the length of "wall_of_text"
        if counter >= len(urls):
            break
        url = urls[counter]
        wall_of_text += scraper(url)
        counter += 1
    text = clean_text(wall_of_text)
    return text


def wiki_to_text(query, lang="it"):
    try:
        wikipedia.set_lang(lang)
        pagina = wikipedia.page(query)
        text = clean_text(pagina.content)
        return text
    except wikipedia.exceptions.PageError:
        print("Not found in wikipedia")
        return web_to_text(query)


def json_validator(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False


app = Flask(__name__)


@app.route('/')
def home():
    return "Sgnack"

# http://localhost:5000/api/questions?query=Apprendimento%20automatico&lang=it&num=5
@app.route('/api/questions', methods=['GET'])
def get_questions():
    # Accessing query parameters from the request.args dictionary
    query = request.args.get('query', default='', type=str)
    num = request.args.get('num', default=5, type=int)
    lang = request.args.get('lang', default='en', type=str)
    context = wiki_to_text(query, lang)

    if context == "not found":
        return context

    chunks = text_to_chunks(context)
    context = chunks[0]
    iteration_count = 0
    json_string = ""
    while not json_validator(json_string):
        json_string, prezzo = LMQuiz(query, context, num, lang)
        if not json_validator(json_string):
            print("Error in JSON")
            # You can add a delay or other actions here if needed

        iteration_count += 1

    data = json.loads(json_string)

    response = {
        "response_code": 0,
        "price": prezzo,
        "total_iterations": iteration_count,
        "results": data
    }
    # Create a dictionary with ensure_ascii=False to preserve non-ASCII characters in the JSON
    response_json = json.dumps(response, ensure_ascii=False)

    return app.response_class(response=response_json, content_type='application/json')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
