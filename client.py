import requests
from sequence import Sequence
import regex
import helpers


class OEISClient(object):
    SEARCH_URL = 'http://oeis.org/search'

    def __init__(self):
        self.session = requests.Session()
        self.session.params = {'fmt': 'text'}

    def _parse_sequence(self, sequence_entry):
        s = Sequence()

        # parse %I
        id_search = regex.id.search(sequence_entry)
        s.id = id_search.groups()[0]
        s.alt_ids.extend(id_search.groups()[1:])

        # parse %S, %T and %U
        unsigned_findall = regex.unsigned.findall(sequence_entry)
        s.unsigned = helpers.parse_comma_separated(unsigned_findall)

        # parse %V, %W and %X
        signed_findall = regex.signed.findall(sequence_entry)
        s.signed = helpers.parse_comma_separated(signed_findall)
        return s

    def get_sequence_by_id(self, id):
        query = 'id:' + id
        response = self.session.get(self.SEARCH_URL, params={'q': query})
        return self._parse_sequence(response.text)
