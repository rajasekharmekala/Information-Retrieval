import os
import logging
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import hashlib
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


def compare_simhash(current_hash, past_hash):
    similarity = 0
    for i in range(len(past_hash) - 1, -1, -1):
        similarity = 1 - '{0:80b}'.format(current_hash ^ past_hash[i]).count("1") / 128.0
        #print("similarity score: ", similarity)
        if similarity > 0.95:  # 95% similar
            return False
    return True


def compute_simhash(tokens):
    hash_ls = []
    for token in tokens:
        hash_ls.append(hashlib.md5(token.encode()))

    hash_int_ls = []
    for hash in hash_ls:
        hash_int_ls.append(int(hash.hexdigest(), 16))

    res = 0
    for i in range(128):
        sum_ = 0
        for h in hash_int_ls:
            if h >> i & 1 == 1:
                sum_ += 1
            else:
                sum_ += -1
        if sum_ > 1:
            sum_ = 1
        else:
            sum_ = 0

        res += sum_ * 2 ** i
    return res

def get_stemmed_tokens(html):
    soup = BeautifulSoup(html, 'html.parser')
    ps = PorterStemmer()
    text = soup.get_text()
    tokens = word_tokenize(text)

    token_count=0
    filtered_tokens = {}
    last_token = ""
    display_text = ""
    for token in tokens:
        token = re.sub(r'[^\x00-\x7F]+', '', token)
        token = token.lower()
        if token_count < 20:
            display_text += token + " "
        token = ps.stem(token)
        for ftoken in re.findall(r"[a-zA-Z0-9@#*&']{2,}", token):
            if ftoken in filtered_tokens:
                filtered_tokens[ftoken] += 1
            else:
                filtered_tokens[ftoken] = 1

            if last_token == "":
                last_token = ftoken
                continue
            bigram_token = last_token + " " + ftoken
            if bigram_token in filtered_tokens:
                filtered_tokens[bigram_token] += 1
            else:
                filtered_tokens[bigram_token] = 1
            last_token = ftoken
            token_count+=1

    # important word scoring
    tags_score = {}
    important_words = soup.find_all(["a", "title", "b", "strong",  "h1", "h2", "h3"])
    doc_title = ""

    for words in important_words:
        rank = 0
        if words.name == "a": # Anchor text 
            rank = 30
        if words.name == "title":
            rank = 10
            doc_title = words.text
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

    return token_count, filtered_tokens, tags_score, doc_title, display_text



# def stop_words():
#     stop_words_list = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
#     stop_words_dict = {}
#     ps = PorterStemmer()
#     for word in stop_words_list and len(word)>1:
#             word = word.lower()
#             word = ps.stem(word)
#             if word not in stop_words_dict:
#                 postings = Search().retrive(word)
#                 stop_words_dict[word] = postings

#     for word1 in stop_words_list and len(word1)>1:
#         for word2 in stop_words_list and len(word2)>1:
#             word1 = word1.lower()
#             word1 = ps.stem(word1)
#             word2 = word2.lower()
#             word2 = ps.stem(word2)
#             word = word1 + " " + word2
#             if word not in stop_words_dict:
#                 postings = Search().retrive(word)
#                 stop_words_dict[word] = postings

#     return stop_words_dict