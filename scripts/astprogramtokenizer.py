import ast
import astunparse


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


if __name__ == '__main__':
    with open("C:\\Users\\Buster\\Documents\\Code\\CBT\\data\\py150_files\\data\\2gis\\badger-api\\common\\storage.py", "r") as source:
        tree = ast.parse(source.read())

    transformer = Transformer()
    transformer.visit(tree)

    a = astunparse.unparse(tree)
    print(a)
