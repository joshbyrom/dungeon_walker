#node class that the graph class may hold to store information
class Node:
    def __init__(self, **kwargs):
        self.column = kwargs.get('column') or 0
        self.row = kwargs.get('row') or 0
        self.contents = kwargs.get('contents') or 'nothing'

# graph class used to hold level information
class Graph:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name') or 'Generic Graph'
        self.width = kwargs.get('width') or 100
        self.height = kwargs.get('height') or 100
        self.content_type = kwargs.get('content_type') or Node

        self.data = None
        self.initializer = kwargs.get('initializer') or (lambda x: x)
        self.initialize_self()

    def initialize_self(self):
        f = lambda x, y: self.initializer(self.content_type(column=x, row=y))
        self.data = [[f(x,y) for y in xrange(0, self.height)] for x in xrange(0, self.width)]

    def get_contents(self, column, row):
        try:
            return self.data[column][row].contents
        except:
            return None

    def set_contents(self, column, row, contents):
        try:
            node = self.data[column][row]
            node.contents = contents
            return node
        except:
            return None
    
#sample use
if __name__ == '__main__':
    def initializer(node):
        node.contents = 'node at ' + str(node.column) + ', ' + str(node.row)
        return node
    
    graph = Graph(initializer=initializer)
    graph.get_contents(101, 101)
    graph.set_contents(101, 101, Node())

    print graph.get_contents(50, 50)
    print 'success'
