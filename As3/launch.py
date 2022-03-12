
import os
import json
import argparse

import indexer
from search import Search
from merger import Merger
from time import process_time


def indexing():
    print("Start Indexing Intially!!")

    start = process_time()
    print("Starting at ", start)

    # initialization
    indexer.run()
    print("Indexer completed! Starting Merging!!")
    Merger().merge_files()
    print("Merging Completed!!")


    end = process_time()
    print("Total time:", end-start)


def do_search() -> None:
    print("Start of search engine.. Welcome!!")
    file = open(f"Report_search.txt", "w+")

    retriever = Search()

    while True:
        query = input("\nInput query: ")
        file.write("\nInput query: ")
        file.write(query)
        file.write("\n")


        start = process_time()
        result = retriever.search_query(query)
        time = f"Query response time: {process_time() - start}"

        file.write(time)
        file.write("\n")
        print(time)

        for link in result:
            file.write(link)
            file.write("\n")
            print(link)

    file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start of search engine.. Welcome!')
    parser.add_argument('--indexing', help='To do indexing? False or True ', default=False)
    args = parser.parse_args()
    if args.indexing:
        indexing()

    do_search()
