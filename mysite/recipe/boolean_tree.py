import re


class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def split_query(query):
    global tokens
    pattern = r'\(|\)|NOT|AND|OR|\w+|"[^"]*"|\b\w+\*|\*\w+\b'
    if isinstance(query, str):
        tokens = re.findall(pattern, query)
    return tokens


def op_count(tokens, op_count=0):
    operators = ['NOT', 'AND', 'OR']
    for op in operators:
        op_count += tokens.count(op)
    return op_count


def p_stack(tokens):
    lp_stack = []
    rp_stack = []
    if tokens.count('(') == tokens.count(')') != 0:
        # generate index for '(' and ')'
        for i in range(len(tokens)):
            if tokens[i] == '(':
                lp_stack.append(i)
            if tokens[i] == ')':
                rp_stack.append(i)
    return lp_stack, rp_stack


def build_tree(tokens):
    operators = ['NOT', 'AND', 'OR']
    prec = {'NOT': 1, 'AND': 2, 'OR': 3}
    lp_stack, rp_stack = p_stack(tokens)
    op_idx = []
    node_op = None
    tree = None
    left = []
    right = []

    if op_count(tokens) > 0:
        # print(f'lp: {lp_stack}')
        # print(f'rp: {rp_stack}')
        # if query contains parentheses
        if len(lp_stack) == len(rp_stack) != 0:
            # op with lowest prec among parentheses pairs
            # ex. '(...) AND (...) AND (...) OR (...)'
            for i in range(len(lp_stack)):
                if lp_stack[i] > rp_stack[i - 1]:  # end of parentheses pairs found
                    for idx, token in enumerate(tokens[rp_stack[i - 1] + 1: lp_stack[i]]):
                        if token in operators:  # op with lowest prec found among parentheses pairs
                            op_idx.append((token, rp_stack[i - 1] + 1 + idx))  #

            # print(len(op_idx))
            if len(op_idx) < 1:
                # op with lowest prec on left side of parentheses pairs
                # ex. '... AND (... OR (...))'
                if min(lp_stack) > 0 and max(rp_stack) == len(tokens) - 1:
                    for idx, token in enumerate(tokens[:min(lp_stack)]):
                        if token in operators:
                            op_idx.append((token, idx))

                # op with lowest prec on right side of parentheses pairs
                # ex. '(... OR (...)) AND ...'
                if min(lp_stack) == 0 and max(rp_stack) < len(tokens) - 1:
                    for idx, token in enumerate(tokens[max(rp_stack) + 1:]):
                        if token in operators:
                            op_idx.append((token, max(rp_stack) + 1 + idx))

                # op with lowest prec on both left and right sides of parentheses pairs
                # ex. '... OR (...) OR ...'
                if min(lp_stack) > 0 and max(rp_stack) < len(tokens) - 1:
                    for idx, token in enumerate(tokens[:min(lp_stack)]):
                        if token in operators:
                            op_idx.append((token, idx))
                    for idx, token in enumerate(tokens[max(rp_stack) + 1:]):
                        if token in operators:
                            op_idx.append((token, max(rp_stack) + 1 + idx))

        elif tokens.count('(') == tokens.count(')') == 0:
            for idx, token in enumerate(tokens):
                if token in operators:
                    op_idx.append((token, idx))

        else:
            print("Number of parentheses mismatching")
            # print(len(op_idx))
            # print(op_idx)

    # find op with lowest prec if more than one in op_idx
    if len(op_idx) > 0:
        top_prec = 0  # top_prec means the lowest prec
        for op in op_idx:
            if op[0] in prec and prec[op[0]] > top_prec:
                node_op = op
                top_prec = prec[op[0]]

    if node_op is not None:
        left = tokens[:node_op[1]]
        right = tokens[node_op[1] + 1:]

    #
    lp_left, rp_left = p_stack(left)
    lp_right, rp_right = p_stack(right)

    # print(f'op: {node_op}')
    # print(f'left: {left}')
    # print(f'lp: {lp_left}')
    # print(f'rp: {rp_left}')
    # print(f'right: {right}')
    # print(f'lp: {lp_right}')
    # print(f'rp: {rp_right}')

    pr_left = True
    pr_right = True
    if len(lp_left) == len(rp_left) != 0:
        if left[0] == '(' and left[len(left) - 1] == ')':
            for i in range(len(lp_left)):
                if lp_left[i] > rp_left[i - 1]:
                    pr_left = False
                    break
            if pr_left:
                left = left[1:-1]
                # print(f'new left: {left}')
    if len(lp_right) == len(rp_right) != 0:
        if right[0] == '(' and right[len(right) - 1] == ')':
            for i in range(len(lp_right)):
                if lp_right[i] > rp_right[i - 1]:
                    pr_right = False
                    break
            if pr_right:
                right = right[1:-1]
                # print(f'new right: {right}')

    # print('------')

    # build root node of the tree
    tree = Node(tokens[node_op[1]])

    # recursively add nodes to the tree
    if op_count(left) > 0:
        tree.left = build_tree(left)
    else:
        tree.left = left[0]
    if op_count(right) > 0:
        tree.right = build_tree(right)
    else:
        tree.right = right[0]

    return tree


def display_tree(tree, indent=0):
    print('  ' * indent + tree.value)
    if tree.left:
        if isinstance(tree.left, str):
            print('  ' * (indent + 1) + tree.left)
        else:
            display_tree(tree.left, indent + 1)
    if tree.right:
        if isinstance(tree.right, str):
            print('  ' * (indent + 1) + tree.right)
        else:
            display_tree(tree.right, indent + 1)

