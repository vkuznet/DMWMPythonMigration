import argparse
import importlib
import requests


def isModuleInstalled(moduleName):
    """
    Checks if module is available in standard/installed libs

    :param moduleName: name of library/module
    :return: returns boolean
    """
    spam_spec = importlib.find_loader(moduleName)
    found = spam_spec is not None
    return found

def supports_py3(project_name):
    """Check with PyPI if a project supports Python 3."""
    request = requests.get("https://pypi.org/pypi/{}/json".format(project_name))
    if request.status_code >= 400:
        return False
    response = request.json()
    return any(c.startswith("Programming Language :: Python :: 3")
               for c in response["info"]["classifiers"])

def main(depFile):
    """
    Reads dependencies and checks if they are available in python 3
    Prints and saves module names that are not supported into the file

    :param depFile: path to dependency file
    """
    with open(depFile) as f:
        fileLines = f.readlines()
    # remove new line symbols
    fileLines = filter(None, list(map(lambda x: x.strip(), fileLines)))
    notSupportedList = []
    for line in fileLines:
        # check if module is from 3rd party or in standard lib
        if not supports_py3(line.lower()) and not isModuleInstalled(line):
            notSupportedList.append(line)

    print("Modules not supported in python3: \n" + "\n".join(notSupportedList)+"\nFor more info go to: "+depFile)
    with open(depFile, mode='w+', encoding='utf-8') as myfile:
        myfile.write("Modules not supported in python3: \n" + "\n".join(notSupportedList))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="path", required=True, action='store')
    opts = parser.parse_args()
    main(opts.path)
