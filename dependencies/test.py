import os
import pickle

import requests
from os.path import join, getsize
import lxml.html

from node import node


class ReadFiles:
    path=""

    def __init__(self, path):
        self.path = path

    def getAllFiles(self):
        list = []
        for root, dirs, files in os.walk(self.path):
            for name in files:
                if name.endswith(".spec"):
                    list.append(name)
        return list

    def readReqFromFile(self, name):
        req=[]
        file = open(self.path+name)
        for line in file:
            li = line.lstrip()
            if li.startswith("Requires:") or li.startswith("BuildRequires:"):
                splited=line.split()
                del splited[:1]
                req+=splited
        file.close()
        return req



    def addChildren(self, _node, dependencies, libs):
        values={}
        for _value in dependencies:
            value=_value
            if (value.startswith('py2')):
                value = value[4:]
            if value.lower() in map(str.lower, libs):
                values[_value] = "ok"
            else:
                values[_value] = "nope"

        _node.children = [node(dep+"- "+values[dep]) for dep in dependencies]
        i=0;
        for dep in dependencies:
            if dep+".spec" in reqMap.keys():
                self.addChildren(_node.children[i], reqMap[dep + ".spec"], libs)
            i+=1



    def retrieveLibs(self):
        libs=[]
        response = requests.get('https://pypi.python.org/pypi?:action=browse&c=533&show=all')
        dom = lxml.html.fromstring(response.content)
        for link in dom.xpath('//table[@class="list"]//a/text()'):  # select the url in href for all a tags(links)
            libs.append(link)
        file = open(self.path + "python3AvailableLibs.txt", 'w+')
        file.write(' '.join(libs))
        file.close()

    def getLibsFromFile(self):
        file = open(self.path+"python3AvailableLibs.txt")
        for line in file:
            splited=line.split()
        file.close()
        return splited


    def saveToFile(self, fileName, text):
        f = open(self.path + fileName, 'w+')
        for i in text.keys():
            f.write(i + ": " + ''.join([str(x) for x in text[i]]) + "\n")
        f.close()


    def compareDepenedencies(self, libs):
        finalDerp={}
        for _key in reqMap.keys():
            key=_key
            if(_key.startswith('py2')):
                key=key[4:-5]
            else:
                key=key[:-5]

            if key.lower()  in map(str.lower, libs):
                finalDerp[_key] = "ok"
            else:
                finalDerp[_key] = "nope"
            for _value in reqMap[_key]:
                value=_value
                if (_value.startswith('py2')):
                    value=value[4:]
                if value.lower()  in map(str.lower, libs) :
                    finalDerp[_value] = "ok"
                else:
                    finalDerp[_value] = "nope"

        return finalDerp


    def addDepToSpec(self, libs):
        finalDerp={}
        for _key in reqMap.keys():
            key = _key
            if (_key.startswith('py2')):
                key = key[4:-5]
            else:
                key = key[:-5]

            if key.lower() in map(str.lower, libs):
                finalDerp[_key] = "ok"
            else:
                finalDerp[_key] = "nope"
        return finalDerp



if __name__ == '__main__':

    home = '/home/adelina/cern/cmsdist/'
    reqMap={}
    fileReader=ReadFiles(home)
    libs =fileReader.getLibsFromFile()

    specFileNames=fileReader.getAllFiles()
    for name in specFileNames:
        reqMap[name]=fileReader.readReqFromFile(name)
    print(reqMap)
    root=node("dependencies")
    specKeys=fileReader.addDepToSpec(libs)
    root.children=[node(key+"- "+specKeys[key]) for key in reqMap.keys()]
    i=0
    for key in reqMap.keys():
        fileReader.addChildren(root.children[i],  reqMap[key], libs)
        i+=1
    root.saveTree(home+"tree.txt")

    # fileReader.saveToFile("results.txt",finalDerp)