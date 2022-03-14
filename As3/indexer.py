import os
import json
import argparse
import math

from urllib.parse import urldefrag
from numpy import size
from utils import get_logger, get_stemmed_tokens
from tqdm import tqdm

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
        # self.doc_ids = set()
        self.doc_count = 0
        self.file_count = 1


    def build_index(self):
        self.clean_index()
        documents = []
        for root, _, files in  os.walk(self.data_path):
            documents.extend([os.path.join(root, path) for path in filter(lambda file: file.endswith(".json"), files ) ])
        self.update_index(documents)

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

            if self.doc_count in [18000, 36000]: #[18000, 36000]
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

            if self.doc_count in self.doc_hashmap:
                self.logger.info("Error: Key doc_count already present in doc_hashmap")
            self.doc_hashmap[self.doc_count]=[doc['url'],token_count]

            

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

            

def main(args):
    data_path = args.path
    indexer = Indexer(data_path)
    indexer.build_index()
    indexer.save_index()
    indexer.save_doc_hashmap("doc_hashmap.json")
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