class node(object):
    """
    Creates dependency tree.
    Value- parent
    Children- list of children
    """
    def __init__(self, value, children = []):
        self.value = value
        self.children = children

    def __str__(self, level=0):
        """
        Convert dependency tree to printable version
            
        :param level: set the level of tree
        :return: ret printable tree
        """
        ret = "  -|"*level+repr(self.value)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        """
        :return: tree node representation
        """
        return '<tree node representation>'

    def saveTree(self, path):
        """
        Save dependency tree to file

        :param path: where to save the dependency tree
        """
        with open(path, 'w') as f:
            f.write(str(self))
