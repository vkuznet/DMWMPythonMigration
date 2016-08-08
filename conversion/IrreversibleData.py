class IrreversibleData(object):
    """
    Some of the code from templates can't be converted
    This class saves information about irreversible code
    """

    def __init__(self, fileName, lineStart, lineEnd, type, oldValue):
        self.lineStart = lineStart
        self.lineEnd = lineEnd
        self.fileName = fileName
        self.type = type
        self.oldValue = oldValue
        self.codeReplacment = ["-No replacment-"]

    @property
    def codeReplacment(self):
        return self._codeReplacment

    @codeReplacment.setter
    def codeReplacment(self, replacment):
        if not isinstance(replacment, list):
            raise ValueError("Replacment should be a list")
        self._codeReplacment = replacment


