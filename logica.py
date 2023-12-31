import re
import openai
from bs4 import BeautifulSoup
import requests
import wikipedia
from googlesearch import search
import json

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


def LMnotes(query, context, lang):
    # print("Input - Topic:", topic)
    # print("Input - Context:", context)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "system",
                "content": f"""I am learning about {query}. Teach me using the provided information in the language: {lang}"""
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


def LMquery(query, context, lang):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
        "role": "system",
        "content": f"I am learning about {query} all i know is the provided text. Give me a string list of 10 queries separed by - character by which i can continue my research in the language: {lang}"
        },
        {
        "role": "user",
        "content": f"{context}"
        }
    ],
    temperature=1,
    max_tokens=255,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    #print(f"Spesa totale:  {quanto_pago(response)}")
    che_ha_detto = response['choices'][0]['message']['content']
    #print("Response: ", che_ha_detto)
    return che_ha_detto


def LMexplain(question, context):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
        "role": "user",
        "content": f"answer this question and explain the reasoning: {question} Given this context: {context}"
        }
    ],
    temperature=1,
    max_tokens=1024,
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


def get_urls(query, lang):
    urls = search(query, lang=lang)
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


def web_to_text(query, lang):
    urls = list(get_urls(query, lang))  # Convert the generator object to a list
    wall_of_text = ""
    counter = 0
    while len(wall_of_text) < 5000:  # Add this condition to check the length of "wall_of_text"
        if counter >= len(urls):
            break
        url = urls[counter]
        wall_of_text += scraper(url)
        counter += 1
    text = clean_text(wall_of_text)
    text = LMnotes(query, text, lang)
    return text


def wiki_to_text(query, lang="it", original_query=None, attempt=1):
    try:
        wikipedia.set_lang(lang)
        page = wikipedia.page(query)
        text = clean_text(page.content)
        text = text[:15000]
        text = LMnotes(query, text, lang)
        return query, text  # Return the extracted text and the original query
    except wikipedia.exceptions.DisambiguationError as e:
        if attempt <= 3 and len(e.options) > 1:
            first_option = e.options[0]
            print(f"Ambiguous term '{query}'. Using option: {first_option}")
            return first_option, wiki_to_text(first_option, lang, original_query=query, attempt=attempt + 1)
        else:
            print(f"Unable to determine the correct option for '{query}', cerco su google")
            return query, web_to_text(original_query, lang)
    except wikipedia.exceptions.PageError:
        print("Not found in Wikipedia")
        return query, web_to_text(original_query, lang)



def json_validator(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False