#!/usr/bin/env python3
from string import ascii_uppercase

#sentences = ['(P > Q)', 'P', 'Q', '(((P > Q) ^ P) > Q)']
sentences = ['(-(A ^ B) v (-C v --D))', '---((B v C) v -A)', '(C > D)']
#                   AB^-C-D--vv              BCvA-v---

def parse(sentence):
    # -- : keep adding negations to negs
    # -( : wait until you see matching ) to add all negations to output
    # -A : add all negations to output immediately
    line = [(x, i) for i, x in enumerate(sentence)][::-1]
    output = []
    op_stack = []
    neg_brackets = []
    while line:
        token = line.pop()
        if token[0] in ascii_uppercase:
            output.append(token)
        elif token[0] in ('v', '^', '>', '='):
            op_stack.append(token)
        elif token[0] == '(':
            op_stack.append(token)
            neg_brackets.append([])
        elif token[0] == ')':
            while op_stack:
                op = op_stack.pop()
                if op[0] == '(':
                    output.extend(neg_brackets.pop()[::-1])
                    break
                else:
                    output.append(op)
        elif token[0] == '-':
            negs = []
            while token[0] == '-':
                negs.append(token)
                token = line.pop()
            if token[0] == '(':
                op_stack.append(token)
                neg_brackets.append(negs)
            elif token[0] in ascii_uppercase:
                output.append(token)
                output.extend(negs[::-1])
            else:
                print('Negating something weird.')
    return output

outputs = [parse(sentence) for sentence in sentences]
letters = sorted(set(x for x in ''.join(sentences) if x in ascii_uppercase))
models = []
table = []
for i in range(2**len(letters)-1, -1, -1):
    truthrow = format(i, '0' + str(len(letters)) + 'b')
    truths = {letter: int(val) for letter, val in zip(letters, truthrow)}
    models.append(truths)
    row = []
    for sentence, output in zip(sentences, outputs):
        subrow = [' ' for _ in range(len(sentence))]
        stack = []
        for cur in output:
            if cur[0] == '-':
                stack.append(int(not stack.pop()))
            elif cur[0] == 'v':
                q, p = stack.pop(), stack.pop()
                stack.append(int(p or q))
            elif cur[0] == '^':
                q, p = stack.pop(), stack.pop()
                stack.append(int(p and q))
            elif cur[0] == '>':
                q, p = stack.pop(), stack.pop()
                stack.append(int((not p) or q))
            elif cur[0] == '=':
                q, p = stack.pop(), stack.pop()
                stack.append(int(p == q))
            else:
                stack.append(truths[cur[0]])
            subrow[cur[1]] = stack[-1]
        row.append(subrow)
    table.append(row)

# Making the result column distinct from the other columns.
for i in range(2**len(letters)):
    for j in range(len(sentences)):
        table[i][j][outputs[j][-1][1]] = 'T' if table[i][j][outputs[j][-1][1]] else 'F'

# Displays the table.
header = ' | '.join([' '.join(letters)] + sentences)
print(header)
print(''.join('+' if x == '|' else '-' for x in header))
for model, row in zip(models, table):
    print(*model.values(), '|', ' | '.join(''.join(str(x) for x in subrow) for subrow in row))
