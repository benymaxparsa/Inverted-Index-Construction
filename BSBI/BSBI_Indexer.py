import gc
import os
import sys
import time
from collections import deque
from string import punctuation

from guppy import hpy
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from pympler import asizeof


class BSBIindexer:
    def __init__(self, input_dir, block_size, output_dir, verbose):
        self.input_dir = input_dir
        self.block_size = block_size
        self.output_dir = output_dir
        self.verbose = verbose
        self.number_of_docs = 0
        self.docId_to_doc = {}
        self.current_block = 0
        self.total_docs_size = 0
        self.current_docId = 0
        self.current_file = 0
        self.punctuation = punctuation + '-—'
        self.sorting_times = []
        self.term_to_docIds = {}
        self.term_to_docIds_sorted = []
        self.docId_to_terms = None
        self.heapy = hpy()
        self.memory_track = []
        self.current_termId = 0
        self.current_block_size = 0
        self.eof = False
        self.porter = PorterStemmer()

    def construct_index(self):
        if self.verbose:
            self.memory_track.append(self.heapy.heap().size)
        timer_start = time.process_time()
        self.total_docs_size = 0

        # Construct a doc to docId mapping and find total doc size
        doc_index = 0
        for dir_path, dir_names, file_names in os.walk(self.input_dir):
            file_names.sort()
            for file_name in file_names:
                self.docId_to_doc[doc_index] = file_name
                file_pointer = os.path.join(dir_path, file_name)

                # making sure fp points to file not a link
                if not os.path.islink(file_pointer):
                    file_size = os.path.getsize(file_pointer)

                    # if file exceeds the block size limit
                    if file_size >= self.block_size:
                        print("Error! {} size exceeds block size limit.".format(
                            self.docId_to_doc[self.current_docId]
                        ))
                        print("file size vs block size: {} Kb > {} Kb".format(
                            file_size / 1024,
                            self.block_size / 1024
                        ))
                        sys.exit(1)
                    self.total_docs_size += file_size
                doc_index += 1

        self.number_of_docs = len(self.docId_to_doc)

        self.print_info()





    def print_info(self):
        pass