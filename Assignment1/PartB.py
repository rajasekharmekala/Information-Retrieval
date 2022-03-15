# Take two text files from the command line as arguments and output the number of tokens they have in common.
from PartA import Tokenizer
import argparse

parser = argparse.ArgumentParser(description='Fetch common tokens between 2 files')
parser.add_argument('files', nargs=2, help='filepaths to parse')

args = parser.parse_args()

print(args.files)


class TextMatch:

    @staticmethod
    def get_token_set(filepath):# -> Set<Token> where file: str 
        # COMPLEXITY: O(n) where n=LEN(file) 
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(filepath)
        result = set(tokens)
        return result
    
    @staticmethod
    def common_vocab(filepath_1, filepath_2):  # -> Set<Token> where Token: str
        # COMPLEXITY: O(max(n*k1, m*k2)) 
        # where n is the number of lines in file1, k1 is average length of file1
        # m is the number of lines in file2, k2 is average length of file2

        # first, get hashset of unique tokens in file1
        # O(n) for n=LEN(file1)
        set1 = TextMatch.get_token_set(filepath_1)
        set2 = TextMatch.get_token_set(filepath_2)
        return set1.intersection(set2)


if __name__ == "__main__":
    common_tokens = TextMatch.common_vocab(args.files[0], args.files[1])
    print(len(common_tokens))
