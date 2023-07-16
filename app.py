from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions = [
        {
            "category": "Science: Computers",
            "type": "multiple",
            "difficulty": "medium",
            "question": "Which internet company began life as an online bookstore called 'Cadabra'?",
            "correct_answer": "Amazon",
            "incorrect_answers": [
                "eBay",
                "Overstock",
                "Shopify"
            ]
        },
        {
            "category": "Science: Computers",
            "type": "boolean",
            "difficulty": "medium",
            "question": "The first computer bug was formed by faulty wires.",
            "correct_answer": "False",
            "incorrect_answers": [
                "True"
            ]
        },
        {
            "category": "Science: Computers",
            "type": "multiple",
            "difficulty": "hard",
            "question": "What was the name of the security vulnerability found in Bash in 2014?",
            "correct_answer": "Shellshock",
            "incorrect_answers": [
                "Heartbleed",
                "Bashbug",
                "Stagefright"
            ]
        }
    ]

    response = {
        "response_code": 0,
        "results": questions
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run()
