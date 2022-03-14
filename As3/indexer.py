import os
import json
import argparse
import math
from bs4 import BeautifulSoup
from urllib.parse import urldefrag
from numpy import size
from utils import get_logger, get_stemmed_tokens, compute_simhash
from tqdm import tqdm
from urllib.parse import urlparse, urljoin, urldefrag
import heapq

# class Posting:
#     def __init__(self, tfidf_score=0, important_tags_score=0):
#         self.tfidf_score = tfidf_score
#         self.important_tags_score = important_tags_score
    
#     def __str__(self):
#         return f"[{self.tfidf_score},{self.important_tags_score}]"

                                                    


class Indexer():
    def __init__(self, data_path) -> None:
        self.data_path = data_path
        self.clean_index()
        self.logger = get_logger("index_logs")

    def clean_index(self):
        self.index = {}
        # self.unique_urls = set()
        self.doc_hashmap = {}
        self.inv_doc_hashmap = {}
        # self.doc_ids = set()
        self.doc_count = 0
        self.file_count = 1

    def build_index(self):
        self.clean_index()
        documents = []
        for root, _, files in os.walk(self.data_path):
            documents.extend([os.path.join(root, path) for path in filter(lambda file: file.endswith(".json"), files)])
        self.update_index(documents)
        outward_links, inward_links = self.linking_index(documents)
        self.hits(outward_links, inward_links)
        self.page_rank(inward_links)

    def get_doc_count(self):
        return self.doc_count

    def get_token_count(self):
        return len(self.index)
    
    def calculate_tf_idf_scores(self, N):

        # w_t,d = (1+log(tf_t,d)) x log(N/df_t)
        for token in self.index:
            # no of documents containing this token
            doc_token = len(self.index[token])
            idf = 0
            if doc_token != 0:
                idf = math.log10(N / doc_token)

            for doc_id, freq in self.index[token].items():
                # term frequency in current document
                tf = 1 + math.log10((self.index[token][doc_id]))
                self.index[token][doc_id] = tf * idf

    def update_index(self, documents):
        self.logger.info("Current index update started...")
       
        for doc_path in tqdm(documents):
            self.doc_count +=1

            if self.doc_count in [18000, 36000]:
                self.save_index()
                self.file_count+=1
                self.index={}

            try:
                with open(doc_path, 'r') as fp:
                    doc = json.load(fp)
            except:
                 self.logger.warn(f"Failed to parse {doc_path}")
                 continue

            # # self.doc_ids.add(doc['url'])
            # doc['url'] = urldefrag(doc['url']).url
            # if doc['url'] in self.unique_urls:
            #     continue
            # self.unique_urls.add(doc['url'])

            token_count, tokenFreq, tags_score = get_stemmed_tokens(doc['content'])
            simhash_value = compute_simhash(tokenFreq)

            if self.doc_count in self.doc_hashmap:
                self.logger.info("Error: Key doc_count already present in doc_hashmap")
            self.doc_hashmap[self.doc_count] = [doc['url'], token_count, simhash_value]

            if doc['url'] in self.inv_doc_hashmap:
                self.logger.info("Error: Key url already present in inv_doc_hashmap")
            self.inv_doc_hashmap[doc['url']] = self.doc_count
            
            if(self.doc_count %2000 == 0):
                self.logger.info(f"parsed {self.doc_count} docurl: {doc['url']} ------ no: of tokens : {len(tokenFreq)} ")

            for token, freq in tokenFreq.items():    # For next assignments break here on size and save partial indexes and continue
                if token not in self.index:
                    self.index[token] = {}
                # if self.doc_count not in self.index[token]:
                self.index[token][self.doc_count]= [0, 0]
                self.index[token][self.doc_count][0] += freq
                self.index[token][self.doc_count][1] += tags_score.get(token,0)

        
        # self.calculate_tf_idf_scores(len(documents))
        print(len(self.index))

    def linking_index(self, documents):
        self.logger.info("Linking analysis started...")

        outward_links = dict()
        inward_links = dict()
        for doc_path in tqdm(documents):
            try:
                with open(doc_path, 'r') as fp:
                    doc = json.load(fp)
            except:
                 self.logger.warn(f"Failed to parse {doc_path}")
                 continue
            soup = BeautifulSoup(doc['content'], 'html.parser')
            for link in soup.find_all('a'):
                path = link.get('href')
                if path is not None:
                    if path.startswith('/'):
                        path = urljoin(doc['url'], path)
                    path = urldefrag(path).url  # defragment the URL
                    if path not in self.inv_doc_hashmap:
                        self.doc_count += 1
                        self.inv_doc_hashmap[path] = self.doc_count
                        self.doc_hashmap[self.doc_count] = [path, 0]
                    current_doc_id = self.inv_doc_hashmap[doc['url']]
                    out_doc_id = self.inv_doc_hashmap[path]
                    if current_doc_id not in outward_links:
                        outward_links[current_doc_id] = []
                    outward_links[current_doc_id].append(out_doc_id)
                    if out_doc_id not in inward_links:
                        inward_links[out_doc_id] = []
                    inward_links[out_doc_id].append(current_doc_id)
        return outward_links, inward_links

    def hits(self, outward_links, inward_links):
        hub = {x:1 for x in outward_links}
        auth = {x:1 for x in inward_links}
        for i in range(5):
            hub_temp = {x: hub[x] for x in hub}
            auth_temp = {x: auth[x] for x in auth}
            norm = 0
            for doc_id in auth:
                auth[doc_id] = 0
                for in_id in inward_links[doc_id]:
                    auth[doc_id] += hub_temp[in_id]
                norm += auth[doc_id]**2
            norm = norm**(1/2)
            for doc_id in auth:
                auth[doc_id] /= norm

            norm = 0
            for doc_id in hub:
                hub[doc_id] = 0
                for out_id in outward_links[doc_id]:
                    hub[doc_id] += auth_temp[out_id]
                norm += hub[doc_id] ** 2
            norm = norm ** (1 / 2)
            for doc_id in hub:
                hub[doc_id] /= norm

            hub_change = 0
            auth_change = 0
            for doc_id in hub:
                hub_change += abs(hub[doc_id] - hub_temp[doc_id])
            for doc_id in auth:
                auth_change += abs(auth[doc_id] - auth_temp[doc_id])
            print("hub_change for round ", i+1, hub_change)
            print("auth_change for round ", i+1, auth_change)
        hub_topk = heapq.nlargest(10, hub, key=hub.get)
        auth_topk = heapq.nlargest(10, auth, key=auth.get)
        for x in hub_topk:
            print("hub top scores: ", x, hub[x])
        for x in auth_topk:
            print("auth top scores: ", x, auth[x])
        hits_score = {x:0 for x in hub}
        hits_score.update(auth)
        for doc_id in hits_score:
            if doc_id in auth and doc_id in hub:
                hits_score[doc_id] = 0.7 * auth[doc_id] + 0.3 * hub[doc_id]
            elif doc_id in auth:
                hits_score[doc_id] = 0.7 * auth[doc_id]
            else:
                hits_score[doc_id] = 0.3 * hub[doc_id]

        with open("hits_scores.json", 'w+') as f:
            json.dump(hits_score, f)

    def page_rank(self, inward_links):
        rank = {x:(1/55000) for x in inward_links}
        for i in range(7):
            rank_temp = {x: rank[x] for x in rank}
            #norm = 0
            for doc_id in rank:
                rank[doc_id] = 0.85
                for in_id in inward_links[doc_id]:
                    if in_id not in rank_temp:
                        rank_temp[in_id] = 1/55000
                    rank[doc_id] += 0.15 * rank_temp[in_id] / len(inward_links[doc_id])
                #norm += rank[doc_id]**2
            #norm = norm**(1/2)
            #for doc_id in auth:
            #    auth[doc_id] /= norm
            rank_change = 0
            for doc_id in rank:
                rank_change += abs(rank[doc_id] - rank_temp[doc_id])
            print("rank_change for round ", i + 1, rank_change)
        rank_topk = heapq.nlargest(10, rank, key=rank.get)
        for x in rank_topk:
            print("page rank top scores: ", x, rank[x])
        with open("page_rank_scores.json", 'w+') as f:
            json.dump(rank, f)

    def save_index(self):             # next to save partial indexes
        self.index = {k:v for k,v in sorted(self.index.items(), key=lambda item: item[0])}
        with open(str(self.file_count) + 'index.txt', 'w+') as file:
            for key, value in self.index.items():
                file.write(str(key) +" - ")
                json.dump(value, file)
                file.write('\n')
        print(len(self.index))
        return
    
    def save_doc_hashmap(self, path):      
        with open(path, 'w+') as f:
            json.dump(self.doc_hashmap, f)

    def save_inv_doc_hashmap(self, path):
        with open(path, 'w+') as f:
            json.dump(self.inv_doc_hashmap, f)

def main(args):
    data_path = args.path
    indexer = Indexer(data_path)
    indexer.build_index()
    indexer.save_index()
    indexer.save_doc_hashmap("doc_hashmap.json")
    indexer.save_inv_doc_hashmap("inv_doc_hashmap.json")
    # index_size_in_bytes = os.path.getsize(args.indexfile)
    # index_size = index_size_in_bytes/(1024)
    # doc_count = indexer.get_doc_count()
    # token_count = indexer.get_token_count()
    # print()
    # with open("Report_indexing.txt", 'w+') as fp:
    #     fp.write(f"The number of indexed documents: {doc_count} \n")
    #     fp.write(f"The number of unique tokens: {token_count} \n")
    #     fp.write(f"Index size: {index_size} KB \n")

    # with open("Report.md", 'w+') as fp:
    #     fp.write(f"<table> \
    #                 <thead> \
    #                     <tr> \
    #                     <th>Indexed Documents</th> \
    #                     <th>Unique tokens</th> \
    #                     <th>Index Size/th> \
    #                     </tr> \
    #                 </thead> \
    #                 <tbody> \
    #                     <tr> \
    #                     <td>{doc_count}</td> \
    #                     <td>{token_count}</td> \
    #                     <td>{index_size} KB</td> \
    #                     </tr> \
    #                 </tbody> \
    #                 </table> \
    #                     ")



def run():
    parser = argparse.ArgumentParser(description='Build index of a folder.')
    parser.add_argument('--path', help='folderpath to index', default="./data/DEV")
    parser.add_argument('--indexing', help='To do indexing? False or True ', default=True)
    args = parser.parse_args()
    main(args)
