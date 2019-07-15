from iteratortools import *
from comment_filter import *
from comment_filter import language
import re


ERROR_LOG_FILE = os.path.join(ERROR_LOG_PATH, 'stripcomments.csv')


def strip_comments(file_path):
    code_only = []
    with open(generalize_path(os.path.join(DATA_PATH, file_path)), 'r+', encoding='utf8') as file:
        for l in parse_file(language.python, file.readlines(), code_only=True):
            if not re.match(r'^ +$', l):
                code_only.append(l)
    with open(generalize_path(os.path.join(DATA_PATH, file_path)), 'w+', encoding='utf8') as file:
        file.writelines(code_only)


if __name__ == '__main__':
    err_no = 0

    content = get_file_paths()

    iterate(strip_comments, ERROR_LOG_FILE, content)