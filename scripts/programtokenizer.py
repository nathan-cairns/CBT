import tokenize
import re
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
    'indent': '\u1325',
    'abs': '\u1326',
    'all': '\u1327',
    'any': '\u1328',
    'ascii': '\u1329',
    'bin': '\u1330',
    'bool': '\u1331',
    'bytearray': '\u1332',
    'bytes': '\u1333',
    'callable': '\u1334',
    'chr': '\u1335',
    'classmethod': '\u1336',
    'compile': '\u1337',
    'complex': '\u1338',
    'delattr': '\u1339',
    'dict': '\u1340',
    'dir': '\u1341',
    'divmod': '\u1342',
    'enumerate': '\u1343',
    'eval': '\u1344',
    'exec': '\u1345',
    'filter': '\u1346',
    'float': '\u1347',
    'format': '\u1348',
    'frozenset': '\u1349',
    'getattr': '\u1350',
    'globals': '\u1351',
    'hasattr': '\u1352',
    'hash': '\u1353',
    'help': '\u1354',
    'hex': '\u1355',
    'id': '\u1356',
    'input': '\u1357',
    'int': '\u1358',
    'isinstance': '\u1359',
    'issubclass': '\u1360',
    'iter': '\u1361',
    'len': '\u1362',
    'list': '\u1363',
    'locals': '\u1364',
    'map': '\u1365',
    'max': '\u1366',
    'memoryview': '\u1367',
    'min': '\u1368',
    'next': '\u1369',
    'object': '\u1370',
    'oct': '\u1371',
    'open': '\u1372',
    'ord': '\u1373',
    'pow': '\u1374',
    'print': '\u1375',
    'property': '\u1376',
    'range': '\u1377',
    'repr': '\u1378',
    'reversed': '\u1379',
    'round': '\u1380',
    'set': '\u1381',
    'setattr': '\u1382',
    'slice': '\u1383',
    'sorted': '\u1384',
    'staticmethod': '\u1385',
    'str': '\u1386',
    'sum': '\u1387',
    'super': '\u1388',
    'tuple': '\u1389',
    'type': '\u1390',
    'vars': '\u1391',
    'zip': '\u1392',
    '__import__': '\u1393'
}


token_to_word = {v: k for k, v in word_to_token.items()}


def tokenize_file(string):
    print (string)
    str_index = 0
    result = ''
    g = tokenize.tokenize(BytesIO(string.encode('utf-8')).readline)
    in_tokenized_statement = False
    in_class_or_def = False
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

        if (tokval == 'if' or tokval == 'while' or tokval == 'try' or tokval == 'class' or tokval == 'def' or
                tokval == 'for' or tokval == 'except' or tokval == 'finally' or tokval == 'elif' or tokval == 'else'):
            in_tokenized_statement = True
        if in_tokenized_statement and tokval == ':':
            in_tokenized_statement = False
            in_class_or_def = False

        if tokval == 'class' or tokval == 'def':
            in_class_or_def = True

        if in_tokenized_statement and in_class_or_def and (tokval == '(' or tokval == ')' or tokval == ','):
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
            while line.startswith(word_to_token['dedent']):
                indent_level -= 1
                line = line[1:]
        indents = ''.join('    ' for _ in range(indent_level))
        formatted_line = indents + line
        # TODO: recreate brackets and commas
        formatted += formatted_line + '\n'


    for t in token_to_word:
        formatted = formatted.replace(t, token_to_word[t])

    return formatted


def split_tokenized_files(string):
    return string.split(word_to_token['eof'])
