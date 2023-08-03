# Hangman Game API

Hangman Game API is a simple server-side API built with Flask and SQLite that allows clients to play the Hangman word guessing game. The server-side API handles starting a new game, making letter guesses, and providing game status.

## Prerequisites

- Python 3.x
- Flask (Install using `pip install Flask`)

## Server-Side Usage

1. Clone the repository and navigate to the `server` directory.

2. Start the server by running the following command:


The server will run on http://127.0.0.1:5000 by default.

API Endpoints
------------------
Start a New Game
Endpoint: /new_game
Method: POST

Make a Letter Guess
Endpoint: /guess_letter
Method: POST

Get Game Status
Endpoint: /my_status
Method: GET


Client-Side Usage
------------------

The guess function would contain the logic to guess a letter

