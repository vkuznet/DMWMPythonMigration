import glob
import ntpath
import re


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

    @staticmethod
    def getFileName(path, type="tmpl"):
        """
        Strips down path so only file name is returned

        :param path: full path to file
        :param type: type of file,  by default- tmpl
        :return: file name
        """
        fileName = ntpath.basename(path)
        return re.sub('\.' + type + '$', '', fileName)
