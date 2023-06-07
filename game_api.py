# from flask import Flask
# import random
# app = Flask(__name__)

dictionary_file_location = 'words_250000_train.txt'
game_db = {}

# import sqlite3

# # create a connection

# # insert data into a table
# c.execute("INSERT INTO students VALUES ('mark', 20, 1.9)")

# all_students = [
#     ('john', 21, 1.8),
#     ('david', 35, 1.7),
#     ('michael', 19, 1.83),
# ]
# c.executemany("INSERT INTO students VALUES (?, ?, ?)", all_students)

# # select data
# c.execute("SELECT * FROM students")
# print(c.fetchall())

# # commit
# conn.commit()

# # close the connection
# conn.close()
import random
import sqlite3

table_name = "game"
class hangman_game():
    def __init__(self) -> None:
          self.actual_word = None
          self.curr_word = None
          self.game_id = None
          self.tries_remaining = 6
          self.word_dict = self.build_dictionary(dictionary_file_location)
          global table_name

    def _init_db(self,):
        conn = sqlite3.connect('game.db',isolation_level=None)
        self.c = conn.cursor()  # cursor
        # listOfTables = self.c.execute(
        # """SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';).fetchall()
        
        # if listOfTables == []:
            # create a table
        self.c.execute("""CREATE TABLE if not exists """+table_name+""" (
                    game_id INTEGER,
                    tries_remaining INTEGER,
                    curr_word TEXT,
                    actual_word TEXT
            )""")
        
    def insert_data(self,):
         status = 'approved'
         print (table_name,self.game_id,self.actual_word,self.tries_remaining,''.join(self.curr_word))
         print ("INSERT INTO "+table_name+"  (game_id, tries_remaining, curr_word, actual_word) VALUES (%d,%d,'%s','%s')" % (self.game_id,self.tries_remaining,self.curr_word,self.actual_word))
         self.c.execute("INSERT INTO "+table_name+"  (game_id, tries_remaining, curr_word, actual_word) VALUES (%d,%d,'%s','%s')" % (self.game_id,self.tries_remaining,self.curr_word,self.actual_word))

    def build_dictionary(self,dictionary_file_location):
        text_file = open(dictionary_file_location,"r")
        full_dictionary = text_file.read().splitlines()
        text_file.close()
        return full_dictionary
    
    # @app.route('/new_game')
    def new_game(self,):        
        self.actual_word = random.choice(self.word_dict)
        self.curr_word = ''.join(['_'] * len(self.actual_word))
        # print (self.c.execute("select max(game_id) from ?"))
        self.game_id = self.c.execute("select max(game_id) from "+ table_name).fetchone()[0]
        print("Congratulations..................new game id is ",self.game_id)
        if self.game_id:
            return {'status':'approved','game_id':self.game_id + 1,'word':self.curr_word,'tries_remains':6}
        else:
             self.game_id = 0
             return {'status':'approved','game_id':self.game_id,'word':self.curr_word,'tries_remains':6}

    def guess_letter(self,game_info):
        game_id = game_info['game_id']
        guess_letter = game_info["letter"]
        if guess_letter not in self.actual_word:
             self.tries_remaining = self.tries_remaining - 1
        if self.tries_remaining > 6:
                return {'tries_remain':self.tries_remaining,'status':'failed'}
        elif self.tries_remaining == 0:
                return {'tries_remain':self.tries_remaining,'status':'success'}
        else:
                for c,i in enumerate(self.actual_word):
                    if c == guess_letter:
                            self.curr_word[i] = guess_letter
                return{'tries_remain':self.tries_remaining,'status':'ongoing','word':self.curr_word}
    #   {"game_id":game_id, "letter":guess_letter}

obj = hangman_game()
obj._init_db()
obj.new_game()
print("game id is ",obj.game_id)
obj.insert_data()
print (obj.guess_letter({"game_id":0, "letter":'a'}))
print (obj.c.execute("select * from game").fetchall())
