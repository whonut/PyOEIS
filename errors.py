class OEISException(Exception):
    '''Base class for PyOEIS exceptions'''
    pass


class NoResultsError(OEISException):

    def __init__(self, query):
        self.query = query

    def __str__(self):
        return 'No results for query "'+self.query+'"'


class TooManyResultsError(OEISException):

    def __init__(self, query):
        self.query = query

    def __str__(self):
        ret = ('Too many results for query "' + self.query
               + '". Narrow your search.')
        return ret


class InvalidQueryError(OEISException):

    def __init__(self, response):
        self.response = response[response.find(':')+2:]

    def __str__(self):
        return self.response
