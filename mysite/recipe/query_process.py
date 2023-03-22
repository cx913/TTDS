import pickle
import math
from . import boolean_tree as bt
#import boolean_tree as bt
from pathlib import Path
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

BASE_DIR = Path(__file__).resolve().parent

stop_words = set(stopwords.words('english'))


def url_process(raw_url):
    if raw_url is None:
        return 'http://img.sndimg.com//food//image//upload//w_512,h_512,c_fit,fl_progressive,q_95//v1//img//recipes//47//91//49//picaYYmb9.jpg'
    else:
        url = raw_url.split('"')
        return url[7]


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
    bm25_scores = {}
    # term index
    for i in range(0, len(terms)-1):
        # distance
        for j in range(1, len(terms)-i):
            if i == 0 and j == 1:
                bm25_scores = proximity_query(terms[i], terms[j+i], j, term_freq, doc_len, doc_num, order=False)
            else:
                new_bm25_scores = proximity_query(terms[i], terms[j+i], j, term_freq, doc_len, doc_num, order=False)
                bm25_scores = merge_dict('and', bm25_scores, new_bm25_scores)
    return bm25_scores


def proximity_query(term1, term2, distance, term_freq, doc_len, doc_num, order=True):
    try:
        d = int(distance)
    except ValueError:
        return {}
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

    doc_freq1 = len(inverse_index1)
    doc_freq2 = len(inverse_index2)

    bm25_scores= {}
    for key in inverse_index1.keys():
        if key in inverse_index2.keys():
            for pos_1 in inverse_index1[key]:
                for pos_2 in inverse_index2[key]:
                    if order:
                        if abs(pos_1 - pos_2) <= d:
                            bm25_scores1 = bm25(term_freq[term1][key], doc_len[key], doc_freq1, doc_num)
                            bm25_scores2 = bm25(term_freq[term2][key], doc_len[key], doc_freq2, doc_num)
                            bm25_scores[key] = bm25_scores1 + bm25_scores2
                    else:
                        if pos_2 - pos_1 <= d:
                            bm25_scores1 = bm25(term_freq[term1][key], doc_len[key], doc_freq1, doc_num)
                            bm25_scores2 = bm25(term_freq[term2][key], doc_len[key], doc_freq2, doc_num)
                            bm25_scores[key] = bm25_scores1 + bm25_scores2

    return bm25_scores


def tree_traverse(tree, term_freq, doc_len, doc_num):
    stemmer = SnowballStemmer("english")
    if tree.left == None:
        if tree.value.find('"') != -1 or tree.value.find("'") != -1:
            phrase = tree.value.replace('"', '').replace("'", '')
            terms = phrase.split()
            terms = [x for x in terms if x not in stop_words]
            terms = [stemmer.stem(x) for x in terms]
            print(terms)
            if len(terms) == 1:
                return term_query(terms[0], term_freq, doc_len, doc_num)
            else:
                return phrase_query(terms, term_freq, doc_len, doc_num)
        elif tree.value.find('#') != -1:
            terms = tree.value[1:].split('#')
            terms[0] = stemmer.stem(terms[0])
            terms[1] = stemmer.stem(terms[1])
            return proximity_query(terms[0], terms[1], terms[2], term_freq, doc_len, doc_num)
        elif tree.value.find(' ') != -1:
            terms = tree.value.split()
            terms = [x for x in terms if x not in stop_words]
            terms = [stemmer.stem(x) for x in terms]
            s = term_query(terms[0], term_freq, doc_len, doc_num)
            for term in terms[1:]:
                s = merge_dict('and', s, term_query(term, term_freq, doc_len, doc_num))
            return s
        else:
            term = stemmer.stem(tree.value)
            return term_query(term, term_freq, doc_len, doc_num)
    else:
        return merge_dict(tree.value, tree_traverse(tree.left, term_freq, doc_len, doc_num),
                          tree_traverse(tree.right, term_freq, doc_len, doc_num))


def tree_query(query, term_freq, doc_len, doc_num):
    tree = bt.build_tree_from_query(query)
    if tree == -1:
        return {}
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
# term1 = '"tuna rice bake"'
# term2 = '#tomato#sauce#3'
# terms = ['fish']
# c_query = 'fucksao'
# bm_list = dict(sorted(tree_query(term1, term_frequency, doc_len,  doc_num).items(), key=lambda kv: kv[1], reverse=True))
# #bm_list = dict(sorted(term_query(term1, term_frequency, doc_len,  doc_num).items(), key=lambda kv: kv[1], reverse=True))
# ir_list = set(bm_list)
# #print(bm_list)
# print(bm_list)
# print(ir_list)
# raw_url = '[{"id":"cb1a684683.jpg","url":"http://assets.epicurious.com/photos/5609a4d662fa7a9917c25748/master/pass/351294_hires.jpg"}]'
#
#
# p = url_process(raw_url)
# print(p)