import re
import argparse


def split_line(str):
    # COMPLEXITY: O(line_length) for using pattern match algorithm using regular expression
    # O(k) for k produced tokens, O(line_length + k) & k < line_length => O(line_length)
    str = str.strip()
    if(len(str) ==0):
        return []
    return [x.lower() for  x in filter(lambda x: len(x)>1 , re.split("[^a-zA-Z0-9@#*&']+", str) )  ]



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
        dict_items = sorted(dict.items(), key=lambda kv: kv[1], reverse=True)
        for token, count in dict_items:
            print(token,"\t",count)

class Tokenizer:
    def __init__(self, tokenize_fn = split_line):
        self.tokenize_fn = tokenize_fn

    # Method: List<Token> tokenize(TextFilePath)
    def tokenize(self, filepath):
        # file is  iterated by reading every line in a sequence 
        # each line takes O(line_length) for parsing
        # COMPLEXITY: O(n * k) where n is the number of lines in the file and k is the average length of line(eqvivalently, O(total number of characters in the file))

        list = []
        if filepath is None :
            raise Exception("Filepath not provided")
        try:
            with open(filepath, 'r+') as f:
                for line in f.readlines():
                    list.extend( self.tokenize_fn(line))
        except:
            raise Exception("Invalid filepath")
        return list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tokenize a file and build vocab.')
    parser.add_argument('file', help='filepath to tokenize')
    args = parser.parse_args()

    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(args.file)
    vocab = Vocab()
    dict = vocab.computeWordFrequencies(tokens)
    vocab.print(dict)


