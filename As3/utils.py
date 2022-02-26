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
    texts = soup.findAll(text=True)
    visible_texts = filter(is_tag_visible, texts)  
    vis_text = " ".join(t.strip() for t in visible_texts)
    tokens = [ps.stem(word) for word in word_tokenize(vis_text)]

    filtered_tokens = []
    for token in tokens:
        token = re.sub(r'[^\x00-\x7F]+', '', token)
        token = token.lower()
        if (re.match(r"[a-zA-Z0-9@#*&']", token)):
            filtered_tokens.append(token)
    return filtered_tokens
