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

    def __str__(self):
        """
        Formats information about failed conversions to string

        :return: formated string
        """
        return "Could not fully convert lines: {0} - {1} in {2}." \
               " {3} expresion should be converted manualy.\nCode:\n{4}" \
               "\nChanged to:\n{5}\n{6}".format(self.lineStart + 1, self.lineEnd + 1, self.fileName, self.type.value[0],
                                                "".join(self.oldValue), "".join(self.codeReplacment), "-" * 100)
