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
