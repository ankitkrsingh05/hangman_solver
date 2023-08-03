import random
import string
import secrets
import sqlite3
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# SQLite database initialization
DATABASE_NAME = 'data/hangman_db.sqlite3'


def initialize_database():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS hangman_games 
                 (game_id TEXT PRIMARY KEY, 
                  word TEXT,
                  tries_remains INTEGER,
                  guessed_letters TEXT)''')
    conn.commit()
    conn.close()


initialize_database()


def build_dictionary(dictionary_file_location):
    text_file = open(dictionary_file_location, "r")
    full_dictionary = text_file.read().splitlines()
    text_file.close()
    return full_dictionary
def update_word(word, guessed_letters):
    updated_word = ""
    for char in word:
        if char == " " or char in guessed_letters:
            updated_word += char
        else:
            updated_word += "_"
    return updated_word


@app.route('/new_game', methods=['POST'])
def new_game():
    data = request.get_json()
    practice = data.get('practice', True)

    game_id = secrets.token_hex(16)
    full_dictionary = build_dictionary("data/words.txt")
    word = random.choice(full_dictionary)
    print ("word is ",word)
    tries_remains = 6  # You can adjust this value as needed

    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO hangman_games (game_id, word, tries_remains, guessed_letters) VALUES (?, ?, ?, ?)",
              (game_id, word, tries_remains, ""))
    conn.commit()
    conn.close()

    updated_word = update_word(word, "")
    response = {
        "status": "approved",
        "game_id": game_id,
        "word": updated_word,
        "tries_remains": tries_remains
    }
    return jsonify(response)


@app.route('/guess_letter', methods=['POST'])
def guess_letter():
    data = request.get_json()
    game_id = data.get('game_id')
    letter = data.get('letter')

    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM hangman_games WHERE game_id=?", (game_id,))
    game_data = c.fetchone()
    conn.close()

    if not game_data:
        return jsonify({"status": "failed", "reason": "Game ID not found."})

    game_id, word, tries_remains, guessed_letters = game_data

    # Update guessed letters
    guessed_letters += letter

    # Update tries_remains based on the correct/incorrect guess
    if letter not in word:
        tries_remains -= 1

    # Update the database with the latest data
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE hangman_games SET tries_remains=?, guessed_letters=? WHERE game_id=?",
              (tries_remains, guessed_letters, game_id))
    conn.commit()
    conn.close()

    updated_word = update_word(word, guessed_letters)

    response = {
        "status": "success" if "_" not in updated_word else "ongoing",
        "word": updated_word,
        "tries_remains": tries_remains
    }
    return jsonify(response)


@app.route('/my_status', methods=['GET'])
def my_status():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM hangman_games WHERE guessed_letters=word")
    total_practice_successes = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM hangman_games")
    total_practice_runs = c.fetchone()[0]
    conn.close()

    # Implement the logic for other statistics if needed

    response = {
        "total_practice_runs": total_practice_runs,
        "total_recorded_runs": total_practice_runs,
        "total_recorded_successes": total_practice_successes,
        "total_practice_successes": total_practice_successes
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run()
