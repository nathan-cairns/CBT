import tokenize
from io import BytesIO

word_to_token = {
    'eof': '\u1286',
    'if': '\u1287',
    '\n': '\u1288',
    '    ': '\u1289',
    'for': '\u1290',
    'while': '\u1291',
    ':': '\u1292',
    'False': '\u1294',
    'None': '\u1295',
    'True': '\u1296',
    'and': '\u1297',
    'as': '\u1298',
    'assert': '\u1299',
    'break': '\u1300',
    'class': '\u1301',
    'continue': '\u1302',
    'def': '\u1303',
    'del': '\u1304',
    'elif': '\u1305',
    'else': '\u1306',
    'except': '\u1307',
    'finally': '\u1308',
    'from': '\u1309',
    'global': '\u1310',
    'import': '\u1311',
    'in': '\u1312',
    'is': '\u1313',
    'lambda': '\u1314',
    'nonlocal': '\u1315',
    'not': '\u1316',
    'or': '\u1317',
    'pass': '\u1318',
    'raise': '\u1319',
    'return': '\u1320',
    'try': '\u1321',
    'with': '\u1322',
    'yield': '\u1323',
    'dedent': '\u1324',
    'indent': '\u1325'
}

token_to_word = {v: k for k, v in word_to_token.items()}


def tokenize_file(string):
    str_index = 0
    result = ''
    g = tokenize.tokenize(BytesIO(string.encode('utf-8')).readline)
    for toknum, tokval, _, _, _ in g:
        if toknum == 59:
            continue
        word_len = len(tokval)

        substr = string[str_index:str_index + word_len]
        spaces_num = 0
        while substr != tokval:
            result += string[str_index]
            str_index += 1
            substr = string[str_index:str_index + word_len]
            spaces_num += 1
            if spaces_num == 4:
                spaces_num = 0
                result = result[:-4]
                # result += word_to_token['    ']

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

    print(result)
    print(untokenize_string(result))

    return result + word_to_token['eof']


def untokenize_string(string):
    formatted = ''
    indent_level = 0
    for line in string.split(word_to_token['\n']):
        if line.startswith(word_to_token['indent']):
            indent_level += 1
            line = line[1:]
        elif line.startswith(word_to_token['dedent']):
            indent_level -= 1
            line = line[1:]
        indents = ''.join('    ' for _ in range(indent_level))
        line = indents + line

        formatted += line + '\n'

    for t in token_to_word:
        formatted = formatted.replace(t, token_to_word[t])

    return formatted


def split_tokenized_files(string):
    return string.split(word_to_token['eof'])
