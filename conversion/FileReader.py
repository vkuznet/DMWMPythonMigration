import glob


class FileReader(object):
    """
    Finds and reads lines from file
    """

    @staticmethod
    def readFile(path):
        """
        Reads lines from file

        :param path: to file
        :return: list of file lines
        """
        with open(path) as f:
            fileLines = f.readlines()
        return fileLines

    @staticmethod
    def getFileNames(path, type="tmpl"):
        """
        Recursively finds files with specific type

        :param path: to file
        :param type: of file
        :return: file name
        """
        for filename in glob.glob(path + "*." + type, recursive=True):
            yield filename
