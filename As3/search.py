import json
import re
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from time import process_time


class Search:
    def __init__(self):
        # load indexes in memory
        self.ps = PorterStemmer()
        start = process_time()
        print("Starting at ", start)
        self.doc_id_to_url = self.load_file('doc_hashmap.json')
        self.data = self.load_file('index.json')

        end = process_time()
        print("Total time to load indexes in memory:", end-start)



    def load_file(self, filepath):
        # Opening JSON file
        f = open(filepath, 'r')
        data = json.load(f)
        # Closing file
        f.close()
        return data

    def search_query(self, query):
        tokens = word_tokenize(query)

        query_len = 0
        query_dict = {}
        query_word_list = []

        for token in tokens:
            token = re.sub(r'[^\x00-\x7F]+', '', token)
            token = token.lower()
            token = self.ps.stem(token)
            if re.match(r"[a-zA-Z0-9@#*&']{2,}", token):
                query_len += 1
                query_word_list.append(token)
                for doc_id in self.data[token]:
                    query_dict[doc_id] = query_dict.get(doc_id, 0) + 1

        tfidf_scores= dict()
        for doc_id, count in query_dict.items():
            if query_len == count:
                for token in query_word_list:
                    tfidf_scores[doc_id] = tfidf_scores.get(doc_id, 0) + self.data[token][doc_id]
        
        df = dict(sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True))

        search_list = []
        count=0
        for doc_id in df:
            doc_id = str(doc_id)
            if(count==5):
                break
            search_list.append(self.doc_id_to_url[doc_id])
            count+=1

        return search_list