import requests
from sequence import Sequence
import regex
import helpers
from errors import NoResultsError, InvalidQueryError, TooManyResultsError
from partialmethod import partialmethod


class OEISClient(object):
    '''Maintains a :class:`Session<requests:requests.Session>` and contains
       all methods for querying the OEIS.'''

    SEARCH_URL = 'http://oeis.org/search'

    def __init__(self):
        self.session = requests.Session()
        self.session.params = {'fmt': 'text'}

    def _check_response(self, response_text, query):
        '''Checks reponses from the OEIS, raises relevant exception upon
           error.'''

        # if no results are found, raise appropriate exception
        if response_text.find('\nNo results.\n') != -1:
            raise NoResultsError(query)

        # if query has invalid syntax, raise appropriate exception
        if response_text.find('Could not parse search query:') != -1:
            raise InvalidQueryError(response_text)

        # if there are too many results to display, raise appropriate exception
        if response_text.find('Too many results.') != -1:
            raise TooManyResultsError(query)

    def _parse_sequence(self, sequence_entry):
        '''Builds a Sequence object from an individual internal format
           sequence entry and returns it.'''

        s = Sequence()

        # parse %I
        id_search = regex.id.search(sequence_entry)
        s.id = id_search.groups()[0]
        s.alt_ids.extend(id_search.groups()[1:])

        # parse %S, %T and %U
        unsigned_findall = regex.unsigned.findall(sequence_entry)
        unsigned_strs = helpers.parse_comma_separated_findall(unsigned_findall)
        s.unsigned = map(int, unsigned_strs)

        # parse %V, %W and %X
        try:
            signed_findall = regex.signed.findall(sequence_entry)
            signed_strs = helpers.parse_comma_separated_findall(signed_findall)
            s.signed = map(int, signed_strs)
        except AttributeError:
            pass

        # parse %N
        name_search = regex.name.search(sequence_entry)
        s.name = name_search.groups()[0]

        # parse %D
        try:
            reference_findall = regex.reference.findall(sequence_entry)
            s.references = reference_findall
        except AttributeError:
            pass

        # parse %H
        try:
            link_findall = regex.link.findall(sequence_entry)
            for l in link_findall:
                url = l[1]
                text = l[0] + l[2] + l[3]
                s.links.append({'text': text, 'url': url})
        except AttributeError:
            pass

        # parse %F
        try:
            formula_findall = regex.formula.findall(sequence_entry)
            s.formulae.extend(formula_findall)
        except AttributeError:
            pass

        # parse %Y
        try:
            crossref_findall = regex.cross_reference.findall(sequence_entry)
            s.cross_references.extend(crossref_findall)
        except AttributeError:
            pass

        # parse %A
        author_search = regex.author.search(sequence_entry)
        s.author = author_search.groups()[0]

        # parse %O
        offset_search = regex.offset.search(sequence_entry)
        s.offset = tuple(map(int, offset_search.groups()))

        # parse %E
        try:
            error_findall = regex.error.findall(sequence_entry)
            s.errors.extend(error_findall)
        except AttributeError:
            pass

        # parse %e
        try:
            example_findall = regex.example.findall(sequence_entry)
            s.examples.extend(example_findall)
        except AttributeError:
            pass

        # parse %p
        try:
            maple_search = regex.maple.search(sequence_entry)
            s.maple = maple_search.groups()[0]
        except AttributeError:
            pass

        # parse %t
        try:
            mathematica_search = regex.mathematica.search(sequence_entry)
            s.mathematica = mathematica_search.groups()[0]
        except AttributeError:
            pass

        # parse %o
        try:
            otherprogs_findall = regex.other_programs.findall(sequence_entry)
            s.other_programs.extend(otherprogs_findall)
        except AttributeError:
            pass

        # parse %K
        keywords_findall = regex.keywords.findall(sequence_entry)
        s.keywords = helpers.parse_comma_separated_findall(keywords_findall)

        # parse %C
        try:
            comment_findall = regex.comment.findall(sequence_entry)
            s.comments.extend(comment_findall)
        except AttributeError:
            pass

        return s

    def _parse_response(self, response_text):
        '''Takes a multi-sequence internal format response & builds Sequence
           objects for each sequence. Returns a list of the Sequence
           objects.'''

        blankline_split = regex.blank_line.split(response_text)
        seqs = []
        if blankline_split[1][1] == u'No results.':
            return seqs

        for entry in blankline_split[2:-1]:      # stripping header & footer
            seqs.append(self._parse_sequence(entry))

        return seqs

    def lookup_by(self, prefix, query, max_seqs=10, list_func=False):
        '''If *prefix* is `""`, search OEIS with string *query*,
           otherwise use string '*prefix*:*query*'.

           If *list_func* is true, return a list of at most
           *max_seqs* :class:`Sequence <sequence.Sequence>` objects or else an
           empty list if there are no results. If *list_func* is false, return
           the first Sequence found, or else raise a
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
    get_by_id.__doc__ = '''Returns a :class:`Sequence <sequence.Sequence>` for
                           the sequence of the specified ID, else raises
                           :exc:`NoResultsError`.'''
    lookup_by_name = partialmethod(lookup_by, 'name', list_func=True)
    lookup_by_name.__doc__ = '''Returns a list of
                                :class:`Sequence <sequence.Sequence>` objects
                                whose names contain *name*.'''
    lookup_by_author = partialmethod(lookup_by, 'author', list_func=True)
    lookup_by_author.__doc__ = '''Returns a list of
                                  :class:`Sequence <sequence.Sequence>` objects
                                  whose authors contain *author*.'''

    def lookup_by_keywords(self, keywords):
        '''Returns a list of at most *max_seqs*
           :class:`Sequence <sequence.Sequence>` objects which are tagged with
           *keywords*.'''

        query = '"'+' '.join(keywords)+'"'
        return self.lookup_by('keyword', query, list_func=True)

    def lookup_by_terms(self, terms, **kwargs):
        '''Returns a list of at most *max_seqs*
           :class:`Sequence <sequence.Sequence>` objects which contain *terms*
           anywhere within them. If none exist, returns an empty list. If
           *ordered* is false, terms may be in any order. If *signed* is false,
           terms may be positive or negative.'''

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
        '''Returns a :class:`Sequence <sequence.Sequence>` object for the
           first sequence, sorting by relevance, which contains *terms*
           consecutively.'''

        seqs = self.lookup_by_terms(*terms)
        return seqs[0]
