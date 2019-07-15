from iteratortools import *
from comment_filter import *
from comment_filter import language


ERROR_LOG_FILE = os.path.join(ERROR_LOG_PATH, 'stripcomments.csv')


if __name__ == '__main__':
    err_no = 0

    content = get_file_paths()

    print('Stripping files of comments:')
    progress_bar = ProgressBar(0, content.__len__(), prefix='Progress:', suffix='Complete')
    progress_bar.print_progress_bar(0, 0)
    for i, file_path in enumerate(content):
        code_only = []
        try:
            with open(generalize_path(os.path.join(DATA_PATH, file_path)), 'r+', encoding='utf8') as file:
                for l in parse_file(language.python, file.readlines(), code_only=True):
                    code_only.append(l)
            with open(generalize_path(os.path.join(DATA_PATH, file_path)), 'w+', encoding='utf8') as file:
                file.writelines(code_only)
        except Exception as e:
            err_no += 1
            handle_exception(ERROR_LOG_FILE, file_path, 'Error in stripping comments', e)
        finally:
            progress_bar.print_progress_bar(i + 1, err_no)

    if err_no is not 0:
        print('WARN Data pre-processing was unable to process {} files!'.format(err_no))
        print('WARN Refer to log/dataprocessing/stripcomments.csv for more details.')
