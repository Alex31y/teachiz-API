from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions = [
        {
            "category": "Science: Computers",
            "type": "multiple",
            "difficulty": "easy",
            "question": "HTML is what type of language?",
            "correct_answer": "Markup Language",
            "incorrect_answers": [
                "Macro Language",
                "Programming Language",
                "Scripting Language"
            ]
        },
        {
            "category": "Science: Computers",
            "type": "boolean",
            "difficulty": "medium",
            "question": "All program codes have to be compiled into an executable file in order to be run. This file can then be executed on any machine.",
            "correct_answer": "False",
            "incorrect_answers": [
                "True"
            ]
        },
        {
            "category": "Science: Computers",
            "type": "multiple",
            "difficulty": "medium",
            "question": "On which day did the World Wide Web go online?",
            "correct_answer": "December 20, 1990",
            "incorrect_answers": [
                "December 17, 1996",
                "November 12, 1990",
                "November 24, 1995"
            ]
        }
    ]
    return jsonify(questions)


if __name__ == '__main__':
    app.run()
