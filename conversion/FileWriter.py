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
    def convertToString(listOfIrreversibles):
        """
        Formats information about failed conversions to string

        :return: formated string
        """
        formatedString=[]
        # get same file names
        fileNames=set(ir.fileName for ir in listOfIrreversibles)
        for name in fileNames:
            # get list of irreversible data from same file
            sameFile=list(filter(lambda x: x.fileName == name, listOfIrreversibles))
            formatedString += "_" * 100+"\n"
            formatedString+="Could not fully convert file: "+name+"\n"
            formatedString += "_" * 90+"\n"
            for values in sameFile:
                replace=lambda x: x if x!="" else "This line was removed\n"
                formatedString += "In lines: {0} - {1}: {2} experssion could not be converted \n\n" \
                       "Old code:\n{3}Results:\n{4}\n".format(values.lineStart + 1, values.lineEnd + 1, values.type.value[0],
                                                        "".join(values.oldValue), replace("".join(values.codeReplacment))+"-"*50)
        return formatedString

