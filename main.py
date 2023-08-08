import json
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import logica
import logicaNews
import question as qw
import note
import db
import threading

app = Flask(__name__)


@app.route('/')
@cross_origin()
def home():
    return "Sgnack"


# http://localhost:5000/api/note?query=Apprendimento%20automatico&lang=it
@app.route('/api/note', methods=['GET'])
@cross_origin()
def genera_note():
    # Accessing query parameters from the request.args dictionary
    query = request.args.get('query', default='', type=str)
    lang = request.args.get('lang', default='en', type=str)
    notes = db.get_note(query, lang)
    if notes != "Empty":
        return notes

    query, context = logica.wiki_to_text(query, lang)
    context = context[:20000]
    notes, prezzo = logica.LMnotes(query, context, lang)
    # queries = logica.LMquery(query, notes, lang)
    # add to db
    new_note = note.Note()
    new_note.set_query(query)
    new_note.set_text(context)
    new_note.set_lang(lang)
    # new_note.set_related_query(queries)
    new_note.set_pop(1)
    db.set_note(new_note)
    # Create a dictionary with ensure_ascii=False to preserve non-ASCII characters in the JSON
    background_thread = threading.Thread(target=genera_domande(query, lang, notes))
    background_thread.start()

    notes = db.get_note(query, lang)
    return notes


def genera_domande(query, lang, context):
    iteration_count = 0
    json_string = ""
    while not logica.json_validator(json_string):
        json_string, prezzo = logica.LMQuiz(query, context, 10, lang)
        if not logica.json_validator(json_string):
            print("Error in JSON")
        iteration_count += 1

    data = json.loads(json_string)
    # Create a list to hold the Question instances
    question_objects = []

    # add to db
    # Loop through the data and create Question instances
    for question_data in data:
        new_qw = qw.Question()
        new_qw.set_query(query)
        new_qw.set_question(question_data['question'])
        new_qw.set_wrong_answ(question_data['incorrect_answers'])
        new_qw.set_corct_answ(question_data['correct_answer'])
        new_qw.set_lang(lang)
        question_objects.append(new_qw)

    # Call the set_questions method with the list of Question instances
    db.set_questions(question_objects)


from bing_image_urls import bing_image_urls


@app.route('/api/qetimage', methods=['GET'])
@cross_origin()
def get_image():
    query = request.args.get('query', default='', type=str)
    url = bing_image_urls(query, limit=1)[0]
    return url


@app.route('/api/qwtfromquery', methods=['GET'])
@cross_origin()
def get_qwt_from_query():
    query = request.args.get('query', default='', type=str)
    lang = request.args.get('lang', default='en', type=str)
    domande = db.get_qwt_from_query(query, lang)

    response = {
        "response_code": 0,
        "results": domande
    }
    # Create a dictionary with ensure_ascii=False to preserve non-ASCII characters in the JSON
    response_json = json.dumps(response, ensure_ascii=False)

    return app.response_class(response=response_json, content_type='application/json')


@app.route('/api/allquestions', methods=['GET'])
@cross_origin()
def get_all_questions():
    lang = request.args.get('lang', default='en', type=str)
    domande = db.get_questions(lang)

    response = {
        "response_code": 0,
        "results": domande
    }
    # Create a dictionary with ensure_ascii=False to preserve non-ASCII characters in the JSON
    response_json = json.dumps(response, ensure_ascii=False)

    return app.response_class(response=response_json, content_type='application/json')


@app.route('/api/allqueries', methods=['GET'])
@cross_origin()
def get_all_queries():
    lang = request.args.get('lang', default='en', type=str)
    queries = db.get_allqueries(lang)
    print("fmain row 118 queries is of type:", type(queries))

    # If the 'queries' list is not empty, create a response dictionary
    if queries:
        response = {
            "response_code": 0,
            "results": queries  # Use 'results' instead of 'queries'
        }
    else:
        response = {
            "response_code": 1,
            "message": "Empty"
        }

    # Create a JSON response directly from the response dictionary
    return app.response_class(response=json.dumps(response, ensure_ascii=False), content_type='application/json')


from datetime import datetime, timedelta

# Get today's date
today = datetime.now().date()
yesterday = today - timedelta(days=1)
# Format the date as "YYYY-MM-DD"
yesterday = yesterday.strftime("%Y-%m-%d")


# http://127.0.0.1:5000/api/getnews?giornale=ilpost.it&data=2023-08-02&depth=10
# "repubblica.it", "2023-08-06"
# ilpost.it
@app.route('/api/getnews', methods=['GET'])
@cross_origin()
def get_news():
    giornale = request.args.get('giornale', default='ilpost.it', type=str)
    data = request.args.get('data', default=yesterday, type=str)
    depth = request.args.get('depth', default=10, type=str)
    #print(giornale + " " + data)
    content = logicaNews.get_content(giornale, data, depth)
    #print(content)
    return content


if __name__ == '__main__':
    app.run()
