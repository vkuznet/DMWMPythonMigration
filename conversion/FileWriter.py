import ntpath
import re


class FileWriter(object):
    """
    Writes lines to file
    """

    @staticmethod
    def writeToFile(path, lines):
        """
        Write lines to file

        :param path: to file
        :param lines: of converted file
        """
        with open(path, mode='w+', encoding='utf-8') as myfile:
            myfile.write(''.join(lines))

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
