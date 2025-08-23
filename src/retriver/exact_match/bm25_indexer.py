import bm25s
import Stemmer
from pypdf import PdfReader

# tokenizer function
def tokenize_corpus(corpus, stemmer_type: str = 'english') -> any:
    """Tokenizes the input corpus using the specified stemmer.

    Args:
        corpus (list of str): The input documents to tokenize.
        stemmer_type (str, optional): The type of stemmer to use. Defaults to 'english'.

    Returns:
        list of list of str: The tokenized corpus.
    """
    stemmer = Stemmer.Stemmer(stemmer_type)
    tokens = bm25s.tokenize(
        texts=corpus, stopwords='en', stemmer=stemmer)
    return tokens

def create_search_index(tokens, stemmer_type: str = 'english') -> bm25s.BM25:
    """Creates a BM25 search index from the input corpus.

    Args:
        corpus (list of str): The input documents to index.
        stemmer_type (str, optional): The type of stemmer to use. Defaults to 'english'.

    Returns:
        bm25s.BM25: The created BM25 search index.
    """
    retriever = bm25s.BM25()
    retriever.index(tokens)
    return retriever

def save_search_index(index, file_path: str):
    """Saves the BM25 search index to a file.

    Args:
        index (bm25s.BM25): The BM25 search index to save.
        file_path (str): The path to the file where the index should be saved.
    """
    index.save(file_path)
    
def run_indexing() -> None:
    """Runs the indexing process for the BM25 search index."""
    # read pdf file from the disk
    pdf_path = "/home/kosala/git-repos/contract_inspect/data/Oracle_contract.pdf"
    pdf_reader = PdfReader(pdf_path)
    
    corpus = [page.extract_text() for page in pdf_reader.pages]
    tokens = tokenize_corpus(corpus)
    index = create_search_index(tokens)
    
    print(0)

if __name__ == "__main__":
    # TODO: use actual document instead
    # corpus = [
    #     "a cat is a feline and likes to purr",
    #     "a dog is the human's best friend and loves to play",
    #     "a bird is a beautiful animal that can fly",
    #     "a fish is a creature that lives in water and swims",
    # ]
    run_indexing()
    # tokens = tokenize_corpus(corpus)
    # index = create_search_index(corpus)
    
    print("end of the program")