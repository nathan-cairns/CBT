import ast

text = '''
import numpy as np

class MyClass:
    def __init__(self, num):
        self.num = num
        
    def print_num(self):
        print(self.num)

a = MyClass(4)
for i in range(10):
    while i < 3:
        i += 1
        a.print_num()
'''


class Transformer(ast.NodeTransformer):
    def __init__(self):
        self.var_count = 0
        self.visited = {}

    def visit_Name(self, node: ast.Name):
        # TODO: actually use utf8 tokens or something instead of v1, v2
        if node.id not in self.visited:
            var_name = 'v' + str(self.var_count)
            self.visited[node.id] = var_name
            self.var_count += 1
        else:
            var_name = self.visited[node.id]
        return ast.copy_location(ast.Name(id=var_name), node)


class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.stats = {"var": []}

    def generic_visit(self, node):
        print(node.__class__.__name__)
        super().generic_visit(node)

    def visit_Name(self, node: ast.Name):
        self.stats["var"].append(node.id)
        self.generic_visit(node)

    def report(self):
        print(self.stats)


if __name__ == '__main__':
    with open("C:\\Users\\Buster\\Documents\\Code\\CBT\\data\\py150_files\\data\\2gis\\badger-api\\common\\storage.py", "r") as source:
        tree = ast.parse(source.read())

    transformer = Transformer()
    transformer.visit(tree)

    analyzer = Analyzer()
    analyzer.visit(tree)
    analyzer.report()
