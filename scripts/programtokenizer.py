import tokenize
import re
from io import BytesIO
import ast
import astunparse
import clang.cindex
import clang.enumerations
import tempfile
import subprocess


TOKEN_RANGE_START = 1286


words = ['eof', 'if', '\n', '    ', 'for', 'while', ':', 'False', 'None', 'True', 'and', 'as', 'assert', 'break',
         'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'from', 'global', 'import', 'in', 'is',
         'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'with', 'yield', 'dedent', 'indent',
         'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes', 'callable', 'chr', 'classmethod', 'compile',
         'complex', 'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter', 'float', 'format',
         'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance',
         'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object', 'oct',
         'open', 'ord', 'pow', 'print', 'property', 'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
         'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip', '__import__', 'self']


word_to_token = {}
utf8char = TOKEN_RANGE_START
for word in words:
    word_to_token[word] = chr(utf8char)
    utf8char += 1
var_char_index = utf8char


token_to_word = {v: k for k, v in word_to_token.items()}


def get_var_char_index():
    return var_char_index


class NameTokenizer:
    def __init__(self, start_token):
        self.start_token = start_token

    class Transformer(ast.NodeTransformer):
        def __init__(self, start_token):
            self.name_map = {}
            self.token_num = start_token

        def visit_Name(self, node: ast.Name):  # Needs to be capital 'N'
            # TODO: actually use utf8 tokens or something instead of v1, v2
            if node.id not in self.name_map:
                var_name = chr(self.token_num)
                self.name_map[node.id] = var_name
                self.token_num += 1
            else:
                var_name = self.name_map[node.id]
            return ast.copy_location(ast.Name(id=var_name), node)

    def tokenize(self, program_as_string):
        was_altered = False
        try:
            tree = ast.parse(program_as_string)
        except SyntaxError:
            was_altered = True
            tree = ast.parse(program_as_string.strip() + ' print(a)')

        transformer = NameTokenizer.Transformer(self.start_token)
        transformer.visit(tree)

        if was_altered:
            unparsed = astunparse.unparse(tree)[:-5]  # All but the last 'p(a)' symbols
        else:
            unparsed = astunparse.unparse(tree)
        return unparsed, transformer.name_map


class SyntaxTokenizer:
    def __init__(self, word_to_token):
        self.word_to_token = word_to_token

    def tokenize(self, program_as_string):
        str_index = 0
        result = ''
        g = tokenize.tokenize(BytesIO(program_as_string.encode('utf-8')).readline)
        in_class_or_def = False
        for toknum, tokval, _, _, _ in g:
            if toknum == 59:
                continue
            word_len = len(tokval)

            substr = program_as_string[str_index:str_index + word_len]
            spaces_num = 0
            while substr != tokval:
                result += program_as_string[str_index]
                str_index += 1
                substr = program_as_string[str_index:str_index + word_len]
                spaces_num += 1
                if spaces_num == 4:
                    spaces_num = 0
                    result = result[:-4]
                    # result += word_to_token['    ']

            if tokval == ':':
                in_class_or_def = False
            if tokval == 'class' or tokval == 'def':
                in_class_or_def = True
            if in_class_or_def and (tokval == '(' or tokval == ')' or tokval == ','):
                result += ' '
                str_index += 1
                continue

            # TODO: remove the indenting token
            if toknum == tokenize.DEDENT:
                result += self.word_to_token['dedent']
            elif toknum == tokenize.INDENT:
                result += self.word_to_token['indent']
            else:
                try:
                    result += self.word_to_token[tokval]
                except KeyError:
                    result += tokval
                finally:
                    str_index += word_len

        return result[:-1]  # all but last char which will always be a dedent


def tokenize_python(program_as_string):
    print(program_as_string)
    # If the program string comes with a bunch of silly extra indents, get rid of them!
    indent_level = 0
    char = program_as_string[0]
    while char == ' ':
        indent_level += 1
        char = program_as_string[indent_level]
    print('->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>' + str(indent_level))
    print("bcgdevcgfuvu")  # TODO: Deffos fix this if you wanna train python lol
    variables_tokenized, _ = NameTokenizer(utf8char).tokenize(program_as_string)
    syntax_tokenized = SyntaxTokenizer(word_to_token).tokenize(variables_tokenized)
    return syntax_tokenized


def untokenize_python(string, token_to_name):
    def remove_all(array, item):
        while item in array:
            array.remove(item)
        return array

    def apply_syntax(raw_tokens):
        if len(raw_tokens) is 0:
            return
        name = raw_tokens[0]
        if len(raw_tokens) is 1:
            return name
        params = raw_tokens[1:]
        new_params_str = ''
        for i, param in enumerate(params):
            new_params_str += param
            if i < len(params) - 1:
                new_params_str += ', '
        return name + '(' + new_params_str + ')'

    class_re = re.compile(word_to_token['class'] + r'([\s\S]*?)' + word_to_token[':'] + word_to_token['\n'])
    def_re = re.compile(word_to_token['def'] + r'([\s\S]*?)' + word_to_token[':'] + word_to_token['\n'])
    for match in re.findall(class_re, string):
        raw = remove_all(match.split(' '), '')
        string = string.replace(match.strip(), apply_syntax(raw))
    for match in re.findall(def_re, string):
        raw = remove_all(match.split(' '), '')
        string = string.replace(match.strip(), apply_syntax(raw))

    formatted = ''
    indent_level = 0
    for line in string.split(word_to_token['\n']):
        if line.startswith(word_to_token['indent']):
            indent_level += 1
            line = line[1:]
        elif line.startswith(word_to_token['dedent']):
            while line.startswith(word_to_token['dedent']):
                indent_level -= 1
                line = line[1:]
        indents = ''.join('    ' for _ in range(indent_level))
        formatted_line = indents + line
        formatted += formatted_line + '\n'

    for t in token_to_word:
        formatted = formatted.replace(t, token_to_word[t])

    for t in token_to_name:
        formatted = formatted.replace(t, token_to_name[t])

    # Final assigning of unmapped variables to new temp variables
    formatted = list(formatted)
    temp_vars = {}
    temp_num = 0
    for i, char in enumerate(formatted):
        if ord(char) >= TOKEN_RANGE_START:
            if char not in temp_vars:
                var_name = 'temp' + str(temp_num)
                temp_vars[char] = var_name
                temp_num += 1
            else:
                var_name = temp_vars[char]
            formatted[i] = var_name

    return ''.join(formatted)


def split_tokenized_files(string):
    return string.split(word_to_token['eof'])



c_keywords = ['auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern',
              'float', 'for', 'goto', 'if', 'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
              'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while', 'strcpy', 'strncpy',
              'strcmp', 'strncmp', 'strlen', 'strcat', 'strncat', 'strchr', 'strrcht', 'strstr', 'strtok', 'calloc',
              'free', 'malloc', 'realloc', 'memcpy', 'memcmp', 'memchr', 'memset', 'memmove', 'tolower', 'toupper',
              'perror', 'strerror', 'printf', 'gets', 'scanf', '==', '!=', '--', '++', '&&', '||', '-=',
              '+=', '*=', '/=', '%=', '&=', '|=', '^=', '<=', '>=', '<=>' '->', '<<', '>>', ]

word_to_token_c = {}
utf8char_c = TOKEN_RANGE_START
for word in c_keywords:
    word_to_token_c[word] = chr(utf8char_c)
    utf8char_c += 1
var_char_index_c = utf8char_c

token_to_word_c = {v: k for k, v in word_to_token_c.items()}

punctuation_mirror = { '=': '=', '-': '-', '+': '+', '&': '&', '|': '|' }

# TODO: tokenize #include <...>


def tokenize_c(text, var_char_index=var_char_index_c):
    def strip_preprocessing(text):
        def comment_replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return ""
            else:
                return s

        def header_replacer(match):
            s = match.group(0)
            return ""

        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        no_comments = re.sub(pattern, comment_replacer, text)
        pattern = re.compile(r'#include<([\s|\S]*?)>')
        return re.sub(pattern, header_replacer, no_comments)

    index = clang.cindex.Index.create()
    text = strip_preprocessing(text)
    f = tempfile.TemporaryFile(mode='r+', suffix='.c')
    f.write(text)
    f.read()
    tu = index.parse(f.name)
    f.close()

    tokens = tu.cursor.get_tokens()
    processed_tokens = []
    variable_names = {}
    last_token = None
    for token in tokens:
        if token.kind.name == 'LITERAL' or \
                token.kind.name == 'KEYWORD':
            try:
                processed_tokens.append(word_to_token_c[token.spelling])
            except KeyError:
                processed_tokens.append(" " + token.spelling)
        elif token.kind.name == 'IDENTIFIER':
            try:
                processed_tokens.append(variable_names[token.spelling])
            except KeyError:
                var_char_index += 1
                processed_tokens.append(chr(var_char_index))
                variable_names[token.spelling] = chr(var_char_index)
        elif token.kind.name == 'PUNCTUATION':
            try:
                try:
                    processed_tokens.append(word_to_token_c[token.spelling])
                except KeyError:
                    # 2 of same punctuation next to each other we can collapse as it mans its own unique thing
                    if last_token and punctuation_mirror[last_token.spelling] == token.spelling:
                        double_punc_as_token = word_to_token_c[last_token.spelling + token.spelling]
                        processed_tokens = processed_tokens[:-1]
                        processed_tokens.append(double_punc_as_token)
                    else:
                        processed_tokens.append(token.spelling)
            except KeyError:
                processed_tokens.append(token.spelling)
        else:
            processed_tokens.append(token.spelling)
        last_token = token

    output = "".join(processed_tokens)
    return output, variable_names


def untokenize_c(text, token_to_name):
    out = text
    for variable in token_to_name:
        out = out.replace(token_to_name[variable], (" " + variable + " "))
    for token in token_to_word_c:
        out = out.replace(token, (" " + token_to_word_c[token]) + " ")

    f = tempfile.TemporaryFile(mode='r+', suffix='.c')
    f.write(out)
    subprocess.call(['./lib/C-Code-Beautifier', f.name, f.name])
    to_return = f.read()
    f.close()

    return to_return
