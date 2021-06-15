import os
import sys
from collections import deque
from string import punctuation

from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from pympler import asizeof


class BSBI_indexing:
    def __init__(self, input_dir, block_size, output_dir):
        self.input_dir = input_dir
        self.block_size = block_size
        self.output_dir = output_dir
        self.number_of_documents = 0
        self.docId_to_doc_map = {}
        self.current_block = 0
        self.total_documents_size = 0
        self.current_docId = 0
        self.current_file = 0
        self.punctuation = punctuation
        self.term_to_docIds_map = {}
        self.term_to_docIds_sorted = []
        self.docId_to_terms = None
        self.current_termId = 0
        self.current_block_size = 0
        self.end_or_fail = False
        self.porter = PorterStemmer()

    def making_index(self):
        self.total_documents_size = 0

        # Construct a doc to docId mapping and find total doc size
        doc_index = 0
        for dir_path, dir_names, file_names in os.walk(self.input_dir):
            file_names.sort()
            for file_name in file_names:
                self.docId_to_doc_map[doc_index] = file_name
                file_pointer = os.path.join(dir_path, file_name)

                # making sure fp points to file not a link
                if not os.path.islink(file_pointer):
                    file_size = os.path.getsize(file_pointer)

                    # if file exceeds the block size limit
                    if file_size >= self.block_size:
                        print("Error! {} size exceeds block size limit.".format(
                            self.docId_to_doc_map[self.current_docId]
                        ))
                        print("file size vs block size: {} Kb > {} Kb".format(
                            file_size / 1024,
                            self.block_size / 1024
                        ))
                        sys.exit(1)
                    self.total_documents_size += file_size
                doc_index += 1

        self.number_of_documents = len(self.docId_to_doc_map)

        # ready output directory
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        else:
            if os.path.isdir(self.output_dir):
                for dir_path, dir_names, file_names in os.walk(self.output_dir):
                    for file_name in file_names:
                        os.remove(os.path.join(dir_path, file_name))
            else:
                os.remove(self.output_dir)
                os.mkdir(self.output_dir)

        # Make Index
        while True:
            self.parse_next_document()
            self.invert_document()

            size = sys.getsizeof(self.term_to_docIds_map)
            current_block_size = self.current_block_size + size
            if current_block_size >= self.block_size or self.end_or_fail:
                # now it's time to sort term-doc by terms and write it to the disk
                terms = list(self.term_to_docIds_map.keys())
                terms.sort()
                self.term_to_docIds_sorted = []
                for term in terms:
                    self.term_to_docIds_sorted.append((term, self.term_to_docIds_map[term]))
                    del self.term_to_docIds_map[term]
                self.term_to_docIds_map = sorted(self.term_to_docIds_map.items())
                self.write_block()
                self.current_block += 1
                self.term_to_docIds_map = {}
                self.current_block_size = 0
                if self.end_or_fail:
                    break

        print("merging state initiated, Please wait")
        self.merge_blocks()
        # self.clear_output_directory()

    def parse_next_document(self):
        self.docId_to_terms = None

        # receive next doc and it's size
        if self.current_docId > self.number_of_documents - 1:
            self.end_or_fail = True
            return
        current_document = self.docId_to_doc_map[self.current_docId]
        current_document = os.path.join(self.input_dir, current_document)
        self.current_file = open(current_document, 'rt', encoding='utf-8')
        current_file_size = os.path.getsize(current_document)

        # parse
        if current_file_size <= self.block_size:
            self.docId_to_terms = [self.current_docId, self.current_file.read()]
            self.current_file.close()
            self.current_docId += 1
        else:
            # overflowed the block
            print("Error! {} size exceeds block size limit.".format(
                self.docId_to_doc_map[self.current_docId]
            ))
            print("file size vs block size: {} Kb > {} Kb".format(
                current_file_size / 1024,
                self.block_size / 1024
            ))
            self.end_or_fail = True

        # extract tokens form a doc and process them into terms
        self.docId_to_terms[1] = word_tokenize(self.docId_to_terms[1])
        self.preprocess_terms(self.docId_to_terms[1])

    def preprocess_terms(self, terms):
        size_of_terms = len(terms)
        for i in range(0, size_of_terms):
            # Removing Punctuation
            terms[i] = "".join([char for char in terms[i] if char not in punctuation])
            # Lowering all terms
            terms[i] = terms[i].lower()
            # stemming terms
            terms[i] = self.porter.stem(terms[i])

    def invert_document(self):
        if self.end_or_fail:
            return
        # store terms as term-document postings
        index = 0
        number_of_duplicate_terms = 0
        document_id = self.docId_to_terms[0]
        terms = self.docId_to_terms[1]
        while index < len(terms):
            term = terms[index]
            if term not in self.term_to_docIds_map:
                number_of_duplicate_terms += 1
                size = sys.getsizeof(term)
                inc = size % 8
                if inc != 0:
                    size += 8 - inc
                self.term_to_docIds_map[term] = []
                self.current_block_size += size
            self.term_to_docIds_map[term].append(document_id)
            index += 1

        size = sys.getsizeof(document_id)
        self.current_block_size += size
        self.current_block_size += number_of_duplicate_terms * 56
        self.current_block_size += number_of_duplicate_terms * size
        self.current_block_size += 8 * index

        del self.docId_to_terms, terms

    def write_block(self):
        with open("{}/block{}.txt".format(self.output_dir, self.current_block), 'wt', encoding='utf-8') as file:
            for term, documents in self.term_to_docIds_sorted:
                for docId in documents:
                    file.write('{} , {}\n'.format(term, docId))
        del self.term_to_docIds_map, file

    def merge_blocks(self):
        pass

    def clear_output_directory(self):
        for dirpath, dirnames, filenames in os.walk(self.output_dir):
            for file in filenames:
                if not file == 'output.txt':
                    os.remove(os.path.join(dirpath, file))



