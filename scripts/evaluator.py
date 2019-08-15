import iteratortools as it
import subprocess
import re
import keyword


class Evaluator():
    def __init__(self):
        self.PROCESSING_CHUNK_SIZE = 50

    def chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def get_linter_stats(self, generated_content):
        in_chunks = self.chunks(generated_content, self.PROCESSING_CHUNK_SIZE)
        progress_bar = it.ProgressBar(0, generated_content.__len__(), prefix='Progress:', suffix='Complete')
        progress_bar.print_progress_bar()

        linting_results = []
        for chunk in in_chunks:
            linting_results = linting_results + self.run_linter(chunk)
        
        return self.generate_linter_stats_from_results(linting_results)


    def run_linter(self, chunk):
        raise NotImplementedError('Implement me in subclass')


    def generate_linter_stats_from_results(self, linting_results):
        raise NotImplementedError('Implement me in subclass')
    
    
    def get_distance_vector_stats(self, generated_content):
        pass

    
    # TODO this can probably be reused for the get_variable_stats function
    def get_keyword_stats(self, generated_content):
        keywords = self.get_keyword_list()
        total_correct_frac = 0

        for item in generated_content:
            for i, orginal_line in enumerate(item['orginal_lines']):
                orginal_keywords = dict.fromkeys(keywords, 0)
                generated_keywords = dict.fromkeys(keywords, 0)

                orginal_arr = orginal_line.split(' ')
                for word in orginal_arr:
                    if word in keywords:
                        orginal_keywords[word] = orginal_keywords[word] + 1

                generated_arr = item['generated_lines'][i].split(' ')
                for word in generated_arr:
                    if word in keywords:
                        generated_keywords[word] = generated_keywords[word] + 1

                total_kwords_in_orginal = sum(orginal_keywords.values())
                correct_guesses = 0

                if total_kwords_in_orginal == 0:
                    total_correct_frac = total_correct_frac + 1
                    break

                for kword in orginal_keywords:
                    if generated_keywords[kword] >= orginal_keywords[kword]:
                        correct_guesses = correct_guesses + orginal_keywords[kword]
                    else:
                        correct_guesses = correct_guesses + generated_keywords[kword]

                correct_frac = correct_guesses / total_kwords_in_orginal
                total_correct_frac = total_correct_frac + correct_frac

        # Return the mean of correct keyword guesses
        return total_correct_frac / (len(generated_content) * len(generated_content[0]['orginal_lines']))


    def get_keyword_list(self):
        raise NotImplementedError('Implement me in subclass')


    def get_variable_stats(self, generated_content):
        pass

    
    def get_keyword_random_stats(self, generated_content):
        pass


    def get_variable_random_stats(self, generated_content):
        pass


class PyEvaluator(Evaluator):
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
        return keyword.kwlist


class CEvaluator(Evaluator):
    
    def run_linter(self, chunk):
        #TODO implement
        raise NotImplementedError('Implement me')


    def generate_linter_stats_from_results(self, linting_results):
        #TODO implement
        raise NotImplementedError('Implement me')


    def get_keyword_list(self):
        #TODO implement
        raise NotImplementedError('Implement me')

