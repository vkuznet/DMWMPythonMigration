import glob

class FileReader(object):

    def readFile(self, path):
        with open(path) as f:
            fileLines = f.readlines()
        return fileLines

    def getFileNames(self,path,type):
        fileNames = []
        for filename in glob.iglob(path+'/**/*.'+type, recursive=True):
            fileNames.append(filename)
        return fileNames

