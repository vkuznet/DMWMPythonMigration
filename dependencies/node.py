class node(object):
    def __init__(self, value, children = []):
        self.value = value
        self.children = children

    def __str__(self, level=0):
        ret = "  -|"*level+repr(self.value)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        return '<tree node representation>'


    def saveTree(self, path):
        f = open(path, 'w')
        f.write(str(self))
        f.close()