import json
import re
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from time import process_time
import math
import heapq
from utils import compare_simhash


class Search:
    def __init__(self):
        # load indexes in memory
        self.ps = PorterStemmer()
        start = process_time()
        print("Starting at ", start)
        self.doc_id_to_url = self.load_file('doc_hashmap.json')
        self.seek_index = self.load_file('seek_index.txt')
        self.page_rank_scores = self.load_file('page_rank_scores.json')
        self.hits_scores = self.load_file('hits_scores.json')
        self.final_index = open('final_index.txt', 'r')
        self.stop_words_dict = {}
        self.stop_words_dict = self.stop_words()
        end = process_time()
        self.N = 55000
        print("Total time to init search in memory:", end-start)

    

    def retrive(self, token):
        #f1 = open('seek_index.txt', 'r')
        #f2 = open('final_index.txt', 'r')
        #s_dict = json.load(f1)
        # print(token)
        if token in self.stop_words_dict:
            return self.stop_words_dict[token]

        token_list = token.split(" ")
        bigram_key=token
        if(len(token_list)==1):
            bigram_key=token_list[0][0:2]
        if(len(token_list)==2):
            bigram_key=token_list[0][0:2]+"-"+token_list[1][0:2]

        idx = self.seek_index[bigram_key]
        # print(idx)
        self.final_index.seek(idx)
        # print(idx)
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

    def stop_words(self):
        print("hi")
        # stop_words_list = ["me", "my", "we", "our", "you", "your", "yours", "he", "him", "his", "she", "her", "it", "its", "they", "them", "their", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "an", "the", "and", "but", "if", "or", "as", "of", "at", "by", "for", "with", "about", "to", "from", "in", "out", "on", "off", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "some", "such", "no", "nor", "not", "only", "same", "so", "than", "too", "very", "can", "will", "now"]
        stop_words_list = ["this", "that","is","the", "of", "and","be","to", "do", "not"]
        stop_words_dict1 = {}
        ps = PorterStemmer()
        for word in stop_words_list:
            if((len(word)>1)):
                # print(word)
                word = word.lower()
                word = ps.stem(word)
                if word not in stop_words_dict1:
                    postings = self.retrive(word)
                    stop_words_dict1[word] = postings

        for word1 in stop_words_list:
            for word2 in stop_words_list:
                if((len(word1)>1) and (len(word2)>1)):
                    word1 = word1.lower()
                    word1 = ps.stem(word1)
                    word2 = word2.lower()
                    word2 = ps.stem(word2)
                    word = word1 + " " + word2
                    if word not in stop_words_dict1:
                        postings = self.retrive(word)
                        stop_words_dict1[word] = postings

        # print(stop_words_dict1)         
        return stop_words_dict1

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
        last_token = ""
        for token in tokens:
            token = re.sub(r'[^\x00-\x7F]+', '', token)
            token = token.lower()
            token = self.ps.stem(token)
            for ftoken in re.findall(r"[a-zA-Z0-9@#*&']{2,}", token):
                query_len += 1
                query_tokens[ftoken] = query_tokens.get(ftoken, 0) + 1
                query_word_list.append(ftoken)

                if last_token == "":
                    last_token = ftoken
                    continue
                bigram_token = last_token + " " + ftoken
                query_tokens[bigram_token] = query_tokens.get(bigram_token, 0) + 1
                query_word_list.append(bigram_token)

                last_token = ftoken
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
        print(query_tokens)
        doc_scores = dict()
        norm_doc_scores = dict()
        norm_query = 0
        #query_token_visited = dict()
        try:
            for token in query_tokens:
                start1 = process_time()
                postings = self.retrive(token)
                print("retrieval time - ",(process_time()-start1)*1000)
                if(len(postings)==0):
                    # print("Query word - ", token, " Not found in Index!!")
                    continue
                #query_token_visited[token] = query_token_visited.get(token, 0) + 1
                #if query_token_visited[token] > 1:
                #    break
                query_tf = 1 + math.log10(query_tokens[token])
                query_idf = math.log10(self.N / len(postings))
                norm_query += (query_tf * query_idf)**2
                for doc_id in postings:
                    score = 0.7 * postings[doc_id][0] + 0.15 * math.log10(postings[doc_id][1]+1)
                    if doc_id in self.page_rank_scores and doc_id in self.hits_scores:
                        score += 0.1 * self.page_rank_scores[doc_id] + 0.05 * self.hits_scores[doc_id]
                    elif doc_id in self.page_rank_scores:
                        score += 0.15 * self.page_rank_scores[doc_id]
                    elif doc_id in self.hits_scores:
                        score += 0.15 * self.hits_scores[doc_id]
                    else:
                        score += 0.15 * postings[doc_id][0]
                    norm_doc_scores[doc_id] = norm_doc_scores.get(doc_id, 0) + score**2
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + score * (query_tf * query_idf)
        except KeyError:
            print("token in the query is not in the corpus")
        # use of heap reduces the sort time complexity
        # for doc_id in doc_scores:
        #     doc_scores[doc_id] /= (norm_doc_scores[doc_id]**(1/2) * norm_query**(1/2))
        search_topk = heapq.nlargest(k+5, doc_scores, key=doc_scores.get)

        url_klist=[]
        past_hash = []
        for doc_id in search_topk:
            print(doc_id,doc_scores[doc_id])
            if len(url_klist) <= k:
                #print(self.doc_id_to_url[doc_id][3])
                if True:
                #if compare_simhash(self.doc_id_to_url[doc_id][2], past_hash):
                    if len(past_hash) >= 20:
                        del past_hash[0]
                        # del past_hash_urls[0]
                    display_data = dict()
                    display_data['url'] = self.doc_id_to_url[doc_id][0]
                    display_data['title'] = self.doc_id_to_url[doc_id][3]
                    display_data['display_text'] = self.doc_id_to_url[doc_id][4]

                    url_klist.append(display_data)
                past_hash.append(self.doc_id_to_url[doc_id][2])
            else:
                break
        #print(url_klist)
        return url_klist[:k]



