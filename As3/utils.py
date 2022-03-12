import os
import logging
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

from bs4 import BeautifulSoup
from bs4.element import Comment
import re

def get_logger(name, filename=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not os.path.exists("Logs"):
        os.makedirs("Logs")
    fh = logging.FileHandler(f"Logs/{filename if filename else name}.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
       "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

def is_tag_visible(element):
    if element.parent.name in ['style', 'script']:
        return False
    if isinstance(element, Comment):
        return False
    return True



def get_stemmed_tokens(html):
    soup = BeautifulSoup(html, 'html.parser')
    ps = PorterStemmer()
    text = soup.get_text()
    tokens = word_tokenize(text)

    token_count=0
    filtered_tokens = {}
    for token in tokens:
        token = re.sub(r'[^\x00-\x7F]+', '', token)
        token = token.lower()
        token = ps.stem(token)
        for ftoken in re.findall(r"[a-zA-Z0-9@#*&']{2,}", token):
            if ftoken in filtered_tokens:
                filtered_tokens[ftoken] += 1
            else:
                filtered_tokens[ftoken] = 1

            token_count+=1

    # important word scoring
    tags_score = {}
    important_words = soup.find_all(["a", "title", "b", "strong",  "h1", "h2", "h3"])

    for words in important_words:
        rank = 0
        if words.name == "a": # Anchor text 
            rank = 30
        if words.name == "title":
            rank = 10
        elif words.name == "h1":
            rank = 5
        elif words.name == "h2":
            rank = 4
        elif words.name == "h3":
            rank = 3
        elif words.name == "b" or words.name == "strong":
            rank = 2

        for token in word_tokenize(words.text):
            token = re.sub(r'[^\x00-\x7F]+', '', token)
            token = token.lower()
            token = ps.stem(token)
            for ftoken in re.findall(r"[a-zA-Z0-9@#*&']{2,}", token):
                if ftoken in tags_score:
                    tags_score[ftoken] += rank
                else:
                    tags_score[ftoken] = rank

    return token_count, filtered_tokens, tags_score
