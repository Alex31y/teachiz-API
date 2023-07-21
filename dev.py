import json
import re
from bs4 import BeautifulSoup
import requests
from googlesearch import search
import openai
import spacy
import spacy.cli
spacy.cli.download("en_core_web_sm")
from flask import Flask, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer

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
    # print("completion_price: " + str(completion_price))
    # print("prompt_price: " + str(prompt_price))
    # print("costo chiamata: " + str(price))
    total_tokens = response['usage']['total_tokens']
    # print(total_tokens)
    global costo_complessivo
    costo_complessivo = costo_complessivo + price
    # print("\n\nCosto sessione: " + str(costo_complessivo))
    return costo_complessivo


def preprocess_text(text):
    nlp = spacy.load('en_core_web_sm')
    sentences = list(nlp(text).sents)

    preprocessed_sentences = []
    for sentence in sentences:
        sentence_tokens = [token.lemma_.lower() for token in sentence if
                           not token.is_punct and not nlp.vocab[token.text.lower()].is_stop]
        preprocessed_sentences.append(sentence_tokens)

    return preprocessed_sentences


def summarize_text(text):
    preprocessed_sentences = preprocess_text(text)
    cleaned_sentences = [" ".join(sentence) for sentence in preprocessed_sentences]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cleaned_sentences)

    sentence_scores = tfidf_matrix.sum(axis=1)

    ranked_sentences = sorted(((score, index) for index, score in enumerate(sentence_scores)), reverse=True)

    num_sentences = min(len(ranked_sentences), int(len(text) / 1000))
    selected_sentences = sorted([index for _, index in ranked_sentences[:num_sentences]])

    sentences = [preprocessed_sentences[index] for index in selected_sentences]

    summary = " ".join([" ".join(sentence) for sentence in sentences])

    return summary


def LMQuiz(topic, context):
    print("Input - Topic:", topic)
    print("Input - Context:", context)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"""generate 10 questions about {topic} using the information in the given text. Put the questions into a JSON like this example [{{"question":"HTML is what type of language?","correct_answer":"Markup Language","incorrect_answers":["Macro Language","Programming Language","Scripting Language"]}},{{"question":"All program codes have to be compiled into an executable file in order to be run. This file can then be executed on any machine.","correct_answer":"False","incorrect_answers":["True"]}}]"""
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
    return che_ha_detto


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


def text_to_chunks(text, chunk_size = 4000, overlap_percentage=0):
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
    urls = get_urls(query)
    wall_of_text = ""
    counter = 0
    for url in urls:
        wall_of_text += scraper(url)
        counter += 1
        if counter == 10:
            break
    text = clean_text(wall_of_text)
    riassunto = summarize_text(text)
    return riassunto


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


@app.route('/api/questions/<input>', methods=['GET'])
def get_questions(input):
    query = input
    context = web_to_text(query)
    chunks = text_to_chunks(context)
    context = chunks[0]

    json_string = ""
    while not json_validator(json_string):
        json_string = LMQuiz(query, context)
        if not json_validator(json_string):
            print("Error in JSON")
            # You can add a delay or other actions here if needed

    data = json.loads(json_string)

    response = {
        "response_code": 0,
        "results": data
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run()
