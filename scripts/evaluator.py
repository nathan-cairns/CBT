import iteratortools as it
import subprocess
import re
import Levenshtein
import programtokenizer
import ast
import tempfile
import clang.cindex
import clang.enumerations


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
            for i, original_line in  enumerate(item['original_lines']):
                generated_line = item['generated_lines'][i]
                total_distance = total_distance + Levenshtein.distance(original_line, generated_line)
        
        # Return average levenshtein distance
        return total_distance / self.__get_total_number_of_lines(generated_content)


    def get_keyword_stats(self, generated_content):
        total_correct_frac = 0
        for item in generated_content:
            total_correct_frac = total_correct_frac + self.__get_count_statistics(item, self.get_keyword_list())

        # Return the mean of correct keyword guesses
        return total_correct_frac / self.__get_total_number_of_lines(generated_content)


    def get_variable_stats(self, generated_content):
        total_correct_frac = 0
        for item in generated_content:
            total_correct_frac =  total_correct_frac + self.__get_count_statistics(item, self.get_variable_list(item['original_program']))

        # Return the mean of correct variable guesses
        return total_correct_frac / self.__get_total_number_of_lines(generated_content)


    def get_first_keyword_stats(self, generated_content):
        correct_guesses = 0
        for item in generated_content:
            correct_guesses = correct_guesses + self.__get_first_occurrence_correct_guesses(item, self.get_keyword_list())

        return correct_guesses / self.__get_total_number_of_lines(generated_content)


    def get_first_variable_stats(self, generated_content):
        correct_guesses = 0
        for item in generated_content:
            correct_guesses = correct_guesses + self.__get_first_occurrence_correct_guesses(item, self.get_variable_list(item['original_program']))
        
        return correct_guesses / self.__get_total_number_of_lines(generated_content)

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
        for i, original_line in enumerate(item['original_lines']):
            first_original_word = ''
            first_generated_word = ''
            original_arr = original_line.split(' ')
            for word in original_arr:
                if word in word_list:
                    first_original_word = word
                    break

            generated_arr = item['generated_lines'][i].split(' ')
            for word in generated_arr:
                if word in word_list:
                    first_generated_word = word

            if first_original_word == first_generated_word:
                correct_guesses = correct_guesses + 1

        return correct_guesses


    def __get_count_statistics(self, item, word_list):
        total_correct_frac = 0

        for i, original_line in enumerate(item['original_lines']):
            original_keywords = dict.fromkeys(word_list, 0)
            generated_keywords = dict.fromkeys(word_list, 0)
            original_arr = original_line.split(' ')

            for word in original_arr:
                if word in word_list:
                    original_keywords[word] = original_keywords[word] + 1

            generated_arr = item['generated_lines'][i].split(' ')
            for word in generated_arr:
                if word in word_list:
                    generated_keywords[word] = generated_keywords[word] + 1

            total_kwords_in_original = sum(original_keywords.values())
            correct_guesses = 0

            if total_kwords_in_original == 0:
                total_correct_frac = total_correct_frac + 1
                break

            for kword in original_keywords:
                if generated_keywords[kword] >= original_keywords[kword]:
                    correct_guesses = correct_guesses + original_keywords[kword]
                else:
                    correct_guesses = correct_guesses + generated_keywords[kword]

            correct_frac = correct_guesses / total_kwords_in_original
            total_correct_frac = total_correct_frac + correct_frac

        return total_correct_frac


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
        return programtokenizer.words


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
        return programtokenizer.c_keywords


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