import pickle
import math
from . import boolean_tree as bt
#import boolean_tree as bt
from pathlib import Path
from nltk.stem.snowball import SnowballStemmer

BASE_DIR = Path(__file__).resolve().parent


def nutrition_test(query, exact_value):
    # empty always true
    if query == '':
        return True
    if len(query) < 2:
        return False
    if query[:2] == '>=':
        value = float(''.join((c for c in query[1:] if c.isdigit())))
        # check nan
        if value != value:
            return False
        return exact_value >= value
    elif query[:2] == '<=':
        value = ''.join((c for c in query[1:] if c.isdigit()))
        # check nan
        if value == '':
            return False
        value = float(value)
        return exact_value <= value
    elif query[0] == '=':
        value = float(''.join((c for c in query[1:] if c.isdigit())))
        # check nan
        if value == '':
            return False
        value = float(value)
        return exact_value == value
    elif query[0] == '<':
        value = float(''.join((c for c in query[1:] if c.isdigit())))
        # check nan
        if value == '':
            return False
        value = float(value)
        return exact_value < value
    elif query[0] == '>':
        value = float(''.join((c for c in query[1:] if c.isdigit())))
        # check nan
        if value == '':
            return False
        value = float(value)
        return exact_value > value
    else:
        # wrong grammar
        return False
def merge_dict(b, x, y):
    z = {}
    if b == 'and':
        for key, value in x.items():
            if key in x.keys() and key in y.keys():
                z[key] = y[key] + x[key]
        return z
    elif b == 'or':
        for key, value in x.items():
            if key in x.keys() and key in y.keys():
                z[key] = y[key] + x[key]
            else:
                z[key] = x[key]
        for key, value in y.items():
            if key not in z:
                z[key] = y[key]
        return z
    elif b == 'not':
        for key, value in x.items():
            if key not in y.keys():
                z[key] = x[key]
        return z


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
    # temp stem, remove when merge into tree
    stemmer = SnowballStemmer("english")
    terms = stemmer.stem(term)
    # Binary search is built in system address search
    address = BASE_DIR / 'doc_index' / term
    try:
        with open(address, "rb") as f:
            inverse_index = pickle.load(f)
    except:
        print("Inverse_Index not found")
        return {}
    bm25_scores = {}
    doc_freq = len(inverse_index)
    for id in inverse_index.keys():
        bm25_scores[id] = bm25(term_freq[term][id], doc_len[id], doc_freq, doc_num)

    return bm25_scores


def phrase_query(terms, term_freq, doc_len, doc_num):
    # Binary search is built in system address search
    inverse_index_list = []
    for term in terms:
        address = BASE_DIR / 'doc_index' / term
        try:
            with open(address, "rb") as f:
                inverse_index = pickle.load(f)
                inverse_index_list.append(inverse_index)
        except:
            print("Inverse_Index not found")
            return {}
    valid_doc_id = []
    bm25_scores = {}
    for doc, pos_list in inverse_index_list[0].items():
        for pos in pos_list:
            cur_pos = pos
            for inverse_index in inverse_index_list[1:]:
                if inverse_index.get(doc):
                    if inverse_index.get(doc) - cur_pos == 1:
                        cur_pos = inverse_index.get(doc)
                    else:
                        return {}
                else:
                    return {}
        valid_doc_id.append(doc)
    for i in range(0, len(inverse_index_list)):
        doc_freq = len(inverse_index_list[i])
        for id in valid_doc_id:
            if bm25_scores.get(id):
                bm25_scores[id] += bm25(term_freq[terms[i]][id], doc_len[id], doc_freq, doc_num)
            else:
                bm25_scores[id] = bm25(term_freq[terms[i]][id], doc_len[id], doc_freq, doc_num)
    return bm25_scores


def proximity_query(term1, term2, distance, term_freq, doc_len, doc_num):
    # Binary search is built in system address search
    address1 = BASE_DIR / 'doc_index' / term1
    try:
        with open(address1, "rb") as f:
            inverse_index1 = pickle.load(f)
    except:
        print("Inverse_Index not found")
        return {}
    address2 = BASE_DIR / 'doc_index' / term2
    try:
        with open(address2, "rb") as f:
            inverse_index2 = pickle.load(f)
    except:
        print("Inverse_Index not found")
        return {}

    bm25_scores1 = {}
    doc_freq1 = len(inverse_index1)
    for id in inverse_index1.keys():
        bm25_scores1[id] = bm25(term_freq[term1][id], doc_len[id], doc_freq1, doc_num)

    bm25_scores2 = {}
    doc_freq2 = len(inverse_index1)
    for id in inverse_index2.keys():
        bm25_scores2[id] = bm25(term_freq[term2][id], doc_len[id], doc_freq2, doc_num)

    bm25_scores_p = {}
    for key, value in bm25_scores1.items():
        if key in bm25_scores1.keys() and key in bm25_scores2.keys():
            for pos_1 in inverse_index1[key]:
                for pos_2 in inverse_index2[key]:
                    if abs(pos_1 - pos_2) <= distance:
                        bm25_scores_p[key] = bm25_scores1[key] + bm25_scores2[key]
    return bm25_scores_p


def tree_traverse(tree, term_freq, doc_len, doc_num):
    stemmer = SnowballStemmer("english")
    if isinstance(tree, str):
        if tree.find('"') != -1 or tree.find("'") != -1:
            phrase = tree.replace('"', '').replace("'", '')
            terms = phrase.split()
            terms = [stemmer.stem(x) for x in terms]
            return phrase_query(terms, term_freq, doc_len, doc_num)
        elif tree.find('#') != -1:
            terms = tree.split('#')
            terms[0] = stemmer.stem(terms[0])
            terms[1] = stemmer.stem(terms[1])
            return proximity_query(terms[0], terms[1], terms[2], term_freq, doc_len, doc_num)
        else:
            term = stemmer.stem(tree)
            return term_query(term, term_freq, doc_len, doc_num)
    else:
        return merge_dict(tree.value, tree_traverse(tree.left, term_freq, doc_len, doc_num),
                          tree_traverse(tree.right, term_freq, doc_len, doc_num))


def tree_query(query, term_freq, doc_len, doc_num):
    tokens = bt.split_query(query)
    tree = bt.build_tree(tokens)
    final_scores = tree_traverse(tree, term_freq, doc_len, doc_num)
    return final_scores
# test
# load frequency, doc lengths, doc number
# term_frequency_address = BASE_DIR / 'doc_index' / 'term_frequency'
# doc_len_address = BASE_DIR / 'doc_index' / 'doc_len'
# num_docs = BASE_DIR / 'doc_index' / 'num_docs'
# # #
# with open(term_frequency_address, "rb") as f:
#     term_frequency = pickle.load(f)
# with open(doc_len_address, "rb") as f:
#     doc_len = pickle.load(f)
# with open(num_docs, "rb") as f:
#     doc_num = pickle.load(f)
# #
# term1 = 'burger'
# term2 = 'onion'
# terms = ['fish']
# c_query = 'fucksao'
# bm_list = dict(sorted(term_query(c_query, term_frequency, doc_len,  doc_num).items(), key=lambda kv: kv[1], reverse=True))
# #bm_list = dict(sorted(term_query(term1, term_frequency, doc_len,  doc_num).items(), key=lambda kv: kv[1], reverse=True))
# ir_list = set(bm_list)
# #print(bm_list)
# print(bm_list)
# print(ir_list)
