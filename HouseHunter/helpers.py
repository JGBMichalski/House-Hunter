import re

class Helpers:
    def removeHTMLTags(str):
        """
        Removes HTML Tags from a supplied string.
        """
        expr = re.compile('<.*?>')
        cleanedText = re.sub(expr, '', str)
        return cleanedText