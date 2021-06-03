
class PostingList:
    term_id: int
    postings: list[int]

    def __init__(self, term_id: int, postings: list[int]):
        self.term_id = term_id
        self.postings = postings

    def __init__(self, term_id: int):
        self.term_id = term_id
        self.postings = []
