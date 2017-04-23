import re
import sqlite3
from collections import Counter
from string import punctuation
from math import sqrt
import os
from gtts import gTTS

counter=1

connection = sqlite3.connect('chatbot.sqlite')
cursor = connection.cursor()
 
try:
    cursor.execute('''
        CREATE TABLE words (
            word TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE sentences (
            sentence TEXT UNIQUE,
            used INT NOT NULL DEFAULT 0
        )''')
    cursor.execute('''
        CREATE TABLE associations (
            word_id INT NOT NULL,
            sentence_id INT NOT NULL,
            weight REAL NOT NULL)
    ''')
except:
    pass
 
def get_id(entityName, text):
    """Retrieve an entity's unique ID from the database, given its associated text.
    If the row is not already present, it is inserted.
    The entity can either be a sentence or a word."""
    tableName = entityName + 's'
    columnName = entityName
    cursor.execute('SELECT rowid FROM ' + tableName + ' WHERE ' + columnName + ' = ?', (text,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute('INSERT INTO ' + tableName + ' (' + columnName + ') VALUES (?)', (text,))
        return cursor.lastrowid


def makeMP3(words,mp3name,language="en"):
    tts=gTTS(text=words,lang=language)
    tts.save("%s.wav" %mp3name)
    print("File %s.wav " % mp3name) 
def get_words(text):
    """Retrieve the words present in a given string of text.
    The return value is a list of tuples where the first member is a lowercase word,
    and the second member the number of time it is present in the text."""
    wordsRegexpString = '(?:\w+|[' + re.escape(punctuation) + ']+)'
    wordsRegexp = re.compile(wordsRegexpString)
    wordsList = wordsRegexp.findall(text.lower())
    return Counter(wordsList).items()
 
 
B = 'Hello!'
while True:
    abc="english"+str(counter)

    makeMP3(B,abc)
    os.popen('C:\\Users\MY DELL\Desktop\\ai-final-project-master\\ai-final-project-master\stanford_parser\\%s.wav ' % abc)
    counter+=1    

   
    print('B: ' + B)
    H = input('H: ').strip()
    if H == '':
        break
    words = get_words(B)
    words_length = sum([n * len(word) for word, n in words])
    sentence_id = get_id('sentence', H)
    for word, n in words:
        word_id = get_id('word', word)
        weight = sqrt(n / float(words_length))
        cursor.execute('INSERT INTO associations VALUES (?, ?, ?)', (word_id, sentence_id, weight))
    connection.commit()
    cursor.execute('CREATE TEMPORARY TABLE results(sentence_id INT, sentence TEXT, weight REAL)')
    words = get_words(H)
    words_length = sum([n * len(word) for word, n in words])
    for word, n in words:
        weight = sqrt(n / float(words_length))
        cursor.execute('INSERT INTO results SELECT associations.sentence_id, sentences.sentence, ?*associations.weight/(4+sentences.used) FROM words INNER JOIN associations ON associations.word_id=words.rowid INNER JOIN sentences ON sentences.rowid=associations.sentence_id WHERE words.word=?', (weight, word,))

    cursor.execute('SELECT sentence_id, sentence, SUM(weight) AS sum_weight FROM results GROUP BY sentence_id ORDER BY sum_weight DESC LIMIT 1')
    row = cursor.fetchone()
    cursor.execute('DROP TABLE results')
    if row is None:
        cursor.execute('SELECT rowid, sentence FROM sentences WHERE used = (SELECT MIN(used) FROM sentences) ORDER BY RANDOM() LIMIT 1')
        row = cursor.fetchone()
    B = row[1]
    cursor.execute('UPDATE sentences SET used=used+1 WHERE rowid=?', (row[0],))
