import pickle
import math
from . import boolean_tree as bt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def bm25(term_freq, doc_len, doc_freq, num_docs, k1=1.2, b=0.75):
    """
    Calculates the BM25 score for a term in a document.

    Args:
        term_freq (int): The frequency of the term in the document.
        doc_len (int): The length of the document in words.
        doc_freq (int): The number of documents that contain the term.
        num_docs (int): The total number of documents in the corpus.
        k1 (float, optional): The k1 parameter. Default is 1.2.
        b (float, optional): The b parameter. Default is 0.75.

    Returns:
        float: The BM25 score for the term in the document.
    """
    idf = math.log((num_docs - doc_freq + 0.5) / (doc_freq + 0.5))
    tf_weight = ((k1 + 1) * term_freq) / (k1 * ((1 - b) + (b * (doc_len / num_docs))) + term_freq)
    return idf * tf_weight

def term_query(term, term_freq, doc_len, doc_num):
    # Binary search is built in system address search
    address = BASE_DIR / 'doc_index' / term
    try:
        with open(address, "rb") as f:
            inverse_index = pickle.load(f)
    except:
        print("Inverse_Index not found")
        return {}
    bm25_scores={}
    doc_freq = len(inverse_index)
    for id in inverse_index.keys():
        bm25_scores[id] = bm25(term_freq[term][id], doc_len[id], doc_freq, doc_num)

    return set(sorted(bm25_scores, reverse=True))


def tree_traverse(tree):
    # and condition
    if tree.value == 'AND':
        return tree_traverse(tree.left) & tree_traverse(tree.right)
    elif tree.value == 'OR':
        return tree_traverse(tree.left) | tree_traverse(tree.right)
    elif isinstance(tree, str):
        return term_query(tree)

#def tree_query(query):
    #tokens = bt.split_query(query)
    #tree = bt.build_tree(tokens)
    #if isinstance(s, str)


# test
# load frequency, doc lengths, doc number
# term_frequency_address = BASE_DIR / 'doc_index' / 'term_frequency'
# doc_len_address = BASE_DIR / 'doc_index' / 'doc_len'
# num_docs = BASE_DIR / 'doc_index' / 'num_docs'
#
# with open(term_frequency_address, "rb") as f:
#     term_frequency = pickle.load(f)
# with open(doc_len_address, "rb") as f:
#     doc_len = pickle.load(f)
# with open(num_docs, "rb") as f:
#     doc_num = pickle.load(f)
#
# query = 'tomato'
#
# ir_list = term_query(query, term_frequency, doc_len,  doc_num)
# print(ir_list)