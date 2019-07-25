import tokenize
import re
from io import BytesIO
import ast
import astunparse


words = ['eof', 'if', '\n', '    ', 'for', 'while', ':', 'False', 'None', 'True', 'and', 'as', 'assert', 'break',
         'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'from', 'global', 'import', 'in', 'is',
         'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'with', 'yield', 'dedent', 'indent',
         'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes', 'callable', 'chr', 'classmethod', 'compile',
         'complex', 'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter', 'float', 'format',
         'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance',
         'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object', 'oct',
         'open', 'ord', 'pow', 'print', 'property', 'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
         'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip', '__import__']


word_to_token = {}
utf8char = 1286
for word in words:
    word_to_token[word] = chr(utf8char)
    utf8char += 1


token_to_word = {v: k for k, v in word_to_token.items()}


class NameTokenizer:
    class Transformer(ast.NodeTransformer):
        def __init__(self):
            self.var_count = 0
            self.visited = {}

        def visit_Name(self, node: ast.Name):  # Needs to be capital 'N'
            # TODO: actually use utf8 tokens or something instead of v1, v2
            if node.id not in self.visited:
                var_name = 'v' + str(self.var_count)
                self.visited[node.id] = var_name
                self.var_count += 1
            else:
                var_name = self.visited[node.id]
            return ast.copy_location(ast.Name(id=var_name), node)

    @staticmethod
    def tokenize(program_as_string):
        tree = ast.parse(program_as_string)

        transformer = NameTokenizer.Transformer()
        transformer.visit(tree)

        return astunparse.unparse(tree)


class SyntaxTokenizer:
    @staticmethod
    def tokenize(program_as_string):
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
                result += word_to_token['dedent']
            elif toknum == tokenize.INDENT:
                result += word_to_token['indent']
            else:
                try:
                    result += word_to_token[tokval]
                except KeyError:
                    result += tokval
                finally:
                    str_index += word_len

        return result


def tokenize_file(program_as_string):
    variables_done = NameTokenizer.tokenize(program_as_string)
    print(variables_done)
    syntax_done = SyntaxTokenizer.tokenize(variables_done)
    print(syntax_done)
    return syntax_done


def untokenize_string(string):
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

    return formatted


def split_tokenized_files(string):
    return string.split(word_to_token['eof'])
