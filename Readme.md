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

**_The guess function would contain the logic to guess a letter_**


# **_Intelligent Guessing Logic_**

In this implementation of the Hangman game, an intelligent guessing strategy has been developed to enhance the accuracy of letter guesses and improve the overall success rate. The strategy combines various factors to make informed decisions on which letters to guess.

## Approach Overview:

#### Frequency Count and Probability:

The initial step involved analyzing the frequency count of letters in the provided word dictionary. Unique letters in each word were considered to remove repetition bias.
This frequency count was used to calculate the probability distribution of each letter occurring in the words.

#### Letter Position-Based Strategy:

A letter position-based strategy was introduced to factor in the probability of a letter occurring at a specific position in the word.
This approach improves guess accuracy by considering the likelihood of a letter's placement.

#### Intelligent Guess Selection:

The final guess is a result of combining probabilities from multiple sources:
Overall frequency distribution of letters in the dictionary.
Probability of the letter appearing at a specific position.
Probability based on the word length.
Probability based on pattern matching with known letters.
The combined probabilities guide the selection of the next letter to guess, aiming for the highest probability of success.

Key Components:
_unique_letter_count(words_dict):_ Calculates the frequency distribution of unique letters in the word dictionary.
_word_length_dict(words_list)_: Creates a dictionary of words based on their length.
_length_wise_dict(all_words)_: Generates a frequency distribution of letters based on word length.
_calculate_prob(letter_freq_dict)_: Calculates the probability distribution of letters based on their frequency.
_fill_missing_prob(letter_freq_dict)_: Fills missing probabilities with zero for all letters.
_guess(word)_: The core guess function that implements the intelligent guessing strategy.

#### Pattern Matching (Work in Progress):

The implementation is ongoing and aims to further optimize the guessing strategy using pattern matching. Identifying patterns within words can contribute to even more accurate guesses, reducing the number of incorrect attempts.

## Usage and Experimentation:

Feel free to explore and modify the implemented code to experiment with different strategies, enhance the success rates, and create an engaging Hangman gameplay experience. The combined efforts of intelligent guessing, probability calculations, and pattern matching contribute to a challenging and enjoyable game.

