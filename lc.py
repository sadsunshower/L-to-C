#!/usr/bin/python3

import re, sys

input_names = []
program_variables = []
program_code = []
program_assertions = []

defs = {}
defs_recursive_base = {}
defs_recursive_rec = {}
defs_functions = {}

test_cases = []


def bool_to_c(bool_expr):
    bool_expr = re.sub(r'&', '&&', bool_expr)
    bool_expr = re.sub(r'\^', '||', bool_expr)
    bool_expr = re.sub(r'=', '==', bool_expr)
    bool_expr = re.sub(r'~', '!', bool_expr)

    return bool_expr


def l_assignment_to_c(l_expr):
    return re.sub(r':=', '=', l_expr)


def l_loop_to_c(l_expr):
    if 'while' in l_expr:
        loop_statement = l_expr.split(' ')
        
        if len(loop_statement) < 3:
            print(f'PARSE ERROR: Malformed while statement {l_expr}')

        return f'while ({bool_to_c(" ".join(loop_statement[1:-1]))}) {{'
    elif 'od' in l_expr:
        return '}'

def l_if_to_c(l_expr):
    if 'if' in l_expr:
        if_statement = l_expr.split(' ')
        
        if len(if_statement) < 3:
            print(f'PARSE ERROR: Malformed if statement {l_expr}')

        return f'if ({bool_to_c(" ".join(if_statement[1:-1]))}) {{'
    elif 'else' in l_expr:
        return '} else {'
    elif 'fi' in l_expr:
        return '}'


def parse_base_rule(rule):
    rhs = rule.split('=')[1].strip()
    lhs = re.search(r'\(([^)]*)\)', rule.split('=')[0]).group(1).split(',')
    
    for i in range(len(lhs)):
        lhs[i] = lhs[i].strip()

    return f'if ({" && ".join([f"(VAR{i} == {lhs[i]})" for i in range(len(lhs))])}) return {rhs};'


def parse_recursive_vars(rule):
    lhs = re.search(r'\(([^)]*)\)', rule.split('=')[0]).group(1).split(',')
    
    for i in range(len(lhs)):
        lhs[i] = lhs[i].strip()

    return lhs


def parse_recursive_rule(name, rule):
    rhs = rule.split('=')[1].strip()
    rhs = rhs.replace(name, 'defined_' + name)
    return f'return {rhs};'


with open(sys.argv[1], 'r') as f:
    lines = f.read().split('\n')
    
    program = False
    maths = False
    test = False

    for i in range(len(lines)):
        t = lines[i].split('|')
        for j in range(len(t)):
            t[j] = t[j].strip()

        if len(t) == 1 and t[0] == '':
            continue

        if lines[i].startswith('INPUT'):
            program = True

            inputs = re.sub(r'\s+', '', t[1])
            input_names = inputs.split(',')

            for i_name in input_names:
                if len(i_name) > 1:
                    print(f'PARSE ERROR: input name {i_name} is too long, only single-letter names are allowed')
                    exit(1)
        
        elif program and len(t) > 1:
            variables = re.findall(r'\b([a-z])\b', t[0])
            for v in variables:
                if v not in program_variables and v not in input_names:
                    program_variables.append(v)

            starting_indent = re.match(r'\s+', lines[i])
            if starting_indent:
                starting_indent = '    ' + starting_indent.group(0)
            else:
                starting_indent = '    '

            if ':=' in lines[i]:
                program_code.append(starting_indent + l_assignment_to_c(t[0]))
            elif 'while' in lines[i] or 'od' in lines[i]:
                program_code.append(starting_indent + l_loop_to_c(t[0]))
            elif 'if' in lines[i] or 'else' in lines[i] or 'fi' in lines[i]:
                program_code.append(starting_indent + l_if_to_c(t[0]))
            elif re.search(r'^\s*$', t[0]):
                program_code.append('')
            
            program_assertions.append(bool_to_c(t[1]))

        elif lines[i].startswith('MATHS'):
            maths = True
            program = False
        
        elif maths and len(t) > 1:
            name = t[1][0]
            if name not in defs:
                defs[name] = []

            if t[0] == 'B':
                if name not in defs_recursive_base:
                    defs_recursive_base[name] = []

                defs_recursive_base[name].append(parse_base_rule(t[1]))
            elif t[0] == 'R':
                defs_recursive_rec[name] = parse_recursive_rule(name, t[1])

                defs[name] = parse_recursive_vars(t[1])
            elif t[0] == 'F':
                defs_functions[name] = t[1].split('=')[1].strip()

                defs[name] = parse_recursive_vars(t[1])
            elif t[0] == 'P':
                defs_functions[name] = bool_to_c(t[1].split(':')[1].strip())

                defs[name] = parse_recursive_vars(t[1].replace(':', '='))
        
        elif lines[i].startswith('TEST'):
            test = True
            maths = False
        
        elif test:
            inputs = lines[i].split(',')
            test_case = {}

            for i in inputs:
                lhs = i.split('=')[0].strip()
                rhs = i.split('=')[1].strip()
                test_case[lhs] = rhs

            test_cases.append(test_case)

    print('// Generated by Nicc\'s lc.py\n')

    print('#include <stdio.h>\n#include <assert.h>\n\n#define TRUE 1\n#define FALSE 0\n')

    for d in defs:
        print(f'int defined_{d}({", ".join(["int " + x for x in defs[d]])})\n{{')
        if d in defs_functions:
            print(f'    return {defs_functions[d]};')
            print('}\n')
        else:
            for b in defs_recursive_base[d]:
                for i in range(len(defs[d])):
                    b = b.replace('VAR' + str(i), defs[d][i])
                print(f'    {b}')
            print(f'    {defs_recursive_rec[d]}')
            print('}\n')
    
    for i in range(len(program_code)):
        for d in defs:
            program_code[i] = re.sub(r'\b' + d + r'\b', f'defined_{d}', program_code[i])
    
    for i in range(len(program_assertions)):
        for d in defs:
            program_assertions[i] = re.sub(r'\b' + d + r'\b', f'defined_{d}', program_assertions[i])
    
    print('void prog(' + ', '.join(['int ' + x for x in input_names]) + ')\n{')

    print('    printf("INPUT STATE\\n");')
    for i_name in input_names:
        print(f'    printf("{i_name} = %d\\n", {i_name});')

    print('    int ' + ', '.join(program_variables) + ';\n')

    indent = max([len(x) for x in program_code]) + 3
    for i in range(len(program_code)):
        remaining_indent = indent - len(program_code[i])
        print(program_code[i] + (' ' * remaining_indent) + f'assert({program_assertions[i]});')

    print('\n    printf("OUTPUT STATE\\n");')
    for i_name in input_names:
        print(f'    printf("{i_name} = %d\\n", {i_name});')
    for v in program_variables:
        print(f'    printf("{v} = %d\\n", {v});')

    print('}')

    print('\nint main(void)\n{')

    i = 1
    for t in test_cases:
        print(f'    printf("=== TEST CASE {i} ===\\n");')
        print(f'    prog({", ".join([t[n] for n in input_names])});\n')

        i += 1
    
    print('    return 0;\n}')