import json
import re
import openai
import spacy
import wikipedia
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

    # Extract the most significant sentences based on a significance factor (adjust as needed)
    significance_factor = 0.6  # Adjust this value to control the summary length
    total_sentences = len(ranked_sentences)
    num_sentences = 0
    accumulated_score = 0
    for i in range(total_sentences):
        accumulated_score += ranked_sentences[i][0]
        num_sentences += 1
        if accumulated_score >= significance_factor * sentence_scores.sum():
            break

    selected_sentences = sorted([index for _, index in ranked_sentences[:num_sentences]])

    sentences = [preprocessed_sentences[index] for index in selected_sentences]

    # Combine selected sentences into the summary
    summary = " ".join([" ".join(sentence) for sentence in sentences])

    # Limit summary to a maximum of 6000 characters
    max_characters = 6000
    if len(summary) > max_characters:
        summary = summary[:max_characters]

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


def wiki_to_text(query, lang="it"):
    try:
        wikipedia.set_lang(lang)
        pagina = wikipedia.page(query)
        text = clean_text(pagina.content)
        riassunto = summarize_text(text)
        return riassunto
    except wikipedia.exceptions.PageError:
        print("Page not found. Please try another query.")
        return "not found"

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
    context = wiki_to_text(input)
    if(context == "not found"):
        return context
    chunks = text_to_chunks(context)
    context = chunks[0]

    json_string = ""
    while not json_validator(json_string):
        json_string = LMQuiz(input, context)
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
