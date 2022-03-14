import os
import json
import math 
import re

class Merger:
    def __init__(self):
        self.N = 55000
        self.seek_dict={}
        self.offset=0


    # def calculate_tf_idf_scores(self, N):
    #     # w_t,d = (1+log(tf_t,d)) x log(N/df_t)
    #     for token in self.index:
    #         # no of documents containing this token
    #         doc_token = len(self.index[token])
    #         idf = 0
    #         if doc_token != 0:
    #             idf = math.log10(N / doc_token)

    #         for doc_id, freq in self.index[token].items():
    #             # term frequency in current document
    #             tf = 1 + math.log10((self.index[token][doc_id]))
    #             self.index[token][doc_id] = tf * idf


    def retrive(self, token):
        f1 = open('seek_index.txt', 'r')
        f2 = open('final_index.txt', 'r')
        s_dict = json.load(f1)
        idx=s_dict[token[0:2]]
        print(idx)
        f2.seek(idx)
        while True:
            line = f2.readline().split(" - ")
            print(line)
            if line[0] >= token: break
            
        if token == line[0]: 
            term=line[0]
            d1=json.loads(line[1])
            print(term)
            print(d1)
        else:
            print("Not found!!")



    def merge_files(self):
        try:
            with open('final_index.txt', 'w+') as mergedIndex, open('seek_index.txt', 'w+') as seekIndex:
                with open("1index.txt", 'r') as f1, open("2index.txt", 'r') as f2, open("3index.txt", 'r') as f3:
                    f1Readline = False
                    f2Readline = False
                    f3Readline = False
                    line1, line2, line3 = f1.readline().strip().split(" - "), f2.readline().strip().split(" - "), f3.readline().strip().split(" - ")
                    # print(line1[0])

                    while line1 or line2 or line3:
                        if f1Readline:
                            line1 = f1.readline().strip().split(" - ")
                        if f2Readline:
                            line2 = f2.readline().strip().split(" - ")
                        if f3Readline:
                            line3 = f3.readline().strip().split(" - ")
                        
                        token1, token2, token3 = line1[0], line2[0],line3[0]
                        listOfTokens = [value for value in [token1,token2,token3] if value!=""]
                        if len(listOfTokens) > 0:
                            mergedToken = min(listOfTokens)
                        else:
                            break
                        
                        mergedTokenIdx = {}
                        if token1 == mergedToken:
                            d1=json.loads(line1[1])
                            mergedTokenIdx.update(d1)
                            f1Readline = True
                        else: f1Readline = False
                        
                        if token2 == mergedToken:
                            d2=json.loads(line2[1])
                            mergedTokenIdx.update(d2)  
                            f2Readline = True
                        else: f2Readline = False
                        
                        if token3 == mergedToken:
                            d3=json.loads(line3[1])
                            mergedTokenIdx.update(d3)    
                            f3Readline = True
                        else: f3Readline = False

                        for doc_id in mergedTokenIdx:
                            tf = 1 + math.log10((mergedTokenIdx[doc_id][0]))
                            idf = math.log10(self.N / len(mergedTokenIdx))
                            mergedTokenIdx[doc_id][0] = tf*idf
                        
                        # mergedTokenIdx = dict(sorted(mergedTokenIdx.items(), key=lambda x:x[1][0]))
                        mergedIndex.write(mergedToken + " - " + json.dumps(mergedTokenIdx) + "\n")
                        prev=""
                        reg_ex = r'^([a-z][a-z]|[a-z])'
                                                        
                        if mergedToken[0:2] > prev:
                            if (mergedToken[0:1] not in self.seek_dict):
                                self.seek_dict[mergedToken[0:1]] = self.offset
                            if (mergedToken[0:2] not in self.seek_dict):
                                self.seek_dict[mergedToken[0:2]] = self.offset

                        prev = mergedToken[0:2] 
                        self.offset += len(mergedToken + " - " + json.dumps(mergedTokenIdx) + "\n")
                        # print(self.offset)

                    # print(self.seek_dict)
                    json.dump(self.seek_dict, seekIndex)

            mergedIndex.close()
            seekIndex.close()

        except:
            print(f"Error!. Merging failed.")



# Merger().merge_files()
# Merger().retrive("abb")