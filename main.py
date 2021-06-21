
from BSBI.BSBI_Indexer import BSBI_indexing

if __name__ == '__main__':

    input_dir = "Datasets/input"
    output_dir = "Datasets/output"
    block_size = eval((input("Enter Block size in M-Byte ")))

    block_size *=(1024 ** 2)

    indexer = BSBI_indexing(input_dir, int(block_size), output_dir)
    indexer.making_index()

    deletion_choice =  input("delete block and merged files from output directory? y/n")
    if deletion_choice.lower() == "y":
        indexer.clear_output_directory()


