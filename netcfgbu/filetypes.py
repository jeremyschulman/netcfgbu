import csv
import re


class CommentedCsvReader(csv.DictReader):
    def __next__(self):
        value = super(CommentedCsvReader, self).__next__()

        if value[self.fieldnames[0]].startswith("#"):
            return self.__next__()

        return value


class TextFileReader(object):
    wordsep_re = re.compile(r"\s+|,")

    def __init__(self, fileio):
        self._lines = fileio.readlines()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            line_item = self._lines.pop(0)
        except IndexError:
            raise StopIteration

        if line_item.startswith("#"):
            return self.__next__()

        host = next(iter(self.wordsep_re.split(line_item)), None)

        if host:
            return host

        return self.__next__()
