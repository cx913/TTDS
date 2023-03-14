import boolean_tree as bt
import time

start_time = time.time()
query = '(("cat" AND "dog" OR "hamster") NOT "rabbit") AND (apples OR "pears and bananas" OR "grapefruit"*) AND ("green" OR "yellow" AND ("blue" OR "purple"))'
query_ = '"apple pie" OR *berry OR ((apple OR banana) AND (pie NOT ("orange juice" OR grape))) OR "pear*"'
query__2 = 'tomato AND NOT potato'
tokens = bt.split_query(query__2)
#print(query)
#print(tokens)
tree = bt.build_tree(tokens)
bt.display_tree(tree)
end_time = time.time()
t = end_time - start_time
print(f'{t * 1000} ms')

