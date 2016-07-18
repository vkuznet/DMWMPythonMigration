import logging
import os

import requests
import lxml.html
import sys

from node import node
import argparse


class DependencyWriter:
    "Downloads, compares and saves python 3 dependencies"
    reqMap = {}
    logger = logging.getLogger()

    def __init__(self, path):
        self.path = path
        format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=format)

    def getAllFiles(self):
        """
        Finds files in the dir and adds them to the generator

        :rtype: fileName
        """
        for root, dirs, files in os.walk(self.path):
            for name in files:
                if name.endswith(".spec"):
                    yield name

    def readReqFromFile(self, name):
        """
        Get required libraries from *.spec file

        :param name: of the file:
        :return: list: of required library names
        """
        req = []
        with open(self.path + name) as f:
            for line in f:
                li = line.lstrip()
                if li.startswith("Requires:") or li.startswith("BuildRequires:"):
                    splited = line.split()
                    del splited[:1]
                    req += splited
        self.logger.debug("Reading frome file: " + name)
        return req

    def addChildren(self, _node, dependencies, libs):
        """
        Adds children to the tree node

        :param _node:  tree node
        :param dependencies: dictionary of dependencies
        :param libs: list of libraries
        """
        values = {}
        for _value in dependencies:
            value = _value
            if (value.startswith('py2')):
                value = value[4:]
            if value.lower() in map(str.lower, libs):
                values[_value] = "ok"
            else:
                values[_value] = "no"

        _node.children = [node(dep + "- " + values[dep]) for dep in dependencies]
        i = 0
        for dep in dependencies:
            if dep + ".spec" in self.reqMap.keys():
                self.addChildren(_node.children[i], self.reqMap[dep + ".spec"], libs)
            i += 1

    def retrieveLibs(self):
        """
        Retrieve available python3 libraries and saves them to file python3AvailableLibs.txt
        """
        libs = []
        try:
            response = requests.get('https://pypi.python.org/pypi?:action=browse&c=533&show=all')
            dom = lxml.html.fromstring(response.content)
            for link in dom.xpath('//table[@class="list"]//a/text()'):  # select the text from links
                libs.append(link)
        except Exception:
            self.logger.error("Could not retrieve libraries from pypi.python.org")
            return
        with open(self.path + "python3AvailableLibs.txt", 'w') as f:
            f.write(' '.join(libs))
        self.logger.info("Python3 libraries are saved to: " + self.path + "python3AvailableLibs.txt")

    def getRetrievedLibs(self):

        """
        Returns available python 3 libraries from python3AvailableLibs.txt

        :return: list of available libraries
        """
        with open(self.path + "python3AvailableLibs.txt") as f:
            for line in f:
                splited = line.split()
        return splited

    def saveToFile(self, fileName, dic):
        """
        Saves dictionary to a file

        :param fileName of the file
        :param dic: dictionary of dependencies
        """
        with open(self.path + fileName, 'w+') as f:
            for i in dic.keys():
                f.write(i + ": " + ''.join([str(x) for x in dic[i]]) + "\n")
        self.logger.info("Saved dictionary with anotations to: " + fileName)

    def addAnotationToKeyAndValue(self, libs):
        """
        Adds annotation "ok" if dependency is in libs list
        Adds annotation "no" otherwise

        :param libs: list of python 3 libraries
        :return: comparedDependencies: list of dependencies with annotation
        """
        comparedDependencies = {}
        for _key in self.reqMap.keys():
            key = _key
            if (_key.startswith('py2')):
                key = key[4:-5]
            else:
                key = key[:-5]

            if key.lower() in map(str.lower, libs):
                comparedDependencies[_key] = "ok"
            else:
                comparedDependencies[_key] = "no"
            for _value in self.reqMap[_key]:
                value = _value
                if (_value.startswith('py2')):
                    value = value[4:]
                if value.lower() in map(str.lower, libs):
                    comparedDependencies[_value] = "ok"
                else:
                    comparedDependencies[_value] = "no"
        return comparedDependencies

    def addAnotationToKey(self, libs):
        """
        Adds annotation "ok" if dependency is in libs list
        Adds annotation "no" otherwise

        :param libs: list of python 3 libraries
        :return: comparedDependencies: list of dependencies with annotation
        """
        comparedDependencies = {}
        for _key in self.reqMap.keys():
            key = _key
            if (_key.startswith('py2')):
                key = key[4:-5]
            else:
                key = key[:-5]

            if key.lower() in map(str.lower, libs):
                comparedDependencies[_key] = "ok"
            else:
                comparedDependencies[_key] = "no"
        return comparedDependencies


def main(opts):
    "Main function"
    path = opts.path
    # set path
    fileReader = DependencyWriter(path)

    # save python 3libs
    fileReader.retrieveLibs()
    libs = fileReader.getRetrievedLibs()

    # create dictionary with dependencies
    for name in fileReader.getAllFiles():
        fileReader.reqMap[name] = fileReader.readReqFromFile(name)

    # initialize node
    root = node("dependencies")
    # add annotation for dependencies dictionary keys
    specKeys = fileReader.addAnotationToKey(libs)
    # add spec dictionary keys to tree
    root.children = [node(key + "- " + specKeys[key]) for key in fileReader.reqMap.keys()]
    i = 0
    # add remaining dependencies to tree
    for key in fileReader.reqMap.keys():
        fileReader.addChildren(root.children[i], fileReader.reqMap[key], libs)
        fileReader.logger.debug("Creating dependencies for: " + key)
        i += 1
    root.saveTree(path + opts.tree)

    if opts.results:
        fileReader.saveToFile(opts.results, fileReader.addAnotationToKeyAndValue(libs))
        fileReader.logger.debug("Saving dependencies list with anotation to:" + opts.results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create dependency tree...')
    parser.add_argument("-path", dest="path", required=True, action='store',
                        help="Directory of .spec files that contain requirements")
    parser.add_argument("-tName", dest="tree", default="tree.txt", action='store', help="Dependencies tree name")
    parser.add_argument("-rName", dest="results", action='store', help="List of dependencies with annotations")

    opts = parser.parse_args()
    main(opts)
