import json
from flask import Flask, request, jsonify
import logica
import question as qw
from db import get_questions, set_questions


app = Flask(__name__)


@app.route('/')
def home():
    return "Sgnack"


# http://localhost:5000/api/questions?query=Apprendimento%20automatico&lang=it&num=5
@app.route('/api/questions', methods=['GET'])
def genera_domande():
    # Accessing query parameters from the request.args dictionary
    query = request.args.get('query', default='', type=str)
    num = request.args.get('num', default=5, type=int)
    lang = request.args.get('lang', default='en', type=str)
    context = logica.wiki_to_text(query, lang)

    if context == "not found":
        return context

    chunks = logica.text_to_chunks(context)
    context = chunks[0]
    iteration_count = 0
    json_string = ""
    while not logica.json_validator(json_string):
        json_string, prezzo = logica.LMQuiz(query, context, num, lang)
        if not logica.json_validator(json_string):
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

    # Create a list to hold the Question instances
    question_objects = []

    # Loop through the data and create Question instances
    for question_data in data:
        new_qw = qw.Question()
        new_qw.set_query(query)
        new_qw.set_question(question_data['question'])
        new_qw.set_wrong_answ(question_data['incorrect_answers'])
        new_qw.set_corct_answ(question_data['correct_answer'])
        question_objects.append(new_qw)

    # Call the set_questions method with the list of Question instances
    set_questions(question_objects)

    return app.response_class(response=response_json, content_type='application/json')



if __name__ == '__main__':
    app.run()
