import argparse
import importlib

from caniusepython3 import pypi


def isModuleInstalled(moduleName):
    """
    Checks if module is available in standard/installed libs

    :param moduleName: name of library/module
    :return: returns boolean
    """
    spam_spec = importlib.find_loader(moduleName)
    found = spam_spec is not None
    return found


def main(depFile):
    """
    Reads dependencies and checks if they are available in python 3
    Prints and saves module names that are not supported into the file

    :param depFile: path to dependency file
    """
    with open(depFile) as f:
        fileLines = f.readlines()

    # get list of py3 supported libs
    py3_projects = pypi.all_py3_projects()
    # get list of available libs
    all = pypi.all_projects()
    # remove new line symbols
    fileLines = filter(None, list(map(lambda x: x.strip(), fileLines)))
    notSupportedList = []
    notFoundList = []
    for line in fileLines:
        # check if module is from 3rd party or in standard lib
        if line.lower() in all or isModuleInstalled(line):
            # check if it is not supported
            if line.lower() not in py3_projects and not isModuleInstalled(line):
                notSupportedList.append(line)
        else:
            notFoundList.append(line)

    print("Modules not supported in python3: \n" + "\n".join(notSupportedList)+"\nFor more info go to: "+depFile)
    with open(depFile, mode='w+', encoding='utf-8') as myfile:
        myfile.write("Modules not supported in python3: \n" + "\n".join(notSupportedList) + "\n" + "-" * 50 +
                     "\nModules not found: \n" + "\n".join(notFoundList))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="path", required=True, action='store')
    opts = parser.parse_args()
    main(opts.path)
