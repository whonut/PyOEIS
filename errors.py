class OEISException(Exception):
    '''Base class for PyOEIS exceptions.'''
    pass


class NoResultsError(OEISException):
    '''Raised when a search gives no results and it is unacceptable to return
       an empty list.'''
    def __init__(self, query):
        self.query = query

    def __str__(self):
        return 'No results for query "'+self.query+'"'


class TooManyResultsError(OEISException):
    '''Raised when too many results are found for a search for them to be
       properly parsed.'''
    def __init__(self, query):
        self.query = query

    def __str__(self):
        ret = ('Too many results for query "' + self.query
               + '". Narrow your search.')
        return ret


class InvalidQueryError(OEISException):
    '''Raised when a search is invalid according to the OEIS search syntax.'''
    def __init__(self, response):
        self.response = response[response.find(':')+2:]

    def __str__(self):
        return self.response
