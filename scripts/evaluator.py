import iteratortools as it
import subprocess
import re
import Levenshtein
import programtokenizer
import ast
import tempfile
import clang.cindex
import clang.enumerations
import re


class Evaluator():
    def __init__(self):
        self.PROCESSING_CHUNK_SIZE = 50

    def get_linter_stats(self, generated_content):
        in_chunks = self.chunks(generated_content, self.PROCESSING_CHUNK_SIZE)
        progress_bar = it.ProgressBar(0, generated_content.__len__(), prefix='Progress:', suffix='Complete')
        progress_bar.print_progress_bar()

        linting_results = []
        for chunk in in_chunks:
            linting_results = linting_results + self.run_linter(chunk)
        
        return self.generate_linter_stats_from_results(linting_results)

    def get_distance_vector_stats(self, generated_content):
        total_distance = 0
        for item in generated_content:
            for i, original_line in enumerate(item['original_lines']):
                generated_line = item['generated_lines'][i]
                total_distance = total_distance + Levenshtein.distance(original_line, generated_line)
        
        # Return average levenshtein distance
        return total_distance / self.__get_total_number_of_lines(generated_content)

    def get_keyword_stats(self, generated_content):

        original_keyword_frequencies = dict.fromkeys(self.get_keyword_list(), 0)
        generated_keyword_frequencies = dict.fromkeys(self.get_keyword_list(), 0)

        for item in generated_content:
            for line in item['original_lines']:
                keywords_in_line = self.__split_line_into_words(line)
                for keyword in keywords_in_line:
                    if keyword in self.get_keyword_list():
                        original_keyword_frequencies[keyword] += 1
        for item in generated_content:
            for line in item['generated_lines']:
                keywords_in_line = self.__split_line_into_words(line)
                for keyword in keywords_in_line:
                    if keyword in self.get_keyword_list():
                        generated_keyword_frequencies[keyword] += 1

        return {"original_keyword_frequencies": original_keyword_frequencies,
                "generated_keyword_frequencies": generated_keyword_frequencies}

    def get_variable_stats(self, generated_content):

        times_new_variable_was_introduced_original = []
        times_new_variable_was_introduced_generated = []

        for item in generated_content:
            try:
                all_variables = self.get_variable_list(item['original_program'])

                last_lines_original = '\n'.join(item['original_lines'])
                big_regex = re.compile('|'.join(map(re.escape, item['original_lines'])))
                program_without_last_lines = big_regex.sub('', item['original_program'])

                variables_in_prog_without_last_lines = []
                for var in all_variables:
                    # print(var  + " => " + str(self.__split_line_into_words(program_without_last_lines)))
                    if var in self.__split_line_into_words(program_without_last_lines):
                        variables_in_prog_without_last_lines.append(var)

                variables_in_last_lines = []
                for var in all_variables:
                    if var in self.__split_line_into_words(last_lines_original) and \
                            var not in self.get_keyword_list() and \
                            var not in variables_in_last_lines:
                        variables_in_last_lines.append(var)

                original_count = 0
                for var in variables_in_last_lines:
                    if var not in variables_in_prog_without_last_lines:
                        original_count += 1

                last_lines_generated = '\n'.join(item['generated_lines'])
                generated_count = len(re.findall(r"temp[0-9]+", last_lines_generated))

                times_new_variable_was_introduced_original.append(original_count)
                times_new_variable_was_introduced_generated.append(generated_count)

            except Exception:
                pass
                # ?

        return {"times_new_variable_was_introduced_original": sum(times_new_variable_was_introduced_original) / len(times_new_variable_was_introduced_original),
                "times_new_variable_was_introduced_generated": sum(times_new_variable_was_introduced_generated) / len(times_new_variable_was_introduced_generated)}

    def get_first_keyword_stats(self, generated_content):
        correct_guesses = 0
        total_unguessable = 0
        for item in generated_content:
            corr, unguessable = self.__get_first_occurrence_correct_guesses(item, self.get_keyword_list())
            correct_guesses += corr
            total_unguessable += unguessable

        return correct_guesses / (self.__get_total_number_of_lines(generated_content) - total_unguessable)

    def get_first_variable_stats(self, generated_content):
        correct_guesses = 0
        total_unguessable = 0
        for item in generated_content:
            try:
                corr, unguessable = self.__get_first_occurrence_correct_guesses(item, self.get_variable_list(item['original_program']))
                correct_guesses += corr
                total_unguessable += unguessable
            except Exception:
                total_unguessable += 1

        return correct_guesses / (self.__get_total_number_of_lines(generated_content) - total_unguessable)

    def get_average_original_line_length(self, generated_content):
        return self.__get_average_line_length(generated_content, 'original_lines')

    def get_average_generated_line_length(self, generated_content):
        return self.__get_average_line_length(generated_content, 'generated_lines')

    def get_number_keywords(self):
        return len(self.get_keyword_list())

    def get_keyword_list(self):
        raise NotImplementedError('Implement in subclass')

    def get_variable_list(self, program):
        raise NotImplementedError('Implement in subclass')

    def run_linter(self, chunk):
        raise NotImplementedError('Implement in subclass')

    def generate_linter_stats_from_results(self, linting_results):
        raise NotImplementedError('Implement in subclass')

    def chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def __get_total_number_of_lines(self, generated_content):
        return len(generated_content) * len(generated_content[0]['original_lines'])

    def __get_average_line_length(self, generated_content, lines):
        total_line_length = 0
        for item in generated_content:
            for line in item[lines]:
                total_line_length = total_line_length + len(line)

        return total_line_length / self.__get_total_number_of_lines(generated_content)

    def __get_first_occurrence_correct_guesses(self, item, word_list):
        correct_guesses = 0
        unguessable = 0
        for i, original_line in enumerate(item['original_lines']):
            first_original_word = ''
            first_generated_word = ''
            original_arr = self.__split_line_into_words(original_line)
            for word in original_arr:
                if word in word_list:
                    first_original_word = word
                    break

            generated_arr = self.__split_line_into_words(item['generated_lines'][i])
            for word in generated_arr:
                if word in word_list:
                    first_generated_word = word
                    break

            if first_original_word != '' and first_original_word == first_generated_word:
                correct_guesses += 1

            if first_original_word == '':
                unguessable += 1

        return correct_guesses, unguessable

    def __split_line_into_words(self, line):
        return re.findall(r"[\w']+", line)


class PyEvaluator(Evaluator):
    class VariableExtractor(ast.NodeTransformer):
        def __init__(self):
            self.variables = []

        def visit_Name(self, node: ast.Name):
            self.variables.append(node.id)

        def get_variables(self):
            return self.variables


    def run_linter(self, chunk):
        # From: https://pylint.readthedocs.io/en/latest/user_guide/message-control.html
        # C convention related checks
        # R refactoring related checks
        # W various warnings
        # E errors, for probable bugs in the code
        # F fatal, if an error occurred which prevented pylint from doing further processing.
        pipeline = subprocess.Popen(['pylint', '--msg-template=\'{msg_id}\''] + chunk, stdout=subprocess.PIPE)
        console_output = pipeline.communicate()
        return re.findall(r'[CRWEF]\d{4}', str(console_output))

    
    def generate_linter_stats_from_results(self, linting_results):
        # For C and R prefixes
        style_fails = {}
        # For W and E prefixes
        warnings = {}
        # For F prefixes
        fatal_errors = {}

        for linting_result in linting_results:
            prefix = linting_result[0]
            if prefix == 'C' or prefix == 'R':
                style_fails[linting_result] = 1 if linting_result not in style_fails else style_fails[linting_result] + 1 
            elif prefix == 'W' or prefix == 'E':
                warnings[linting_result] = 1 if linting_result not in warnings else warnings[linting_result] + 1
            elif prefix == 'F':
                fatal_errors[linting_result] = 1 if linting_result not in fatal_errors else fatal_errors[linting_result] + 1
            else:
                print('invalid prefix: {}'.format(prefix))

        return {
            'style_fails': style_fails,
            'warnings': warnings,
            'fatal_errors': fatal_errors
        }


    def get_keyword_list(self):
        return list(filter(lambda x: x != 'eof' and
                      x != '\n' and
                      x != '    ' and
                      x != ':' and
                      x != '__import__', programtokenizer.words))


    def get_variable_list(self, program):
        contents = ast.parse(program)
        variableExtractor = self.VariableExtractor()
        variableExtractor.visit(contents)
        return variableExtractor.get_variables()


class CEvaluator(Evaluator):
    def run_linter(self, chunk):
        #TODO implement
        raise NotImplementedError('Implement me')


    def generate_linter_stats_from_results(self, linting_results):
        #TODO implement
        raise NotImplementedError('Implement me')


    def get_keyword_list(self):
        disallowed_keywords = ['==', '!=', '--', '++', '&&', '||', '-=', '+=', '*=', '/=', '%=', '&=', '|=', '^=', '<=',
                               '>=', '<=>' '->', '<<', '>>']
        return list(filter(lambda x: x not in disallowed_keywords, programtokenizer.c_keywords))


    def get_variable_list(self, filename):
        variables = []
        index = clang.cindex.Index.create()
        f = tempfile.TemporaryFile(mode='r+', suffix='.c')
        f.write(filename)
        f.read()
        tu = index.parse(f.name)
        f.close()
        tokens = tu.cursor.get_tokens()
        for token in tokens:
            if token.kind.name == 'IDENTIFIER' and token.spelling not in variables:
                variables.append(token.spelling)

        return variables