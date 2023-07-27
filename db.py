import os
import pymysql
import json
import random
from flask import jsonify

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

def open_connection():
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    try:
        if os.environ.get('GAE_ENV') == 'standard':
            conn = pymysql.connect(user=db_user, password=db_password,
                                   unix_socket=unix_socket, db=db_name,
                                   cursorclass=pymysql.cursors.DictCursor)
            return conn
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
        return None

def get_questions(lang):
    conn = open_connection()
    if not conn:
        return "Error connecting to the database"

    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM questions WHERE LOWER(lang) = %s"
            cursor.execute(sql, (lang.lower(),))
            qwt = cursor.fetchall()
            if qwt:
                random_5_qwt = random.sample(qwt, min(5, len(qwt)))
                got_questions = jsonify(random_5_qwt)
            else:
                got_questions = "Empty"
    except pymysql.Error as e:
        print(f"Error executing SQL query: {e}")
        got_questions = "Error occurred while fetching data"

    conn.close()
    return got_questions

def get_qwt_from_query(query, lang):
    conn = open_connection()
    if not conn:
        return "Error connecting to the database"

    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM questions WHERE LOWER(query) = %s AND LOWER(lang) = %s"
            cursor.execute(sql, (query.lower(), lang.lower()))
            qwt = cursor.fetchall()
            if qwt:
                random_5_qwt = random.sample(qwt, min(5, len(qwt)))
                got_qwt = jsonify(random_5_qwt)
            else:
                got_qwt = "Empty"
    except pymysql.Error as e:
        print(f"Error executing SQL query: {e}")
        got_qwt = "Error occurred while fetching data"

    conn.close()
    return got_qwt

def set_questions(questions):
    conn = open_connection()
    if not conn:
        return "Error connecting to the database"

    try:
        with conn.cursor() as cursor:
            for qw in questions:
                wrong_answ_str = json.dumps(qw.get_wrong_answ())
                corct_answ_str = qw.get_corct_answ()
                sql = 'INSERT INTO questions (query, question, wrong_answ, corct_answ) VALUES (%s, %s, %s, %s)'
                cursor.execute(sql, (qw.get_query(), qw.get_question(), wrong_answ_str, corct_answ_str))

        conn.commit()
    except pymysql.Error as e:
        print(f"Error executing SQL query: {e}")
        conn.rollback()
        return "Error occurred while setting questions"
    finally:
        conn.close()

    return "Questions have been successfully set."


def set_note(note):
    conn = open_connection()
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO note (query, text, related_query) VALUES (%s, %s, %s)', (note.get_query(), note.get_text(), note.get_related_query()))
    conn.commit()
    conn.close()


def get_note(query, lang):
    conn = open_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM note WHERE LOWER(query) = %s AND LOWER(lang) = %s"
        cursor.execute(sql, (query.lower(), lang.lower()))
        qwt = cursor.fetchall()
        if len(qwt) > 0:
            got_notes = jsonify(qwt)
        else:
            got_notes = "Empty"
    conn.close()
    return got_notes

def get_allqueries(lang):
    conn = open_connection()
    with conn.cursor() as cursor:
        sql = "SELECT query FROM note WHERE LOWER(lang) = %s ORDER BY pop"
        cursor.execute(sql, (lang.lower()))
        queries = cursor.fetchall()
        print(queries)
        # Check if the list is empty and handle the response accordingly
        if queries:
            # Return the list of strings
            got_notes = queries
        else:
            # Return a message indicating that the list is empty
            got_notes = "Empty"

    conn.close()
    return got_notes




