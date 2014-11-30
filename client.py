# A limitation of the internal format of the OEIS internal format means only
# the first 10 terms are returned for any query.

import requests
from sequence import Sequence
import regex
import helpers
from errors import NoResultsError, InvalidQueryError, TooManyResultsError


class OEISClient(object):
    SEARCH_URL = 'http://oeis.org/search'

    def __init__(self):
        self.session = requests.Session()
        self.session.params = {'fmt': 'text'}

    def _check_response(self, response_text, query):
        '''Checks reponses from the OEIS, raises exception else allows outer
           functions to handle ambiguous cases'''

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
           sequence entry and returns it. Returns None for query with no
           results.'''

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
        signed_findall = regex.signed.findall(sequence_entry)
        signed_strs = helpers.parse_comma_separated_findall(signed_findall)
        s.signed = map(int, signed_strs)

        # parse %N
        name_search = regex.name.search(sequence_entry)
        s.name = name_search.groups()[0]

        # parse %D
        reference_findall = regex.reference.findall(sequence_entry)
        s.references = reference_findall

        # parse %H
        link_findall = regex.link.findall(sequence_entry)
        for l in link_findall:
            url = l[1]
            text = l[0] + l[2] + l[3]
            s.links.append({'text': text, 'url': url})

        # parse %F
        formula_findall = regex.formula.findall(sequence_entry)
        s.formulae.extend(formula_findall)

        # parse %Y
        crossreference_findall = regex.cross_reference.findall(sequence_entry)
        s.cross_references.extend(crossreference_findall)

        # parse %A
        author_search = regex.author.search(sequence_entry)
        s.author = author_search.groups()[0]

        # parse %O
        offset_search = regex.offset.search(sequence_entry)
        s.offset = tuple(map(int, offset_search.groups()))

        # parse %E
        error_findall = regex.error.findall(sequence_entry)
        s.errors.extend(error_findall)

        # parse %e
        example_findall = regex.example.findall(sequence_entry)
        s.examples.extend(example_findall)

        # parse %p
        maple_search = regex.maple.search(sequence_entry)
        s.maple = maple_search.groups()[0]

        # parse %t
        mathematica_search = regex.mathematica.search(sequence_entry)
        s.mathematica = mathematica_search.groups()[0]

        # parse %o
        otherprograms_findall = regex.other_programs.findall(sequence_entry)
        s.other_programs.extend(otherprograms_findall)

        # parse %K
        keywords_findall = regex.keywords.findall(sequence_entry)
        s.keywords = helpers.parse_comma_separated_findall(keywords_findall)

        # parse %C
        comment_findall = regex.comment.findall(sequence_entry)
        s.comments.extend(comment_findall)

        return s

    def _parse_response(self, response_text):
        '''Takes a multi-sequence internal format response & builds Sequence
           objects for each sequence. Returns a list of the Sequence objects'''

        blankline_split = regex.blank_line.split(response_text)
        seqs = []
        if blankline_split[1][1] == u'No results.':
            return seqs

        for entry in blankline_split[2:-1]:      # stripping header & footer
            seqs.append(self._parse_sequence(entry))

        return seqs

    def _int_lookup(self, search_string):
        '''Internal version of lookup_by_string with no error-handling.
           Used to implement other lookup functions'''
        response = self.session.get(self.SEARCH_URL,
                                    params={'q': search_string})
        self._check_response(response.text, search_string)
        seqs = self._parse_response(response.text)
        return seqs

    def lookup_by_string(self, search_string):
        '''Returns a list of sequences matching search_string'''
        try:
            return self._int_lookup(search_string)
        except NoResultsError:      # return empty list if no sequences match
            return []

    def get_sequence_by_id(self, id):
        '''Returns a Sequence object for the sequence of the specified ID,
           else raises NoResultsError'''
        seq = self._int_lookup('id:'+id)[0]
        return seq

    def lookup_by_terms(self, *terms, **kwargs):
        '''Returns Sequences which have the given terms anywhere within them.
           If none exist, returns an empty list. If the keyword argument
           'ordered' is given as False, terms may be in any order. If the
           keyword argument 'signed' is given as False, terms may be positive
           or negative.'''

        # if order does not matter, specify in search query (space-delimited)
        if ('ordered' in kwargs) and not kwargs['ordered']:
            query = ' '.join(terms)
        else:
            # ordered is assumed True
            query = ','.join(map(str, terms))

        # if sign does not matter, specify in search query (space-delimited)
        if ('signed' in kwargs) and not kwargs['signed']:
            query = 'seq:' + query
        else:
            # signed is assumed True
            query = 'signed:' + query

        try:
            return self._int_lookup(query)
        except NoResultsError:
            return []
