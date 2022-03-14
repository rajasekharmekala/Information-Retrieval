import json
import re
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from time import process_time
import math
import heapq


class Search:
    def __init__(self):
        # load indexes in memory
        self.ps = PorterStemmer()
        start = process_time()
        print("Starting at ", start)
        self.doc_id_to_url = self.load_file('doc_hashmap.json')
        self.seek_index = self.load_file('seek_index.txt')
        self.final_index = open('final_index.txt', 'r')
        self.N = 55000

        end = process_time()
        # print("Total time to load indexes in memory:", end-start)

    def retrive(self, token):
        #f1 = open('seek_index.txt', 'r')
        #f2 = open('final_index.txt', 'r')
        #s_dict = json.load(f1)
        idx = self.seek_index[token[0:2]]
        # print(idx)
        self.final_index.seek(idx)
        while True:
            line = self.final_index.readline().split(" - ")
            # print(line)
            if line[0] >= token: break

        if token == line[0]:
            term = line[0]
            d1 = json.loads(line[1])
            # print(term)
            return d1
        else:
            # print("Not found!!")
            return {}

    def load_file(self, filepath):
        # Opening JSON file
        f = open(filepath, 'r')
        data = json.load(f)
        # Closing file
        f.close()
        return data

    def search_query(self, query, k):
        tokens = word_tokenize(query)

        query_len = 0
        query_dict = {}
        query_tokens = dict()
        query_word_list = []

        for token in tokens:
            token = re.sub(r'[^\x00-\x7F]+', '', token)
            token = token.lower()
            token = self.ps.stem(token)
            if re.match(r"[a-zA-Z0-9@#*&']{2,}", token):
                query_len += 1
                query_tokens[token] = query_tokens.get(token, 0) + 1
                query_word_list.append(token)
                # for doc_id in self.data[token]:
                #     query_dict[doc_id] = query_dict.get(doc_id, 0) + 1
        '''
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
        '''

        doc_scores = dict()
        #query_token_visited = dict()
        try:
            for token in query_tokens:
                postings = self.retrive(token)
                if(len(postings)==0):
                    # print("Query word - ", token, " Not found in Index!!")
                    continue
                #query_token_visited[token] = query_token_visited.get(token, 0) + 1
                #if query_token_visited[token] > 1:
                #    break
                query_tf = 1 + math.log10(query_tokens[token])
                query_idf = math.log10(self.N / len(postings))
                for doc_id in postings:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + (0.9 * postings[doc_id][0] + 0.1 *  math.log10(postings[doc_id][1]+1)) * (query_tf * query_idf)
        except KeyError:
            print("token in the query is not in the corpus")
        # use of heap reduces the sort time complexity
        # for doc_id in doc_scores:
        #     # doc_scores[doc_id] /= self.doc_id_to_url[doc_id][1]
        #     print(doc_id, doc_scores[doc_id])
        # print("END")
        search_topk = heapq.nlargest(k, doc_scores, key=doc_scores.get)
        url_klist=[]
        for doc_id in search_topk:
            print(doc_id,doc_scores[doc_id], postings[doc_id][0], )
            url_klist.append(self.doc_id_to_url[doc_id][0])

        return url_klist