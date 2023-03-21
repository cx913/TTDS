from threading import stack_size
from typing import Counter
import re

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

def token_split(query):
    # Temporarily replace spaces inside quotes with a placeholder
    placeholder = '___SPACE___'
    inside_quotes = False
    modified_query = ""

    for char in query:
        if char == '"':
            inside_quotes = not inside_quotes

        if char == ' ' and inside_quotes:
            modified_query += placeholder
        else:
            modified_query += char

    # Split the modified query based on the specified delimiters
    tokens = re.split(r'(\sand\s|\sor\s|\snot\s|\()|(\))', modified_query)

    # Filter out empty strings and None values from the tokens list and restore spaces
    tokens = [token.replace(placeholder, ' ') for token in tokens if token and token.strip()]

    # Further split tokens with a single quote and remove extra spaces around operators
    final_tokens = []
    for token in tokens:
        if token.count('"') == 1:
            final_tokens.extend(re.split(r'\s+', token))
        else:
            final_tokens.append(token.strip())

    return final_tokens



def is_valid_query(tokens):
    operators = {"not", "and", "or"}
    previous_token = None

    for idx, token in enumerate(tokens):
        if isinstance(token, Node) or token not in operators:
            if previous_token and previous_token not in operators:
                return False
        elif token in operators:
            if previous_token is None or previous_token in operators:
                return False
            if token == "not" and (idx == len(tokens) - 1 or tokens[idx + 1] == "NOT"):
                return False
            if token in {"and", "or"} and (idx == len(tokens) - 1):
                return False
        previous_token = token

    return True
def build_tree_from_list(tokens):
    if not tokens:
        return None

    if len(tokens) == 1:
        return tokens[0] if isinstance(tokens[0], Node) else Node(tokens[0])

    for op in ["or"]:
        indices = [i for i, token in enumerate(tokens) if token == op]
        if indices:
            index = indices[0]
            root = Node(op)
            root.left = build_tree_from_list(tokens[:index])
            root.right = build_tree_from_list(tokens[index + 1:])
            return root

    for op in ["and"]:
        indices = [i for i, token in enumerate(tokens) if token == op]
        if indices:
            index = indices[0]
            root = Node(op)
            root.left = build_tree_from_list(tokens[:index])
            root.right = build_tree_from_list(tokens[index + 1:])
            return root

    for op in ["not"]:
        indices = [i for i, token in enumerate(tokens) if token == op]
        if indices:
            index = indices[0]
            root = Node(op)
            root.left = build_tree_from_list(tokens[:index])
            root.right = build_tree_from_list(tokens[index + 1:])
            return root

def create_binary_tree(tokens):
    stack = []
    operators = {'not': 3, 'and': 2, 'or': 1}
    
    for token in tokens:
        i = -1
        

        if token == '(':
            stack.append(token)
            print("append ( to list")
          

        elif token == ')':
            i=-1
            count = 0
            while(stack[i] != "("):
                count += 1
                i -= 1
            print("current number before (" + str(count))
            # the case when only one element between brackets
            if count == 1:
                if stack[-1] in operators:
                    print("1")
                    return -1
                else:
                    cur = stack.pop()
                    stack.pop()
                    stack.append(cur)
                    print("2")
                    continue
            # when two elements between brackets
            elif count == 2:
                if (isinstance(stack[-1],str) and stack[-1] not in operators) and (isinstance(stack[-2],str) and stack[-1] not in operators):
                    cur_str = stack[-2] + " " + stack[-1]
                    cur_node = Node(cur_str)
                    stack.pop()
                    stack.pop()
                    stack.pop()
                    stack.append(cur_node)
                    print("3")
                    continue  
                else:
                    print("6")
                    return -1
            # when three elements between brackets
            elif count == 3:
                if (isinstance(stack[-1],str) or isinstance(stack[-1],Node))\
                and (stack[-2] in operators)\
                and (isinstance(stack[-3],str) or isinstance(stack[-3],Node)):
              
                    cur_node = Node(stack[-2])
                    if isinstance(stack[-1],str):
                        cur_right_node = Node(stack[-1])
                    if isinstance(stack[-1], Node):
                        cur_right_node = stack[-1]
                    if isinstance(stack[-3],str):
                        cur_left_node = Node(stack[-3])
                    if isinstance(stack[-3], Node):
                        cur_left_node = stack[-3]
                    cur_node.left = cur_left_node
                    cur_node.right = cur_right_node
                    for i in range(4):
                        stack.pop()
                    stack.append(cur_node)
                    print("4")
                    continue
                elif (isinstance(stack[-1],str) and stack[-1] not in operators)\
                    and (isinstance(stack[-2],str) and stack[-1] not in operators)\
                    and (isinstance(stack[-2],str) and stack[-1] not in operators):
                    cur_str = stack[-1] + " " + stack[-2] + " " + stack[-3]
                    cur_node = Node(cur_str)
                    for i in range(4):
                        stack.pop()
                    stack.append(cur_node)
                    print("5")
                    continue  
                else:
                    print("7")
                    return -1
            elif count > 3:
                flag = False  
                for j in range(-1, -count-1, -1):
                    if (stack[j] in operators) == True:
                        flag = True
             
                if flag == False:
                    cur_str = ""
                    for j in range(-count, 0, 1):
                        cur_str += stack[j]
                        cur_str += " "
                    cur_str.strip()
                    cur_node = Node(cur_str)
                    for j in range(-count, 1, 1):
                        stack.pop()
                    stack.append(cur_node)
                    print(11)
                    continue
            
                else:
                    length = len(stack)
                    if is_valid_query(stack[length-count:length]):
                        cur_node = build_tree_from_list(stack[length-count:length])
                        for j in range(-count, 1, 1):
                            stack.pop()
                            stack.append(cur_node)
                            print("9")
                            continue
                    else:
                        print("10")
                        return -1                            
            else:
                print("8")
                return -1


       
        else:
            stack.append(token)
            
    if len(stack) == 1:
        return stack.pop()
    elif len(stack) > 1:
        if is_valid_query(stack):
            print("14")
            return build_tree_from_list(stack)
        else:
            print("13")
            return -1
    else:
        print("12")
        return -1

def build_tree_from_query(query):
    query_list = token_split(query)
    print(query_list)
    if ('(' in query_list) or (')' in query_list):
        count_left = 0
        count_right = 0
        for token in query_list:
            if token == '(':
                count_left += 1
            if token == ')':
                count_right +=1
            if count_left == count_right:
                return create_binary_tree(query_list)
        else:
            print('left and right brackets not the same number')
            return -1
    else:
        if is_valid_query(query_list):
            return build_tree_from_list(query_list)
        else:
            print("13")
            return -1