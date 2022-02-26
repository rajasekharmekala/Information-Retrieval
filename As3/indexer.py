import os
import json
import argparse

from numpy import size
from utils import get_logger, get_stemmed_tokens

class Vocab:
    def __init__(self, tokens = []):
        self.vocab = {}
    def build_vocab(self, tokens = []):
        self.tokens = []
        self.update_vocab(tokens)

    def update_vocab(self, tokens = []):
        for token in tokens:
            self.vocab[token] = self.vocab.get(token, 0) +1
    
    # Method:        Map<Token,Count> computeWordFrequencies(List<Token>)
    def computeWordFrequencies(self, tokens):
        # COMPLEXITY: O(n) where n is the number of tokens
        if tokens is None:
            return {}
        self.build_vocab(tokens)
        return self.vocab
    
    # Method:         void print(Frequencies<Token, Count>)
    def print(self, dict):
        # COMPLEXITY: O(nlogn) where n=#(dict_items)
        # O(nlogn) for sorting, O(n) for iterating over each key. 
        # dict_items = sorted(dict.items(), key=lambda kv: kv[1], reverse=True)
        for token, count in dict.items():
            print(token,"\t",count)


class Indexer():
    def __init__(self, data_path) -> None:
        self.data_path = data_path
        self.clean_index()
        self.logger = get_logger("index_logs")

    def clean_index(self):
        self.index = {}
        self.doc_hashmap = {}
        self.doc_ids = set()
        self.doc_count = 0


    def build_index(self):
        self.clean_index()
        documents = []
        for root, _, files in  os.walk(self.data_path):
            documents.extend([os.path.join(root, path) for path in filter(lambda file: file.endswith(".json"), files ) ])
        self.update_index(documents)

    def param(self, x):
        print(x)
        return True

    def get_doc_count(self):
        return self.doc_count

    def get_token_count(self):
        return len(self.index)

    def update_index(self, documents):
        vocab = Vocab()
        self.logger.info("Current index update started...")
       
        for doc_path in documents:
            try:
                with open(doc_path, 'r') as fp:
                    doc = json.load(fp)
            except:
                 self.logger.warn(f"Failed to parse {doc_path}")
                 continue
            self.doc_count +=1
            self.doc_ids.add(doc['url'])
            if self.doc_count in self.doc_hashmap:
                self.logger.info("Error: Key doc_count already present in doc_hashmap")
            self.doc_hashmap[self.doc_count]=doc['url']

            tokens = get_stemmed_tokens(doc['content'])
            # total_doc_tokens = len(tokens)
            self.logger.info(f"parsed {self.doc_count} docurl: {doc['url']} ------ token count: {len(tokens)} ")
            # self.logger.info(f"{self.doc_count}")
            for token, freq in vocab.computeWordFrequencies(tokens).items():    # For next assignments break here on size and save partial indexes and continue
                if token not in self.index:
                    self.index[token] = []
                self.index[token].append((self.doc_count, freq))
    
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
    indexer.save_doc_hashmap("doc_hashmap.txt")
    index_size_in_bytes = os.path.getsize(args.indexfile)
    index_size = index_size_in_bytes/(1024)
    doc_count = indexer.get_doc_count()
    token_count = indexer.get_token_count()
    print()
    with open("Report.txt", 'w+') as fp:
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



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build index of a folder.')
    parser.add_argument('--path', help='folderpath to index', default="./data")
    parser.add_argument('--indexfile', help='index dump filename', default="index.json" )
    args = parser.parse_args()
    main(args)