from BSBI.BSBI_Indexer import BSBI_indexing

if __name__ == '__main__':
    input_dir = "Datasets/input+"
    output_dir = "Datasets/output"
    block_size = 20 * (1024 ** 2)

    indexer = BSBI_indexing(input_dir, int(block_size), output_dir)
    indexer.making_index()
