import requests
from sequence import Sequence
import regex


class OEISClient(object):
    SEARCH_URL = 'http://oeis.org/search'

    def __init__(self):
        self.session = requests.Session()
        self.session.params = {'fmt': 'text'}

    def _parse_sequence(self, sequence_entry):
        s = Sequence()
        lines = [l.split(' ', 2) for l in sequence_entry.split('\n')]
        for l in lines:
            flag = l[0][1]
            # parse identification line
            if flag == 'I':
                s.id = l[1]
                try:
                    s.alt_ids = l[2].split(' ')
                except IndexError:
                    pass
                continue
            # parse unsigned sequence lines
            if flag in 'STU':
                new_terms = [t for t in l[2].split(',') if t != '']
                s.unsignedterms.extend(new_terms)
                continue
            # parse signed sequence lines
            if flag in 'VWX':
                new_terms = [t for t in l[2].split(',') if t != '']
                self.signedterms.extend(new_terms)
                continue
            # parse sequence name line
            if flag == 'N':
                s.name = l[2]
                continue
            # parse detailed reference lines
            if flag == 'D':
                self.references.append(l[2])
                continue
            # parse link lines
            if flag == 'H':
                link_text = l[2][:l.find('<')]
                link_text = link_text + l[l.find('>')+1:l.rfind('<')]
                link_text = link_text + l[l.rfind('>')+1:]
                link_url = l[2][l.find('href=')+6:l.find('.html')+5]
                s.links.append({'text': link_text, 'url': link_url})
                continue
            # parse formula line
            if flag == 'F':
                s.formulas.append(l[2])
                continue
            # parse cross-reference lines
            if flag == 'Y':
                s.crossreferences.append(l[2])
                continue
            # parse author line
            if flag == 'A':
                
        return s

    def get_sequence_by_id(self, id):
        query = 'id:' + id
        response = self.session.get(self.SEARCH_URL, params={'q': query})
        return self._parse_sequence(response.text)

c = OEISClient()
primes = c.get_sequence_by_id('A000040')
print primes.id
