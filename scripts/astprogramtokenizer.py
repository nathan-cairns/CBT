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

class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.stats = {"import": [], "from": [], "func": [], "var": []}

    def visit_Import(self, node):
        for alias in node.names:
            self.stats["import"].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.stats["from"].append(alias.name)
        self.generic_visit(node)

    def generic_visit(self, node):
        print(node.__class__.__name__)
        super().generic_visit(node)

    def visit_Name(self, node):
        self.stats["var"].append(node.id)
        self.generic_visit(node)

    def report(self):
        print(self.stats)


if __name__ == '__main__':
    with open("C:\\Users\\Buster\\Documents\\Code\\CBT\\data\\py150_files\\data\\2gis\\badger-api\\common\\storage.py", "r") as source:
        tree = ast.parse(source.read())

    analyzer = Analyzer()
    analyzer.visit(tree)
    analyzer.report()
