import json
import requests
import random
import string
import secrets
import time
import re
import collections

# Server-side API URL
HANGMAN_URL = "http://127.0.0.1:5000"


class HangmanAPI(object):
    def __init__(self, access_token=None, session=None, timeout=None):
        self.access_token = access_token
        self.session = session or requests.Session()
        self.timeout = timeout
        self.guessed_letters = []
        self.full_dictionary = self.build_dictionary("data/words.txt")
        self.full_dictionary_common_letter_sorted = collections.Counter("".join(self.full_dictionary)).most_common()
        self.current_dictionary = []

        self.word_length_dictionary = self.word_length_dict(self.full_dictionary)
        self.wrong_guess = set()

        self.all_prob = self.calculate_prob(self.unique_letter_count(self.full_dictionary))

        self.length_wise_dictionary = self.length_wise_dict(self.full_dictionary)
        # self.letter_pos_dictionary = {}
        self.pos_filled = []

        # self.probability_letter = defaultdict(lambda: defaultdict(int))

    # Function to ccalculte the frequency dictionary from the list of words given- unique letter in each word
    def unique_letter_count(self, words_dict):
        return dict(collections.Counter(''.join([''.join(set(d)) for d in words_dict])).most_common())

    # Function to create a dict of words based on the word length from the list of words given
    def word_length_dict(self, words_list):
        w_d = {}
        for word in words_list:
            key = len(word)
            w_d[key] = w_d.get(key, []) + [word]
        return (w_d)

    # Function to create the frequency ditribution of letters based on length from the list of words given
    def length_wise_dict(self, all_words):
        length_wise_count = {}
        word_len_dict = self.word_length_dict(all_words)
        for lengths in word_len_dict:
            length_wise_count[lengths] = self.unique_letter_count(word_len_dict[lengths])
        return length_wise_count

    # Function to calculate the frequency distribution based on the letter position from the list of words given
    def letter_pos_dict(self, words):
        letter_pos_dictionary = collections.defaultdict(lambda: collections.defaultdict(int))
        for word in words:
            for position, letter in enumerate(word):
                letter_pos_dictionary[position][letter] += 1
        return letter_pos_dictionary

    # function to calculate the probability of the given dictionary
    def calculate_prob(self, letter_freq_dict):
        total = sum(letter_freq_dict.values())
        prob_dict = {}
        for letter, freq in letter_freq_dict.items():
            prob_dict[letter] = freq / total
        return self.sort_dictionary(prob_dict)

    # function to return a sorted dictionry
    def sort_dictionary(self, diction):
        return dict(sorted(diction.items(), key=lambda x: x[1], reverse=True))

    # function to add missing probailities as 0
    def fill_missing_prob(self, letter_freq_dict):
        filled_dict = {letter: letter_freq_dict.get(letter, 0) for letter in 'abcdefghijklmnopqrstuvwxyz'}
        return filled_dict

    def build_dictionary(self,dictionary_file_location):
        text_file = open(dictionary_file_location, "r")
        full_dictionary = text_file.read().splitlines()
        text_file.close()
        return full_dictionary

    def guess(self, word):
        ###############################################
        # Replace with your own "guess" function here #
        ###############################################

        # clean the word so that we strip away the space characters
        # replace "_" with "." as "." indicates any character in regular expressions
        # print ("word:",word)
        clean_word = word[::2].replace("_", ".")
        self.pos_filled_dict = {char: index for index, char in enumerate(word) if char != '.'}
        # print ("word:",clean_word)
        # time.sleep(5)
        # find length of passed word
        len_word = len(clean_word)
        for gl in self.guessed_letters:
            if gl not in clean_word:
                self.wrong_guess.add(gl)
        if len(self.pos_filled) == 0:
            self.pos_filled = [False] * len_word
        for i, letter in enumerate(clean_word):
            if letter != '.':
                self.pos_filled[i] = True

        guess_letter = '!'
        # grab current dictionary of possible words from self object, initialize new possible words dictionary to empty
        if len(self.current_dictionary) < 1:
            self.current_dictionary = self.word_length_dictionary[len_word]
        new_dictionary = []

        # to check if this improves the efficency as any pattern irrespctive of the length would be checked now
        if len(self.wrong_guess) >= 3:
            self.current_dictionary = self.full_dictionary
        #####--------------filtering of the words

        for dict_word in self.current_dictionary:
            if re.match(clean_word, dict_word):
                if not self.wrong_guess.intersection(set(dict_word)):
                    new_dictionary.append(dict_word)

        # iterate through all of the words in the old plausible dictionary
        '''for dict_word in current_dictionary:
            # continue if the word is not of the appropriate length
            if len(dict_word) != len_word:
                continue

            print ("dict_word",dict_word)
            # if dictionary word is a possible match then add it to the current dictionary
            if re.match(clean_word,dict_word):
                print ("matched",clean_word,dict_word)
                new_dictionary.append(dict_word)
        '''
        # overwrite old possible words dictionary with updated version
        self.current_dictionary = new_dictionary
        print(new_dictionary)
        curr_prob = self.calculate_prob(self.unique_letter_count(new_dictionary))
        len_prob = self.calculate_prob(self.length_wise_dictionary[len_word])
        ###----------This part is to check for the letter position probability
        unfilled = len_word - sum(self.pos_filled)
        weight = 100 / unfilled
        pos_prob = {}
        pos_dict = {}
        if len(self.wrong_guess) >= 3:
            for pos, status in enumerate(self.pos_filled):
                if not status:
                    pos_dict[pos] = self.calculate_prob(
                        self.letter_pos_dict(self.length_wise_dictionary[len_word])[pos])
                    pos_dict[pos].update((x, y * weight) for x, y in pos_dict[pos].items())
            for dicts in pos_dict.values():
                pos_prob = collections.Counter(pos_prob) + collections.Counter(dicts)
            pos_dict = dict(pos_dict)

        # just to ensure all the keys are there in all the dictionaries
        pos_prob = self.fill_missing_prob(pos_prob)
        curr_prob = self.fill_missing_prob(curr_prob)
        len_prob = self.fill_missing_prob(len_prob)
        ##----------------------------------------------------------------------
        ######Calculation of combined probabilities of the current dictionary, full dictionarya and length probability

        final_prob_dict = {}
        for letter in self.all_prob:
            if letter in self.wrong_guess:
                final_prob_dict[letter] = 0
            else:
                if unfilled <= 2:
                    if curr_prob[letter] > 0:
                        final_prob_dict[letter] = (self.all_prob[letter] * 0.05) + (curr_prob[letter] * 0.4) + (
                                    len_prob[letter] * 0.05) + (pos_prob[letter] * 0.5)
                    else:
                        final_prob_dict[letter] = (self.all_prob[letter] * 0.25) + (curr_prob[letter] * 0) + (
                                    len_prob[letter] * 0.25) + (pos_prob[letter] * 0.5)
                else:
                    wrong_guess_cnt = len(self.wrong_guess)
                    if wrong_guess_cnt <= 2:
                        final_prob_dict[letter] = (self.all_prob[letter] * 0.05) + (curr_prob[letter] * 0.6) + (
                                    len_prob[letter] * 0.25) + (pos_prob[letter] * 0.1)
                    elif wrong_guess_cnt == 3:
                        final_prob_dict[letter] = (self.all_prob[letter] * 0.1) + (curr_prob[letter] * 0.3) + (
                                    len_prob[letter] * 0.3) + (pos_prob[letter] * 0.3)
                    elif wrong_guess_cnt == 4:
                        final_prob_dict[letter] = (self.all_prob[letter] * 0.2) + (curr_prob[letter] * 0.2) + (
                                    len_prob[letter] * 0.35) + (pos_prob[letter] * 0.5)
                    elif wrong_guess_cnt >= 5:
                        final_prob_dict[letter] = (self.all_prob[letter] * 0.2) + (curr_prob[letter] * 0.1) + (
                                    len_prob[letter] * 0.3) + (pos_prob[letter] * 0.4)

        final_prob_dict_sorted = self.sort_dictionary(final_prob_dict)
        print(final_prob_dict_sorted)
        ##-----------------------------------------------------------------------

        if guess_letter == '!':
            # calculate unique letter count
            for letter in final_prob_dict_sorted:
                if letter not in self.guessed_letters and letter not in clean_word:
                    guess_letter = letter
                    break
        # return most frequently occurring letter in all possible words that hasn't been guessed yet
        # If no word matces in the training dict, we can check for most common letter in 5 letter word
        if guess_letter == '!':
            for letter in self.unique_letter_count(self.word_length_dictionary[len_word]):
                if letter not in self.guessed_letters and letter not in clean_word and letter not in self.wrong_guess:
                    guess_letter = letter
        # if there is still no match we can go for the full unique dict count:
        if guess_letter == '!':
            for letter in self.unique_letter_count(self.full_dictionary):
                if letter not in self.guessed_letters and letter not in clean_word and letter not in self.wrong_guess:
                    guess_letter = letter
        # if no word matches in training dictionary, default back to ordering of full dictionary
        if guess_letter == '!':
            sorted_letter_count = self.full_dictionary_common_letter_sorted
            for letter, instance_count in sorted_letter_count:
                if letter not in self.guessed_letters and letter not in clean_word and letter not in self.wrong_guess:
                    guess_letter = letter
                    break
        return guess_letter

    def start_game(self, practice=True, verbose=True):
        # reset guessed letters to empty set and current plausible dictionary to the full dictionary
        self.guessed_letters = []
        self.current_dictionary = self.full_dictionary

        data = {"practice": practice}
        response = self.request("/new_game", data=data)

        if response.get('status') == "approved":
            game_id = response.get('game_id')
            word = response.get('word')
            tries_remains = response.get('tries_remains')
            if verbose:
                print(
                    "Successfully start a new game! Game ID: {0}. # of tries remaining: {1}. Word: {2}.".format(game_id,
                                                                                                                tries_remains,
                                                                                                                word))

            while tries_remains > 0:
                # get guessed letter from user code
                guess_letter = self.guess(word)

                # append guessed letter to guessed letters field in hangman object
                self.guessed_letters.append(guess_letter)
                if verbose:
                    print("Guessing letter: {0}".format(guess_letter))

                data = {"game_id": game_id, "letter": guess_letter}
                try:
                    res = self.request("/guess_letter", data=data)
                except HangmanAPIError:
                    print('HangmanAPIError exception caught on request.')
                    continue
                except Exception as e:
                    print('Other exception caught on request.')
                    raise e

                if verbose:
                    print("Server response: {0}".format(res))
                status = res.get('status')
                tries_remains = res.get('tries_remains')
                if status == "success":
                    if verbose:
                        print("Successfully finished game: {0}".format(game_id))
                    return True
                elif status == "failed":
                    reason = res.get('reason', '# of tries exceeded!')
                    if verbose:
                        print("Failed game: {0}. Because of: {1}".format(game_id, reason))
                    return False
                elif status == "ongoing":
                    word = res.get('word')
        else:
            if verbose:
                print("Failed to start a new game")
        return status == "success"

    def request(self, path, data=None):
        url = HANGMAN_URL + path
        headers = {'Content-Type': 'application/json'}
        if self.access_token:
            headers['Authorization'] = 'Bearer ' + self.access_token

        response = self.session.post(url, json=data, headers=headers, timeout=self.timeout, verify=False)
        response.raise_for_status()
        return response.json()

    def my_status(self):
        # Make a GET request to the /my_status endpoint
        url = HANGMAN_URL + "/my_status"
        headers = {'Content-Type': 'application/json'}
        if self.access_token:
            headers['Authorization'] = 'Bearer ' + self.access_token

        response = self.session.get(url, headers=headers, timeout=self.timeout, verify=False)
        response.raise_for_status()
        return response.json()


class HangmanAPIError(Exception):
    def __init__(self, result):
        self.result = result
        self.code = None
        try:
            self.type = result["error_code"]
        except (KeyError, TypeError):
            self.type = ""

        try:
            self.message = result["error_description"]
        except (KeyError, TypeError):
            try:
                self.message = result["error"]["message"]
                self.code = result["error"].get("code")
                if not self.type:
                    self.type = result["error"].get("type", "")
            except (KeyError, TypeError):
                try:
                    self.message = result["error_msg"]
                except (KeyError, TypeError):
                    self.message = result

        Exception.__init__(self, self.message)


api = HangmanAPI()

# The rest of the client-side code remains unchanged.
# ... (rest of the client-side code here) ...
api.start_game(practice=1,verbose=True)
[total_practice_runs,total_recorded_runs,total_recorded_successes,total_practice_successes] = api.my_status().values() # Get my game stats: (# of tries, # of wins)
print(api.my_status())
print ([total_practice_runs,total_recorded_runs,total_recorded_successes,total_practice_successes])
practice_success_rate = total_practice_successes / total_practice_runs
print('run %d practice games out of an allotted 100,000. practice success rate so far = %.3f' % (total_practice_runs, practice_success_rate))

