import tokenize
import os
from io import BytesIO
import iteratortools as it

word_to_token = {
    'eof': '\u1286',
    'if': '\u1287',
    '\n': '\u1288',
    '\t': '\u1289',
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
    'yield': '\u1323'
}

token_to_word = {v: k for k, v in word_to_token.items()}


def tokenize_file(string):
    g = tokenize.tokenize(BytesIO(string.encode('utf-8')).readline)
    result = []
    for toknum, tokval, _, _, _ in g:
        try:
            result.append((tokenize.NAME, word_to_token[tokval]))
        except KeyError:
            result.append((tokenize.NAME, tokval))

    print('here it is:')
    print(tokenize.untokenize(result))
    untokenize_file(tokenize.untokenize(result))


def untokenize_file(string):
    g = tokenize.tokenize(BytesIO(string.encode('utf-8')).readline)
    result = []
    for t in token_to_word:
        string = string.replace(t, token_to_word[t])

    print("and back:" + string)