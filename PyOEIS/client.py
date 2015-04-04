import requests
from sequence import Sequence
import regex
from errors import NoResultsError, InvalidQueryError, TooManyResultsError
from partialmethod import partialmethod


class OEISClient(object):
    '''Maintains a :class:`Session<requests:requests.Session>` and
       contains all methods for querying the OEIS.'''

    SEARCH_URL = 'http://oeis.org/search'

    def __init__(self):
        self.session = requests.Session()
        self.session.params = {'fmt': 'text'}

    def _check_response(self, response_text, query):
        '''Checks reponses from the OEIS, raises relevant exception
           upon error.'''

        # if no results are found, raise appropriate exception
        if response_text.find('\nNo results.\n') != -1:
            raise NoResultsError(query)

        # if query has invalid syntax, raise appropriate exception
        if response_text.find('Could not parse search query:') != -1:
            raise InvalidQueryError(response_text)

        # if there are too many results to display, raise appropriate exception
        if response_text.find('Too many results.') != -1:
            raise TooManyResultsError(query)

    def _parse_response(self, response_text):
        '''Takes a multi-sequence internal format response & builds
           Sequence objects for each sequence. Returns a list of the
           Sequence objects.'''

        blankline_split = regex.blank_line.split(response_text)
        seqs = []
        if blankline_split[1][1] == u'No results.':
            return seqs

        for entry in blankline_split[2:-1]:      # stripping header & footer
            seqs.append(Sequence(entry))

        return seqs

    def lookup_by(self, prefix, query, max_seqs=10, list_func=False):
        '''If *prefix* is `""`, search OEIS with string *query*,
           otherwise use string '*prefix*:*query*'.

           If *list_func* is true, return a list of at most
           *max_seqs* :class:`Sequence <sequence.Sequence>` objects or
           else an empty list if there are no results. If *list_func*
           is false, return the first Sequence found, or else raise a
           :exc:`NoResultsError <errors.NoResultsError>`.'''

        if not prefix:
            search_string = query
        else:
            search_string = '{}:{}'.format(prefix, query)

        try:
            response = self.session.get(self.SEARCH_URL,
                                        params={'q': search_string})
            self._check_response(response.text, search_string)
            seqs = self._parse_response(response.text)
            num_seqs = regex.showing_line.search(response.text).groups()[0]
            for i in xrange(10, (int(num_seqs) - (int(num_seqs) % 10)) + 1):
                if len(seqs) < max_seqs:
                    response = self.session.get(self.SEARCH_URL,
                                                params={'q': search_string,
                                                        'start': str(i)})
                    self._check_response(response.text, search_string)
                    seqs.extend(self._parse_response(response.text))
                else:
                    break

            if len(seqs) > max_seqs:
                seqs = seqs[:max_seqs]

            if list_func:
                return seqs
            else:
                return seqs[0]

        except NoResultsError:
            if list_func:
                return []
            else:
                raise NoResultsError(search_string)

    get_by_id = partialmethod(lookup_by, 'id')
    get_by_id.__doc__ = '''Returns a
                           :class:`Sequence <sequence.Sequence>` for
                           the sequence of the specified ID, else
                           raises :exc:`NoResultsError`.'''
    lookup_by_name = partialmethod(lookup_by, 'name', list_func=True)
    lookup_by_name.__doc__ = '''Returns a list of
                                :class:`Sequence <sequence.Sequence>`
                                objects whose names contain *name*.'''
    lookup_by_author = partialmethod(lookup_by, 'author', list_func=True)
    lookup_by_author.__doc__ = '''Returns a list of
                                  :class:`Sequence <sequence.Sequence>`
                                  objects whose authors contain
                                  *author*.'''

    def lookup_by_keywords(self, keywords):
        '''Returns a list of at most *max_seqs*
           :class:`Sequence <sequence.Sequence>` objects which are
           tagged with *keywords*.'''

        query = '"'+' '.join(keywords)+'"'
        return self.lookup_by('keyword', query, list_func=True)

    def lookup_by_terms(self, terms, **kwargs):
        '''Returns a list of at most *max_seqs*
           :class:`Sequence <sequence.Sequence>` objects which
           contain *terms* anywhere within them. If none exist,
           returns an empty list. If *ordered* is false, terms may be
           in any order. If *signed* is false, terms may be positive
           or negative.'''

        # if order does not matter, specify in search query (space-delimited)
        if ('ordered' in kwargs) and not kwargs['ordered']:
            query = ' '.join(terms)
        else:
            # ordered is assumed True
            query = ','.join(map(str, terms))

        # if sign does not matter, specify in search query (space-delimited)
        if ('signed' in kwargs) and not kwargs['signed']:
            return self.lookup_by('seq', query, list_func=True)
        else:
            # signed is assumed True
            return self.lookup_by('signed', query, list_func=True)

    def extend_sequence(self, *terms):
        '''Returns a :class:`Sequence <sequence.Sequence>` object for
           the first sequence, sorting by relevance, which contains
           *terms* consecutively.'''

        seqs = self.lookup_by_terms(*terms)
        return seqs[0]
