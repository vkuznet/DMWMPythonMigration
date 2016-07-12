from FileReader import FileReader
import re


class TemplateConverter(object):
    pythonConversions={}
    nrOfPythonConversions=0

    def __init__(self, fileLines):
        self.fileLines=fileLines
        lineNumbers=self.getChangeableLineNumbers()
        self.convert(lineNumbers)

    def getChangeableLineNumbers(self):
        lineNumbers=[]
        for id,line in enumerate(self.fileLines):
            if any(x in line for x in ["#","$"]):
                lineNumbers.append(id)
        return lineNumbers

    def convert(self, lineNumbers):
        for number in lineNumbers:
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
            if any(x in self.fileLines[number] for x in ["#*","*#"]):
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
                self.convertDanimcalPlaceHolder(number)
            if "$" in self.fileLines[number]:
                self.convertPlaceHolders(number)
            if "#slurp" in self.fileLines[number]:
                self.convertSlurp(number)
            # deletes the line from file, so needs to be called last
            if any(x in self.fileLines[number] for x in ["#import", "#from"]):
                self.convertImport(number)


    def getFileLines(self):
        return self.fileLines

    def cleanHTMLTags(self, lineNr):
        cleaningRegex = re.compile('<.*?>')
        cleanText = re.sub(cleaningRegex, '', self.fileLines[lineNr])
        return cleanText

    def removeNewLine(self, text):
        if (text.endswith("\n")):
            text = text.replace("\n", "")
        return text

    def convertIfBlock(self, lineNr):
        cleanText = self.removeNewLine(self.fileLines[lineNr])
        cleanReplacment=cleanText.replace("#if", "{% if").replace("$", "") + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)
        lineNrEnd=lineNr
        while ("#end if" not in self.fileLines[lineNrEnd]):
            lineNrEnd += 1
            if (lineNrEnd > lineNr + 10 or len(self.fileLines) < lineNrEnd):
                print("Failed to convert if block")
                return
            if "#if" in  self.fileLines[lineNrEnd]:
                self.convertIfBlock(lineNrEnd)
            if "#elif" in self.fileLines[lineNrEnd]:
                self.convertElifInIfBlock(lineNrEnd)
            if "#else if" in self.fileLines[lineNrEnd]:
                self.convertElseIfInIfBlock(lineNrEnd)
            if "#else" in self.fileLines[lineNrEnd]:
                self.convertElseInIfBlock(lineNrEnd)
        cleanText = self.cleanHTMLTags(lineNrEnd)
        cleanReplacment=cleanText.replace("#end if", "{% endif %}")
        self.fileLines[lineNrEnd] = self.fileLines[lineNrEnd].replace(cleanText, cleanReplacment)


    def convertStop(self, lineNr):
        lineNrEnd=lineNr
        deletableLines=[]
        while ("#end " not in self.fileLines[lineNrEnd]):
            deletableLines.append(lineNrEnd)
            lineNrEnd += 1
            if (lineNrEnd < lineNr - 10):
                print("Failed to convert stop")
                return
        for line in deletableLines:
            self.fileLines[line] = ""

    def convertFor(self, lineNr):
        cleanText = self.removeNewLine(self.fileLines[lineNr])
        cleanReplacment=cleanText.replace("#for", "{% for").replace("$", "") + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)
        lineNrEnd=lineNr
        while ("#end for" not in self.fileLines[lineNrEnd]):
            lineNrEnd += 1
        cleanText = self.cleanHTMLTags(lineNrEnd)
        cleanReplacment=cleanText.replace("#end for", "{% endfor %}")
        self.fileLines[lineNrEnd] = self.fileLines[lineNrEnd].replace(cleanText, cleanReplacment)

    def convertElseIfInIfBlock(self, lineNr):
        cleanText = self.removeNewLine(self.fileLines[lineNr])
        cleanReplacment=cleanText.replace("#else if", "{% elif").replace("$", "") + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)

    def convertElifInIfBlock(self, lineNr):
        cleanText = self.removeNewLine(self.fileLines[lineNr])
        cleanReplacment=cleanText.replace("#elif", "{% elif").replace("$", "") + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)

    def convertElseInIfBlock(self, lineNr):
        cleanText = self.removeNewLine(self.fileLines[lineNr])
        cleanReplacment=cleanText.replace("#else", "{% else %}")
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)

    def convertBreak(self, lineNr):
        self.fileLines[lineNr]=self.fileLines[lineNr].replace("#break", "{% break %}")

    def convertContinue(self, lineNr):
        self.fileLines[lineNr]=self.fileLines[lineNr].replace("#continue", "{% break %}")

    def convertPass(self, lineNr):
        self.fileLines[lineNr]=self.fileLines[lineNr].replace("#pass", "")

    def convertSet(self, lineNr):
        cleanText = self.cleanHTMLTags(lineNr)
        cleanText=self.removeNewLine(cleanText)
        cleanReplacment=cleanText.replace("#set", "{% set").replace("$", "") + " %}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(cleanText, cleanReplacment)

    def convertComment(self, lineNr):
        # single line comments "## comment" are supported
        if "#*" in self.fileLines[lineNr]:
            self.fileLines[lineNr]=self.fileLines[lineNr].replace("#*", "{#")
        if "*#" in self.fileLines[lineNr]:
            self.fileLines[lineNr]=self.fileLines[lineNr].replace("*#", "#}")

    # Need to be called after all other placeholders were converted
    def convertPlaceHolders(self, lineNr):
        # convert placeholder with multiple parameters
        if re.search("\$\w*?[\)\]\[a-z0-9._\($]+,[ \w=,$)]+", self.fileLines[lineNr]):
            changeableWords = re.findall("\$\w*?[\)\]\[a-z0-9._\($]+,[ \w=,$)]+", self.fileLines[lineNr])
            for word in changeableWords:
                replace = lambda x: "{{"+x.replace("$", "")+"}}"
                self.fileLines[lineNr] = self.fileLines[lineNr].replace(word,replace(word))
        # add }} at the end of any placeholder
        changeableWords = re.findall("\$\w*?[\)\]\[a-z0-9._\($]+", self.fileLines[lineNr])
        for word in changeableWords:
            self.fileLines[lineNr]=self.fileLines[lineNr].replace(word, word + "}}")
        # add {{ at the start of placeholder if it's not in the method call
        changeableWords = re.findall('.\$\w+', self.fileLines[lineNr])
        for word in changeableWords:
            replace = lambda x: x.replace("$","{{")[1:] if x[:1] != "(" else x.replace("$","")[1:]
            self.fileLines[lineNr]=self.fileLines[lineNr].replace(word[1:], replace(word))
        # in case if any is missed
        changeableWords = re.findall('\$\w+', self.fileLines[lineNr])
        for word in changeableWords:
            replace = lambda x: x.replace("$", "{{")
            self.fileLines[lineNr]=self.fileLines[lineNr].replace(word, replace(word))

    # replaces echo with placeholder, expressions are moved to pythonConversions dictionary
    def convertEcho(self, lineNr):
        changeableParts = re.findall("#echo.+?#|#echo.+", self.fileLines[lineNr])
        for changeablePart in changeableParts:
            self.nrOfPythonConversions += 1
            nameOfPlaceHolder = "echo" + str(self.nrOfPythonConversions)
            pythonCode = changeablePart.replace("#echo", '').replace("#", '',1)
            self.pythonConversions.update({nameOfPlaceHolder: pythonCode})
            self.fileLines[lineNr] = self.fileLines[lineNr].replace(changeablePart,
                                                                    "{{" + nameOfPlaceHolder + "}}")

    def convertSilent(self, lineNr):
        cleanText = self.cleanHTMLTags(lineNr)
        changeablePart = re.search("#silent.+#|#silent.+", cleanText).group(0)
        replace = changeablePart.replace("$", "").replace("#silent", '').replace("#", '',1)
        # adding jijnja filter to replace output with empty string
        replace ="{{"+replace+"|replace("+replace+",'')}}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(changeablePart, replace)

    def convertOneLineIf(self,lineNr):
        cleanText = self.cleanHTMLTags(lineNr)
        changeablePart = re.search("#if.+then.+else.+#|#if.+then.+else.+", cleanText).group(0)
        changeableParts=changeablePart.split(" then ")
        changeableParts[0]=changeableParts[0].replace("#if","{% if").replace("$","")+"%}"
        changeableParts[1]=changeableParts[1].replace(" else ","{% else %}")
        if changeablePart.endswith("#"):
            changeableParts[1]=changeableParts[1][:-1]+"{% endif %}"
        else:
            changeableParts[1]=changeableParts[1]+"{% endif %}"
        replacement=changeableParts[0]+ changeableParts[1]
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(changeablePart,  replacement)

    # has to be called after all for statments are converted
    # TODO: add support for other statments
    def convertSlurp(self, lineNr):
        self.fileLines[lineNr] = self.fileLines[lineNr].replace("#slurp",  "")
        lineNrEnd=lineNr
        lineNrStart=lineNr
        while("{% endfor" not in  self.fileLines[lineNrEnd]):
            lineNrEnd+=1
            if(lineNrEnd>lineNr+10):
                print("Failed to convert slurp")
                break

        while ("{% for " not in self.fileLines[lineNrStart]):
            lineNrStart -= 1
            if(lineNrEnd<lineNr-10):
                print("Failed to convert slurp")
                break

        self.fileLines[lineNrEnd] = self.fileLines[lineNrEnd].replace("{% endfor",  "{%- endfor")
        self.fileLines[lineNrStart] = self.fileLines[lineNrStart].replace("%}",  "-%}")

    # has to be callled before converPlaceHolder
    def convertDanimcalPlaceHolder(self, lineNr):
        changeablePart = re.search("\${.*}",  self.fileLines[lineNr]).group(0)
        replace = lambda x: x.replace("${", "{{") + "}"
        self.fileLines[lineNr] = self.fileLines[lineNr].replace(changeablePart, replace(changeablePart))

    # python code importation is not supported
    # moving it from scrip and deleting it from template
    def convertImport(self, lineNr):
        importKey="importedFrom"
        fromImports = re.search("#from (.+) import(.+)",  self.fileLines[lineNr])
        if(fromImports):
            self.pythonConversions.update({fromImports.group(2):{importKey:fromImports.group(1)}})
        imports=re.search("#import (.+)",  self.fileLines[lineNr])
        if (imports):
            self.pythonConversions.update({imports.group(1):{importKey:None}})
        # clean the line
        self.fileLines[lineNr]=""



if __name__=="__main__":
    fileLines=FileReader().readFile("/home/adelina/PycharmProjects/testCheetah/quote/qoute.tmpl")
    lineNumbers=TemplateConverter(fileLines)
    aaa=lineNumbers.getFileLines()

    for line in aaa:
        print(line,end="")
    # print(str(lineNumbers.pythonConversions))


