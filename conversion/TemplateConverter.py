import argparse
import os
import re

from FileReader import FileReader
from FileWriter import FileWriter
from IrreversibleData import IrreversibleData
from IrreversibleDataType import IrreversibleType, DataTypes


class TemplateConverter(object):
    """
    Converts cheetah templates to jinja2
    Code that has to be converted manualy is saved in separate file
    """
    nrOfPythonConversions = 0

    def __init__(self, fileLines, fileName):
        self.irreversibleDataList = []
        self.fileLines = fileLines
        self.filename = fileName
        lineNumbers = self.getChangeableLineNumbers()
        self.convert(lineNumbers)
        # add replaced code to irreversibleData object
        for irreversibleData in self.irreversibleDataList:
            irreversibleData.codeReplacment = self.fileLines[irreversibleData.lineStart:irreversibleData.lineEnd + 1]

    def getChangeableLineNumbers(self):
        """
        Gets line numbers that can be converted
        Add unconvertible lines to a IrreversibleType class

        :return: list with numbers of convertable lines
        """
        lineNumbers = []
        for id, line in enumerate(self.fileLines):
            if any(x.value[0] in line for x in list(IrreversibleType)):
                self.addUnconvertibleLines(id)
            elif any(x in line for x in ["#", "$"]):
                lineNumbers.append(id)
        return lineNumbers

    def addUnconvertibleLines(self, lineNr):
        """
        Add info about lines that can't be converted to the IrreversibleData list

        :param lineNr: number of line
        """
        # finds what types of expressions are in the line
        types = [enumType for enumType in list(IrreversibleType) if enumType.value[0] in self.fileLines[lineNr]]
        lineEnd = lineNr
        for type in types:
            # type has 2 values if it has #end
            if len(type.value) > 1:
                # finds the #end
                while (type.value[1] not in self.fileLines[lineEnd]):
                    lineEnd += 1
                    if (lineEnd > lineNr + 20 or len(self.fileLines) <= lineEnd):
                        print("Failed to find the end of block in file: " + self.filename + "of type: " + type.value[0])
            # adds info about lines to the list
            self.irreversibleDataList.append(
                IrreversibleData(self.filename, lineNr, lineEnd, type, self.fileLines[lineNr:lineEnd + 1]))

    def convert(self, lineNumbers):
        """
        Converts cheetah expressions to jinja2

        :param lineNumbers: list of numbers that represent convertable lines
        """
        for number in lineNumbers:
            if "#block" in self.fileLines[number]:
                self.convertBlock(number)
            if "#set" in self.fileLines[number]:
                self.convertSet(number)
            if "#stop" in self.fileLines[number]:
                self.convertStop(number)
            # Could be moved to loop methods
            if "#break" in self.fileLines[number]:
                self.convertBreak(number)
            # Could be moved to loop methods
            if "#continue" in self.fileLines[number]:
                self.convertContinue(number)
            if "#pass" in self.fileLines[number]:
                self.convertPass(number)
            if any(x in self.fileLines[number] for x in ["#*", "*#","##"]):
                self.convertComment(number)
            if "#silent" in self.fileLines[number]:
                self.convertSilent(number)
            if "#echo" in self.fileLines[number]:
                self.convertEcho(number)
            if re.compile(".+#if.+then.+else.+").match(self.fileLines[number]):
                self.convertOneLineIf(number)
            if "#if" in self.fileLines[number]:
                self.convertIfBlock(number)
            if "#for" in self.fileLines[number]:
                self.convertFor(number)
            if "${" in self.fileLines[number]:
                self.convertDynamicalPlaceHolder(number)
            if "$" in self.fileLines[number]:
                self.convertPlaceHolders(number)
            if "#slurp" in self.fileLines[number]:
                self.convertSlurp(number)
            if any(x in self.fileLines[number] for x in ["#import", "#from"]):
                self.convertImport(number)

    def getFileLines(self):
        """
        Get list of file lines

        :return: list of file lines
        """
        return self.fileLines

    def cleanHTMLTags(self, lineNr):
        """
        Strips line out of html tags

        :param lineNr: number of line
        :return: text without html tags
        """
        cleaningRegex = re.compile('<.*?>')
        cleanText = re.sub(cleaningRegex, '', self.fileLines[lineNr])
        return cleanText

    def removeNewLine(self, text):
        """
        Removes new line from given string

        :param text: string
        :return: string without any new lines
        """
        if (text.endswith("\n")):
            text = text[:-1]
        return text

    def convertBlock(self, lineNr):
        """
        Converts #block to jinja2 {% block %}

        :param lineNr: number of line
        """
        changeableWords = re.search("#block (\w+)", self.fileLines[lineNr])
        replacment = "{% block " + changeableWords.group(1) + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(changeableWords.group(0), replacment)
        lineNrEnd = lineNr
        while ("#end block" not in self.fileLines[lineNrEnd]):
            lineNrEnd += 1
            if (len(self.fileLines) <= lineNrEnd):
                irreversibleData = IrreversibleData(self.filename, lineNr, lineNrEnd, DataTypes.block,
                                                    self.fileLines[lineNr:lineNrEnd + 1])
                self.irreversibleDataList.append(irreversibleData)
                print("Failed to convert block in " + self.filename)
                return
        changeableWords = re.search("#end block( \w+)?", self.fileLines[lineNrEnd])
        replacment = "{% endblock %}"
        self.fileLines[lineNrEnd] = self.fileLines[lineNrEnd].replace(changeableWords.group(0), replacment)

    def convertIfBlock(self, lineNr):
        """
        Converts #if expression with conditions to jinja2 {% if exp%}
        :param lineNr: number of line
        """
        cleanText = self.removeNewLine(self.fileLines[lineNr])
        cleanReplacment = cleanText.replace("#if", "{% if").replace("$", "") + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)
        lineNrEnd = lineNr
        while ("#end if" not in self.fileLines[lineNrEnd]):
            lineNrEnd += 1
            if (len(self.fileLines) <= lineNrEnd):
                irreversibleData = IrreversibleData(self.filename, lineNr, lineNrEnd, DataTypes.ifBlock,
                                                    self.fileLines[lineNr:lineNrEnd + 1])
                self.irreversibleDataList.append(irreversibleData)
                print("Failed to convert if block in " + self.filename)
                return
            if "#if" in self.fileLines[lineNrEnd]:
                self.convertIfBlock(lineNrEnd)
            if "#elif" in self.fileLines[lineNrEnd]:
                self.convertElifInIfBlock(lineNrEnd)
            if "#else if" in self.fileLines[lineNrEnd]:
                self.convertElseIfInIfBlock(lineNrEnd)
            if "#else" in self.fileLines[lineNrEnd]:
                self.convertElseInIfBlock(lineNrEnd)
        cleanText = self.cleanHTMLTags(lineNrEnd)
        cleanReplacment = cleanText.replace("#end if", "{% endif %}")
        self.fileLines[lineNrEnd] = self.fileLines[lineNrEnd].replace(cleanText, cleanReplacment)

    def convertStop(self, lineNr):
        """
        Removes all lines from "#stop" till first "#end"

        :param lineNr: number of line
        """
        lineNrEnd = lineNr
        deletableLines = []
        while ("#end " not in self.fileLines[lineNrEnd]):
            deletableLines.append(lineNrEnd)
            lineNrEnd += 1
            if (lineNrEnd >= len(self.fileLines)):
                irreversibleData = IrreversibleData(self.filename, lineNr, lineNrEnd, DataTypes.stop,
                                                    self.fileLines[lineNr:lineNrEnd + 1])
                self.irreversibleDataList.append(irreversibleData)
                print("Failed to convert stop in " + self.filename)
                return
        for line in deletableLines:
            self.fileLines[line] = ""

    def convertFor(self, lineNr):
        """
        Converts "#for" to jinja2 "{% for ...%}"

        :param lineNr: number of lines
        """
        cleanText = self.removeNewLine(self.fileLines[lineNr])
        cleanReplacment = cleanText.replace("#for", "{% for").replace("$", "") + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)
        lineNrEnd = lineNr
        while ("#end for" not in self.fileLines[lineNrEnd]):
            lineNrEnd += 1
            if (lineNrEnd >= len(self.fileLines)):
                irreversibleData = IrreversibleData(self.filename, lineNr, lineNrEnd, DataTypes.forLoop,
                                                    self.fileLines[lineNr:lineNrEnd + 1])
                self.irreversibleDataList.append(irreversibleData)
                print("Failed to convert #for in " + self.filename)
                return
        cleanText = self.cleanHTMLTags(lineNrEnd)
        cleanReplacment = cleanText.replace("#end for", "{% endfor %}")
        self.fileLines[lineNrEnd] = self.fileLines[lineNrEnd].replace(cleanText, cleanReplacment)

    def convertElseIfInIfBlock(self, lineNr):
        """
        Converts "#else if" to jinja2  "{% elif... %}"

        :param lineNr: number of line
        """
        cleanText = self.removeNewLine(self.fileLines[lineNr])
        cleanReplacment = cleanText.replace("#else if", "{% elif").replace("$", "") + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)

    def convertElifInIfBlock(self, lineNr):
        """
        Converts "#elif" to jinja2  "{% elif... %}"

        :param lineNr: number of line
        """
        cleanText = self.removeNewLine(self.fileLines[lineNr])
        cleanReplacment = cleanText.replace("#elif", "{% elif").replace("$", "") + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)

    def convertElseInIfBlock(self, lineNr):
        """
        Converts "#else " to jinja2  "{% else... %}"

        :param lineNr: line number
        """
        cleanText = self.removeNewLine(self.fileLines[lineNr])
        cleanReplacment = cleanText.replace("#else", "{% else %}")
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)

    def convertBreak(self, lineNr):
        """
        Converts "#break" to jinja2  "{% break %}"

        :param lineNr: number of line
        """
        self.fileLines[lineNr] = self.fileLines[lineNr].replace("#break", "{%- break %}")

    def convertContinue(self, lineNr):
        """
        Converts "#continue" to jinja2  "{% continue %}"

        :param lineNr: number of line
        """
        self.fileLines[lineNr] = self.fileLines[lineNr].replace("#continue", "{%- continue %}")

    def convertPass(self, lineNr):
        """
        Removes "#pass" as it is redundant

        :param lineNr: number of line
        """
        self.fileLines[lineNr] = self.fileLines[lineNr].replace("#pass", "")

    def convertSet(self, lineNr):
        """
        Converts "#set ..." to jinja2  "{% set ... %}"

        :param lineNr: number of line
        """
        cleanText = self.cleanHTMLTags(lineNr)
        cleanText = self.removeNewLine(cleanText)
        cleanReplacment = cleanText.replace("#set", "{%- set").replace("$", "") + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)

    def convertComment(self, lineNr):
        """
        Converts cheetah  comments to jinja2 comments

        :param lineNr: number of lines
        """
        if "##" in self.fileLines[lineNr]:
            self.fileLines[lineNr] = self.removeNewLine(self.fileLines[lineNr].replace("##", "{#-"))+"#}\n"
        if "#*" in self.fileLines[lineNr]:
            self.fileLines[lineNr] = self.fileLines[lineNr].replace("#*", "{#-")
        if "*#" in self.fileLines[lineNr]:
            self.fileLines[lineNr] = self.fileLines[lineNr].replace("*#", "#}")

    def convertPlaceHolders(self, lineNr):
        """
        Converts cheetah placeholders to jinja2

        :param lineNr: number of line
        """
        placeholders = re.findall("\$\w+.", self.fileLines[lineNr])
        fullPlaceholders = self.getFullPlacehoder(lineNr, placeholders)
        replace = lambda x: "{{" + x.replace("$", "")[:-1] + "}}" + \
                            x[-1:] if not re.search('\w$', x) else "{{" + x.replace( "$", "") + "}}"
        for placeholder in fullPlaceholders:
            self.fileLines[lineNr] = self.fileLines[lineNr].replace(placeholder, replace(placeholder))

    def getFullPlacehoder(self, lineNr, words):
        """
        Recursively checks where placeholder ends and returns it

        :param lineNr: number of line
        :param words: list of partial placeholders
        :return: returns list of full placeholder
        """
        for word in words:
            if word[-1:] == "(":
                words = re.findall(re.escape(word) + ".+?\)+.", self.fileLines[lineNr])
                return self.getFullPlacehoder(lineNr, words)
            if word[-1:] == "[":
                words = re.findall(re.escape(word) + ".+?\]+.", self.fileLines[lineNr])
                return self.getFullPlacehoder(lineNr, words)
            if word[-1:] == ".":
                words = re.findall(re.escape(word) + "\w+.", self.fileLines[lineNr])
                return self.getFullPlacehoder(lineNr, words)
        return words

    def convertEcho(self, lineNr):
        """
        Convert #echo to place holder and add info about it to irreversibleDataList
        :param lineNr: number of lines
        """
        changeableParts = re.findall("#echo.+?#|#echo.+", self.fileLines[lineNr])
        for changeablePart in changeableParts:
            self.nrOfPythonConversions += 1
            nameOfPlaceHolder = "echo" + str(self.nrOfPythonConversions)
            irreversibleData = IrreversibleData(self.filename, lineNr, lineNr, DataTypes.echo, self.fileLines[lineNr])
            self.irreversibleDataList.append(irreversibleData)
            self.fileLines[lineNr] = self.fileLines[lineNr].replace(changeablePart,
                                                                    "{{" + nameOfPlaceHolder + "}}")

    def convertSilent(self, lineNr):
        """
        Converts #silent to placeholder that will not present any output
        :param lineNr: number of line
        """
        cleanText = self.cleanHTMLTags(lineNr)
        changeablePart = re.search("#silent.+#|#silent.+", cleanText).group(0)
        replace = changeablePart.replace("$", "").replace("#silent", '').replace("#", '', 1)
        # output should always be empty
        replace = "{{- \"\" if " + replace + "}}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(changeablePart, replace)

    def convertOneLineIf(self, lineNr):
        """
        Converts one line if to regulr jinja2 {%if ..%}

        :param lineNr: number of line
        """
        cleanText = self.cleanHTMLTags(lineNr)
        changeablePart = re.search("#if.+then.+else.+#|#if.+then.+else.+", cleanText).group(0)
        changeableParts = changeablePart.split(" then ")
        changeableParts[0] = changeableParts[0].replace("#if", "{%- if").replace("$", "") + "%}"
        changeableParts[1] = changeableParts[1].replace(" else ", "{% else %}")
        if changeablePart.endswith("#"):
            changeableParts[1] = changeableParts[1][:-1] + "{% endif %}"
        else:
            changeableParts[1] = changeableParts[1] + "{% endif %}"
        replacement = changeableParts[0] + changeableParts[1]
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(changeablePart, replacement)

    # TODO: add support for other statments. ONly for is supported
    def convertSlurp(self, lineNr):
        """
        Slurp is used for whitespace control
        Removes slurp and adds '-' (- is a using in jinja2 to remove whitespaces)

        :param lineNr: number of line
        """
        self.fileLines[lineNr] = self.fileLines[lineNr].replace("#slurp", "")
        lineNrEnd = lineNr
        lineNrStart = lineNr
        while ("{% endfor" not in self.fileLines[lineNrEnd]):
            lineNrEnd += 1
            if (lineNrEnd >= len(self.fileLines)):
                irreversibleData = IrreversibleData(self.filename, lineNr, lineNrEnd, DataTypes.slurp,
                                                    self.fileLines[lineNr:lineNrEnd + 1])
                self.irreversibleDataList.append(irreversibleData)
                print("Failed to convert slurp")
                return

        while ("{% for " not in self.fileLines[lineNrStart]):
            lineNrStart -= 1
            if (lineNrEnd < 0):
                irreversibleData = IrreversibleData(self.filename, lineNrEnd, lineNr, DataTypes.slurp,
                                                    self.fileLines[lineNr:lineNrEnd + 1])
                self.irreversibleDataList.append(irreversibleData)
                print("Failed to convert slurp in " + self.filename)
                return

        self.fileLines[lineNrEnd] = self.fileLines[lineNrEnd].replace("{% endfor", "{%- endfor")
        self.fileLines[lineNrStart] = self.fileLines[lineNrStart].replace("%}", "-%}")

    def convertDynamicalPlaceHolder(self, lineNr):
        """
        Removes dynamical placeholder with normal placeholders "{{..}}"
        Has to be called before convertPlaceHolder
        :param lineNr:
        """
        changeablePart = re.search("\${.*}", self.fileLines[lineNr]).group(0)
        replace = lambda x: x.replace("${", "{{") + "}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(changeablePart, replace(changeablePart))

    def convertImport(self, lineNr):
        """
        Python code importation is not supported in jinja2
        Removes import from template, adds information about it to irreversibleDataList
        :param lineNr: number of line
        """
        self.irreversibleDataList.append(
            IrreversibleData(self.filename, lineNr, lineNr, DataTypes.importFrom, [self.fileLines[lineNr]]))
        # clean the line
        self.fileLines[lineNr] = ""


def main(opts):
    "Main function"
    if not [os.path.isdir(x) for x in vars(opts)]:
        raise IOError("No such directory")
    # add slash at the end of directory
    slashIt = lambda x: x if x.endswith("/") else x + "/"
    path = slashIt(opts.path)
    pathConverted = slashIt(opts.pathConverted)
    pathManual = slashIt(opts.pathManual)

    manualReplacments = []
    fileNames = []
    for name in FileReader.getFileNames(path):
        # extracts file name from path
        fileName = FileReader.getFileName(name)
        # get file lines
        fileLines = FileReader.readFile(name)
        templateConverter = TemplateConverter(fileLines, name)
        # get converted lines
        convertedLines = templateConverter.getFileLines()
        # add lines that are inconvertible to the list
        manualReplacments += templateConverter.irreversibleDataList
        fileNames += [x.fileName for x in templateConverter.irreversibleDataList]
        fileName = fileName + ".tmpl"
        # save jinja2 template
        FileWriter.writeToFile(pathConverted + fileName, convertedLines)
    # save info about inconvertible template
    print(str(len(list(set(
        fileNames)))) + " file(s) need manual conversion. More information can be found in:\n" +
          pathManual + "manualConversions.txt")
    FileWriter.writeToFile(pathManual + "manualConversions.txt", FileWriter.convertToString(manualReplacments))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts cheetah .tmpl to jinja2')
    parser.add_argument("-p", dest="path", required=True, action='store',
                        help="Directory of .tmpl files that needs to be converted")
    parser.add_argument("-pc", dest="pathConverted", required=True, action='store',
                        help="Path where converted templates should be saved")
    parser.add_argument("-pm", dest="pathManual", action='store', required=True,
                        help="Path where information about failed conversions should be saved")
    opts = parser.parse_args()
    main(opts)
