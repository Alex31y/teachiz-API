import os
import pymysql
import json
from flask import jsonify

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')


def open_connection():
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    conn = None  # Initialize conn with None
    try:
        if os.environ.get('GAE_ENV') == 'standard':
            conn = pymysql.connect(user=db_user, password=db_password,
                                   unix_socket=unix_socket, db=db_name,
                                   cursorclass=pymysql.cursors.DictCursor
                                   )
    except pymysql.MySQLError as e:
        print(e)

    return conn



def get_questions():
    conn = open_connection()
    with conn.cursor() as cursor:
        result = cursor.execute('SELECT * FROM songs;')
        songs = cursor.fetchall()
        if result > 0:
            got_songs = jsonify(songs)
        else:
            got_songs = 'No Songs in DB'
    conn.close()
    return got_songs


def set_questions(questions):
    conn = open_connection()
    with conn.cursor() as cursor:
        for qw in questions:
            wrong_answ_str = json.dumps(qw.get_wrong_answ())  # Convert list to JSON string
            corct_answ_str = qw.get_corct_answ()  # Assuming this is a single string, no need for conversion
            cursor.execute('INSERT INTO questions (query, question, wrong_answ, corct_answ) VALUES (%s, %s, %s, %s)',
                           (qw.get_query(), qw.get_question(), wrong_answ_str, corct_answ_str))

    conn.commit()
    conn.close()