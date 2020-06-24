import csv


class CommentedCsvReader(csv.DictReader):
    def __next__(self):
        value = super(CommentedCsvReader, self).__next__()

        if value[self.fieldnames[0]].startswith("#"):
            return self.__next__()

        return value


# TODO: not in use just yet.
# class TextFileReader(object):
#     wordsep_re = re.compile(r"\s+|,")
#
#     def __init__(self, fileio, index=0):
#         self._index = index
#         self._lines = fileio.readlines()
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         try:
#             line_item = self._lines.pop(0)
#         except IndexError:
#             raise StopIteration
#
#         if line_item.startswith("#"):
#             return self.__next__()
#
#         try:
#             return self.wordsep_re.split(line_item)[self._index]
#         except IndexError:
#             pass
#
#         return self.__next__()
