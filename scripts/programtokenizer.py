import tokenize
import re
from io import BytesIO
import ast
import astunparse
import clang.cindex
import clang.enumerations


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


def tokenize_file(program_as_string):
    variables_tokenized, _ = NameTokenizer(utf8char).tokenize(program_as_string)
    syntax_tokenized = SyntaxTokenizer(word_to_token).tokenize(variables_tokenized)
    return syntax_tokenized


def untokenize_string(string, token_to_name):
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




def tokenize_c(text):
    def comment_remover(text):
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return ""
            else:
                return s

        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        return re.sub(pattern, replacer, text)


    text = comment_remover(text)
    index = clang.cindex.Index.create()
    tu = index.parse("C:\\Users\\Buster\\Documents\\Code\\CBT\\new.c")
    print(tu.spelling)
    tokens = tu.cursor.get_tokens()
    processed_tokens = []
    for token in tokens:
        # print("extent: {}, {}".format(token.extent, dir(token.extent)))
        # print("int_data: {}, {}".format(token.int_data, dir(token.int_data)))
        # print("kind: {}, {}".format(token.kind, dir(token.kind)))
        # print("location: {}, {}".format(token.location, dir(token.location)))
        # print("ptr_data: {}, {}".format(token.ptr_data, dir(token.ptr_data)))
        # print("spelling: {}, {}".format(token.spelling, dir(token.spelling)))
        # print("=======================================================================================================")
        processed_tokens.append(token.spelling)
        print("{} {}".format(token.spelling, token.kind))
    print("".join(processed_tokens))

