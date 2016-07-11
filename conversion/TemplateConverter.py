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
            if any(x in self.fileLines[number] for x in ["#import","#from"]):
                self.convertImport(number)
            if any(x in self.fileLines[number] for x in ["#*","*#"]):
                self.convertComment(number)
            if "#silent" in self.fileLines[number]:
                self.convertSilent(number)
            if "#echo" in self.fileLines[number]:
                self.convertEcho(number)
            if re.compile(".+#if.+then.+else.+").match(self.fileLines[number]):
                self.convertOneLineIf(number)
            if "${" in self.fileLines[number]:
                self.convertDanimcalPlaceHolder(number)
            if "$" in self.fileLines[number]:
                self.convertPlaceHolders(number)
            if "#slurp" in self.fileLines[number]:
                self.convertSlurp(number)



    def getFileLines(self):
        return self.fileLines

    def cleanHTMLTags(self, lineNr):
        cleaningRegex = re.compile('<.*?>')
        cleanText = re.sub(cleaningRegex, '', self.fileLines[lineNr])
        return cleanText


    def convertComment(self, lineNr):
        # single line comments "## comment" are supported
        if "#*" in self.fileLines[lineNr]:
            self.fileLines[lineNr]=self.fileLines[lineNr].replace("#*", "{#")
        if "*#" in self.fileLines[lineNr]:
            self.fileLines[lineNr]=self.fileLines[lineNr].replace("*#", "#}")

    # Need to be called after all other placeholders were converted
    def convertPlaceHolders(self, lineNr):
        cleanText=self.cleanHTMLTags(lineNr).split()
        changeableWords=[word for word in cleanText if word.startswith('$')]
        for word in changeableWords:
            replace = lambda x: x.replace("$","{{") + "}}"
            self.fileLines[lineNr]=self.fileLines[lineNr].replace(word, replace(word))

    # replaces echo with placeholder, expressions are moved to pythonConversions dictionary
    def convertEcho(self, lineNr):
        cleanText = self.cleanHTMLTags(lineNr)
        changeablePart = re.search("#echo.+#|#echo.+", cleanText).group(0)
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
        self.nrOfPythonConversions+=1
        importKey="importedFrom"+self.nrOfPythonConversions
        fromImports = re.search("#from (.+) import(.+)",  self.fileLines[lineNr])
        if(fromImports):
            self.pythonConversions.update({fromImports.group(2):{importKey:fromImports.group(1)}})
        imports=re.search("#import (.+)",  self.fileLines[lineNr])
        if (imports):
            self.pythonConversions.update({imports.group(1):{importKey:None}})
        del self.fileLines[lineNr]



if __name__=="__main__":
    fileLines=FileReader().readFile("/home/adelina/PycharmProjects/testCheetah/quote/qoute.tmpl")
    lineNumbers=TemplateConverter(fileLines).getFileLines()

    for line in lineNumbers:
        print(line)



