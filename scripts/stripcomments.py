from iteratortools import *
from comment_filter import *
from comment_filter import language


if __name__ == '__main__':
    #content = get_file_paths() TODO: Uncomment when data in place again
    content = ['..\\test.py']
    print('Stripping files of comments:')

    progress_bar = ProgressBar(0, content.__len__(), prefix='Progress:', suffix='Complete')
    progress_bar.print_progress_bar(0)
    for i, f in enumerate(content):
        code_only = []
        try:
            with open(generalize_path(os.path.join(DATA_PATH, f)), 'r+', encoding='utf8') as file:
                for l in parse_file(language.python, file.readlines(), code_only=True):
                    code_only.append(l)
            with open(generalize_path(os.path.join(DATA_PATH, f)), 'w+', encoding='utf8') as file:
                file.writelines(code_only)
        except OSError as e:
            a = 1
        finally:
            progress_bar.print_progress_bar(i + 1)