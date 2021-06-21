## How it works:
The BSBI_indexing class is divided into methods below:
#### making_index
In this method, the process of making the index is started, and other methods are called
###### preparing document ID map
+ We will first create a dictionary that maps document ID to document path for later use
+ We ensure that no document exceeds the block size
+ We sum up the document's total size
+ then we calculate number of documents  
 
###### preparing output
+ When there is no output directory, we make one, and when there is, we clear it.
###### starting to make index
we do the following for each document :
+ tokenize the document 
+ We invert the document by making a dictionary that maps a term to a list of documents
+ if inverted index size exceeds the block size then first we sort the terms and then we store the inverted index in its block

###### merge blocks
In this step, we combine all blocks and produce one final result

#### parse_next_document
purpose of this method is to make  document ID to its terms map  

+ to do this we first make the file path using  ``docID_to_doc_map`` 
+ then we read the file if its size is less than current block size 
+ then using **nltk** `` word_tokenize`` we tokenize the document text
+ then with ``preprocess_terms`` method we do some text operations like to lower and stemming on terms 
#### preprocess_terms
here these operations will be applied on terms
+ removing punctuations
+ lowercase letters
+ stemming  with ``stem`` method in  **PorterStemmer** from **nltk** 
#### invert_document
We make a map here that maps term to a document ID posting list  
+ first we take the document ID to terms map to invert it
+ and for each term if the term was already in the inverted map called ``term_to_docIds_map`` then we just add the document id to terms posting list
+ otherwise we make a new entry in the map
+ The size of the map is calculated as we create the posting lists
+ at the end we calculate the size of current block by adding size of new terms and document IDs that has been added 

#### write_block
here is where output blocks will be written  
The output file includes a line for each document ID for each terms posting list   
The term is listed first, followed by the docID
#### merge_blocks
Using this method, we merge all already created blocks into one output file  
+ first we make a queue
+ then we fill the queue with created blocks
+ This part will continue until the queue is empty
  - take two files from the queue to merge
  - make a empty merge text file
  - read a line from both files
  - if one of two files is empty we wont continue to merge and we will go back to getting files from queue
  - split the line with space character so it fits the **term** : **document ID** format
  - then we read line by line from both files
  - write the minimum term and document ID to current merge file
  - move the minimum file from the two one line further (read a line from minimum file)
  - fill the merge file with the remaining file if one of two ended
  - add the merged file to queue
+ at the end we will convert one last merged file that is result of all files and turn its document ID part into document file name that is saved in ``docId_to_doc_map``  and write it in output file

#### clear_output_directory
Here we are going to delete temporary merged files but keep the output
