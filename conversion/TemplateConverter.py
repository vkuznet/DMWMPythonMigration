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
    irreversibleDataList = []
    nrOfPythonConversions = 0

    def __init__(self, fileLines, fileName):
        self.fileLines = fileLines
        lineNumbers = self.getChangeableLineNumbers()
        self.convert(lineNumbers)
        self.filename = fileName

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
                    if (lineEnd > lineNr + 20 or len(self.fileLines) < lineEnd):
                        print("Failed to find the end of block in file: " + fileName + "of type: " + type.value[0])
            # adds info about lines to the list
            self.irreversibleDataList.append(
                IrreversibleData(fileName, lineNr, lineEnd, type, self.fileLines[lineNr:lineEnd + 1]))

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
            if any(x in self.fileLines[number] for x in ["#*", "*#"]):
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
            text = text.replace("\n", "")
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
            if (lineNrEnd > lineNr + 15 or len(self.fileLines) < lineNrEnd):
                self.irreversibleDataList.append(IrreversibleData())
                print("Failed to convert block")
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
            if (lineNrEnd > lineNr + 10 or len(self.fileLines) < lineNrEnd):
                print("Failed to convert if block")
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
            if (lineNrEnd < lineNr - 10):
                print("Failed to convert stop")
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
        self.fileLines[lineNr] = self.fileLines[lineNr].replace("#break", "{% break %}")

    def convertContinue(self, lineNr):
        """
        Converts "#continue" to jinja2  "{% continue %}"

        :param lineNr: number of line
        """
        self.fileLines[lineNr] = self.fileLines[lineNr].replace("#continue", "{% continue %}")

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
        cleanReplacment = cleanText.replace("#set", "{% set").replace("$", "") + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)

    def convertComment(self, lineNr):
        """
        Converts cheetah  comments to jinja2 comments

        :param lineNr: number of lines
        """
        # single line comments "## comment" are supported
        if "#*" in self.fileLines[lineNr]:
            self.fileLines[lineNr] = self.fileLines[lineNr].replace("#*", "{#")
        if "*#" in self.fileLines[lineNr]:
            self.fileLines[lineNr] = self.fileLines[lineNr].replace("*#", "#}")

    # Need to be called after all other placeholders were converted
    def convertPlaceHolders(self, lineNr):
        # convert placeholder with multiple parameters
        if re.search("\$\w*?[\)\]\[\w._\($]+,[ \w=,$]+\)+", self.fileLines[lineNr]):
            changeableWords = re.findall("\$\w*?\([\)\]\[\w._\($]+,[ \w=,$]+\)+", self.fileLines[lineNr])
            for word in set(changeableWords):
                replace = lambda x: "{{" + x.replace("$", "") + "}}"
                self.fileLines[lineNr] = self.fileLines[lineNr].replace(word, replace(word))
        # add }} at the end of any placeholder
        changeableWords = re.findall("\$\w*.+?\(.+\)+|\$\w*?[\)\]\[\w._\($]+", self.fileLines[lineNr])
        for word in set(changeableWords):
            self.fileLines[lineNr] = self.fileLines[lineNr].replace(word, word + "}}")
        # add {{ at the start of placeholder if it's not in the method call
        changeableWords = re.findall('.\$\w+', self.fileLines[lineNr])
        for word in changeableWords:
            replace = lambda x: x.replace("$", "{{")[1:] if x[:1] != "(" and x[:1] != ":" else x.replace("$", "")[1:]
            self.fileLines[lineNr] = self.fileLines[lineNr].replace(word[1:], replace(word))
        # in case if any is missed
        changeableWords = re.findall('\$\w+', self.fileLines[lineNr])
        for word in changeableWords:
            replace = lambda x: x.replace("$", "{{")
            self.fileLines[lineNr] = self.fileLines[lineNr].replace(word, replace(word))

    def convertEcho(self, lineNr):
        """
        Convert #echo to place holder and add info about it to irreversibleDataList
        :param lineNr: number of lines
        """
        changeableParts = re.findall("#echo.+?#|#echo.+", self.fileLines[lineNr])
        for changeablePart in changeableParts:
            self.nrOfPythonConversions += 1
            nameOfPlaceHolder = "echo" + str(self.nrOfPythonConversions)
            self.irreversibleDataList.append(IrreversibleData(self.filename, lineNr, lineNr, DataTypes.echo, [self.fileLines[lineNr]]))
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
        # adding jijnja filter to replace output with empty string
        replace = "{{" + replace + "|replace(" + replace + ",'')}}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(changeablePart, replace)

    def convertOneLineIf(self, lineNr):
        """
        Converts one line if to regulr jinja2 {%if ..%}

        :param lineNr: number of line
        """
        cleanText = self.cleanHTMLTags(lineNr)
        changeablePart = re.search("#if.+then.+else.+#|#if.+then.+else.+", cleanText).group(0)
        changeableParts = changeablePart.split(" then ")
        changeableParts[0] = changeableParts[0].replace("#if", "{% if").replace("$", "") + "%}"
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
            if (lineNrEnd > lineNr + 10):
                print("Failed to convert slurp")
                break

        while ("{% for " not in self.fileLines[lineNrStart]):
            lineNrStart -= 1
            if (lineNrEnd < lineNr - 10):
                print("Failed to convert slurp")
                break

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
        self.irreversibleDataList.append(IrreversibleData(self.filename, lineNr, lineNr, DataTypes.importFrom, self.fileLines[lineNr]))
        # clean the line
        self.fileLines[lineNr] = ""


if __name__ == "__main__":
    # for name in FileReader.getFileNames("/home/adelina/cern/DAS/src/templates/"):
    name = "/home/adelina/PycharmProjects/testCheetah/quote/qoute.tmpl"
    fileName = FileWriter.getFileName(name)
    fileLines = FileReader.readFile(name)
    lineNumbers = TemplateConverter(fileLines, fileName)
    aaa = lineNumbers.getFileLines()
    for conversions in lineNumbers.irreversibleDataList:
        conversions.codeReplacment=lineNumbers.getFileLines()[conversions.lineStart:conversions.lineEnd+1]
    print(str(lineNumbers.irreversibleDataList[0]))
    # fileName=fileName+".html"
    # FileWriter.writeToFile("/home/adelina/cern/convertedTemplates/"+fileName, aaa)
