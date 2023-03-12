import numpy as np
import json, re
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import pickle

def preprocess(line, stopword_set=None):
    output = []
            # CASE FOLDING
    lowercase_line = line.lower()
            # TOKENIZATION
    tokens = re.findall(r'\b[a-z0-9][a-z0-9]*', lowercase_line)
            # STOPPING
    # noneST_tokens = [x for x in tokens if not x in stopword_set]
            # NORMALISATION
    stop_words = set(stopwords.words('english'))
    stemmer = SnowballStemmer("english")
    # remove stopwords
    tokens = [x for x in tokens if not x.lower() in stop_words]
    stems = [stemmer.stem(x) for x in tokens]
    output.extend(stems)
    return output

# load json file
with open('recipes.json', 'r') as f:
    dataset = json.load(f)

# 2-d dictionary of recipe index
dataset_index = {}
# 2-d dictionary for term frequency
term_frequency = {}
# 1-d document length
doc_len = {}
# integer for doc frequency
num_docs = 0


for data in dataset:
#    print(f"id: {data['id']}")
#    print(f"title: {data['title']}, ingredients: {data['ingredients']}, instructions: {data['instructions']}")
    num_docs += 1
    if num_docs % 10000 == 0:
        print('current state: {}'.format(num_docs))
    # store id

    doc_id = data['id']

    title = data['title']
    instructions = ', '
    for d in data['instructions']:
        instructions += d['text'] + ' '

#   print(title, ingredients, instructions)
#   combine title and instructions

    text = title + instructions
    processed_text = preprocess(text)
    position_index = 1


# store doc_len
    doc_len[doc_id] = len(processed_text)

    for token in processed_text:

    # term_frequency


    # dataset_index
        if token in dataset_index:
            if doc_id in dataset_index[token]:
                dataset_index[token][doc_id].append(position_index)
                term_frequency[token][doc_id] += 1
            else:
                dataset_index[token][doc_id] = [position_index]
                term_frequency[token][doc_id] = 1
        else:
            # create new token
            term_frequency[token] = {}
            term_frequency[token][doc_id] = 1
            dataset_index[token] = {}
            dataset_index[token][doc_id] = [position_index]
        position_index += 1

    # restriction for test
    #if num_docs == 5:
       # break

for key, value in dataset_index.items():
    with open('./doc_index/' + key, 'wb') as f:
        pickle.dump(value, f)

with open('./doc_index/term_frequency', 'wb') as f:
    pickle.dump(term_frequency, f)

with open('./doc_index/doc_len', 'wb') as f:
    pickle.dump(doc_len, f)

with open('./doc_index/num_docs', 'wb') as f:
    pickle.dump(num_docs, f)
#print(dataset_index)
#print(len(dataset_index))