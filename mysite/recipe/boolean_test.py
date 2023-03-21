import boolean_tree as bt
import time

start_time = time.time()
query = '(("cat" AND "dog" OR "hamster") NOT "rabbit") AND (apples OR "pears and bananas" OR "grapefruit"*) AND ("green" OR "yellow" AND ("blue" OR "purple"))'
query_ = '"apple pie" and banana and pie'
query__2 = 'Yogurt and Parfaits'
tokens = bt.token_split(query_)
#print(query)
#print(tokens)
tree = bt.create_binary_tree(tokens)

end_time = time.time()
t = end_time - start_time
print(f'{t * 1000} ms')

