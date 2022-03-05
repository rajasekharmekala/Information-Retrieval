import os
import json
import argparse
import math

from urllib.parse import urldefrag
from numpy import size
from utils import get_logger, get_stemmed_tokens



class Indexer():
    def __init__(self, data_path) -> None:
        self.data_path = data_path
        self.clean_index()
        self.logger = get_logger("index_logs")

    def clean_index(self):
        self.index = {}
        self.unique_urls = set()
        self.doc_hashmap = {}
        # self.doc_ids = set()
        self.doc_count = 0


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
       
        for doc_path in documents:
            try:
                with open(doc_path, 'r') as fp:
                    doc = json.load(fp)
            except:
                 self.logger.warn(f"Failed to parse {doc_path}")
                 continue

            # self.doc_ids.add(doc['url'])
            doc['url'] = urldefrag(doc['url']).url
            if doc['url'] in self.unique_urls:
                continue
            self.unique_urls.add(doc['url'])
            
            self.doc_count +=1
            if self.doc_count in self.doc_hashmap:
                self.logger.info("Error: Key doc_count already present in doc_hashmap")
            self.doc_hashmap[self.doc_count]=doc['url']

            tokenFreq = get_stemmed_tokens(doc['content'])
            # total_doc_tokens = len(tokens)
            # if(self.doc_count %200 == 0):
            self.logger.info(f"parsed {self.doc_count} docurl: {doc['url']} ------ no: of tokens : {len(tokenFreq)} ")
            # self.logger.info(f"{self.doc_count}")
            for token, freq in tokenFreq.items():    # For next assignments break here on size and save partial indexes and continue
                if token not in self.index:
                    self.index[token] = {}
                # if self.doc_count not in self.index[token]:
                self.index[token][self.doc_count] = freq
            
        self.calculate_tf_idf_scores(len(documents))



    
    def save_index(self, path):             # next to save partial indexes
        with open(path, 'w+') as f:
            json.dump(self.index, f)
    
    def save_doc_hashmap(self, path):      
        with open(path, 'w+') as f:
            json.dump(self.doc_hashmap, f)

            

def main(args):
    data_path = args.path
    indexer = Indexer(data_path)
    indexer.build_index()
    indexer.save_index(args.indexfile)
    indexer.save_doc_hashmap("doc_hashmap.json")
    index_size_in_bytes = os.path.getsize(args.indexfile)
    index_size = index_size_in_bytes/(1024)
    doc_count = indexer.get_doc_count()
    token_count = indexer.get_token_count()
    print()
    with open("Report_indexing.txt", 'w+') as fp:
        fp.write(f"The number of indexed documents: {doc_count} \n")
        fp.write(f"The number of unique tokens: {token_count} \n")
        fp.write(f"Index size: {index_size} KB \n")

    with open("Report.md", 'w+') as fp:
        fp.write(f"<table> \
                    <thead> \
                        <tr> \
                        <th>Indexed Documents</th> \
                        <th>Unique tokens</th> \
                        <th>Index Size/th> \
                        </tr> \
                    </thead> \
                    <tbody> \
                        <tr> \
                        <td>{doc_count}</td> \
                        <td>{token_count}</td> \
                        <td>{index_size} KB</td> \
                        </tr> \
                    </tbody> \
                    </table> \
                        ")



def run():
    parser = argparse.ArgumentParser(description='Build index of a folder.')
    parser.add_argument('--path', help='folderpath to index', default="./data/DEV")
    parser.add_argument('--indexfile', help='index dump filename', default="index.json" )
    parser.add_argument('--indexing', help='To do indexing? False or True ', default=True)
    args = parser.parse_args()
    main(args)