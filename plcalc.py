#!/usr/bin/env python3
from string import ascii_uppercase

while True:
    choice = input(f'Welcome to the Propositional Logic Calculator!\n'
                   f"Enter '1' to check if a sentence is a tautology, contradiction, or contingent.\n"
                   f"Enter '2' to check if a set of sentences is consistent/satisfiable.\n"
                   f"Enter '3' to check if an argument is valid.\n"
                   f'> ')
    print('\033[H\033[J', end='')    # Clears the screen.
    if choice == '1':
        print(f'Checking if a sentence is a tautology, contradiction, or contingent.\n'
              f'Enter a well-formed formula.\n')
        while True:
            line = input('1: ')
            if line:
                sentences = [line]
                break
            else:
                print('Enter a well-formed formula.\n')
        break
    elif choice in ('2', '3'):
        if choice == '2':
            print(f'Checking if a set of sentences is consistent/satisfiable.\n'
                  f'Enter an empty line to stop.\n')
        elif choice == '3':
            print(f'Checking if an argument is valid.\n'
                  f'Enter an empty line to stop.\n'
                  f'The last sentence entered is the conclusion.\n')
        sentences = []
        i = 1
        while True:
            line = input(f'{i}: ')
            if line:
                sentences.append(line)
            elif not sentences:
                print('Enter at least one well-formed formula.\n')
                continue
            else:
                break
            i += 1
        break
    print('Invalid input.\n')
print('\033[H\033[J', end='')    # Clears the screen.

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

if choice == '1':
    if all(table[i][0][outputs[0][-1][1]] == 'T' for i in range(2**len(letters))):
        print(f'\n{sentences[0]} is a tautology.')
    elif all(table[i][0][outputs[0][-1][1]] == 'F' for i in range(2**len(letters))):
        print(f'\n{sentences[0]} is a contradiction.')
    else:
        print(f'\n{sentences[0]} is contingent.')
elif choice == '2':
    consistent = []
    for i in range(2**len(letters)):
        if all(table[i][j][outputs[j][-1][1]] == 'T' for j in range(len(sentences))):
            consistent.append(i)
    print('\nThe set {' + ", ".join(sentences) + '} is', 'consistent.' if consistent else 'inconsistent.')
    if consistent:
        print('\nThese models satisfy the set:\n')
        header = ' | '.join([' '.join(letters)] + sentences)
        print(header)
        print(''.join('+' if x == '|' else '-' for x in header))
        for i in consistent:
            print(*models[i].values(), '|', ' | '.join(''.join(str(x) for x in subrow) for subrow in table[i]))
elif choice == '3':
    counterexamples = []
    for i in range(2**len(letters)):
        if all(table[i][j][outputs[j][-1][1]] == 'T' for j in range(len(sentences)-1)) and table[i][-1][outputs[-1][-1][1]] == 'F':
            counterexamples.append(i)
    print('\nThe argument\n')
    for sentence in sentences[:-1]:
        print('  ' + sentence)
    print('∴', sentences[-1])
    print('\nis', 'invalid.' if counterexamples else 'valid.')
    if counterexamples:
        print('\nThese models are counterexamples:\n')
        header = ' | '.join([' '.join(letters)] + sentences)
        print(header)
        print(''.join('+' if x == '|' else '-' for x in header))
        for i in counterexamples:
            print(*models[i].values(), '|', ' | '.join(''.join(str(x) for x in subrow) for subrow in table[i]))
