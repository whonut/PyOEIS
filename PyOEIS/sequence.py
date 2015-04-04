import regex
from helpers import parse_comma_separated_findall
from errors import MalformedSequenceError, NoFunctionError
from math import factorial as fac  # NOQA


class Sequence(object):
    '''Takes internal format sequence entry as constructor argument.

       Has attributes to contain information for each field of a
       sequence entry in the OEIS and methods fot retrieving a certain
       number of the sequence's signed or unsigned terms.'''

    def __init__(self, sequence_entry):
        # parse %I
        try:
            id_search = regex.id.search(sequence_entry)
            self.id = id_search.groups()[0]
        except AttributeError:
            raise MalformedSequenceError('%I')
        self.alt_ids = []
        if id_search.groups()[1] is not None:
            self.alt_ids.extend(id_search.groups()[1:])

        # parse %S, %T and %U
        try:
            unsigned_findall = regex.unsigned.findall(sequence_entry)
            unsigned_strs = parse_comma_separated_findall(unsigned_findall)
            self.unsigned_list = map(int, unsigned_strs)
        except AttributeError:
            raise MalformedSequenceError('%S')

        # parse %V, %W and %X
        try:
            signed_findall = regex.signed.findall(sequence_entry)
            signed_strs = parse_comma_separated_findall(signed_findall)
            self.signed_list = map(int, signed_strs)
        except AttributeError:     # sequence entry has no %V, %W or %X
            self.signed_list = []

        # parse %N
        try:
            name_search = regex.name.search(sequence_entry)
            self.name = name_search.groups()[0]
            self.raw_formula = name_search.groups()[1]
        except AttributeError:
            raise MalformedSequenceError('%N')

        # parse %D
        try:
            reference_findall = regex.reference.findall(sequence_entry)
            self.references = reference_findall
        except AttributeError:     # sequence entry has no %D
            self.references = []

        # parse %H
        try:
            link_findall = regex.link.findall(sequence_entry)
            for l in link_findall:
                url = l[1]
                text = l[0] + l[2] + l[3]
                self.links.append({'text': text, 'url': url})
        except AttributeError:     # sequence entry has no %H
            self.links = []

        # parse %F
        try:
            formula_findall = regex.formula.findall(sequence_entry)
            self.formulae = formula_findall
        except AttributeError:     # sequence entry has no %F
            self.formulae = []

        # parse %Y
        try:
            crossref_findall = regex.cross_reference.findall(sequence_entry)
            self.cross_references = crossref_findall
        except AttributeError:     # sequence entry has no %Y
            self.cross_references = []

        # parse %A
        try:
            author_search = regex.author.search(sequence_entry)
            self.author = author_search.groups()[0]
        except AttributeError:
            raise MalformedSequenceError('%A')

        # parse %O
        try:
            offset_search = regex.offset.search(sequence_entry)
            self.offset = tuple(map(int, offset_search.groups()))
        except AttributeError:
            raise MalformedSequenceError('%O')

        # parse %E
        try:
            error_findall = regex.error.findall(sequence_entry)
            self.errors = error_findall
        except AttributeError:     # sequence entry has no %E
            self.errors = []

        # parse %e
        try:
            example_findall = regex.example.findall(sequence_entry)
            self.examples = example_findall
        except AttributeError:     # sequence entry has no %e
            self.examples = []

        # parse %p
        try:
            maple_search = regex.maple.search(sequence_entry)
            self.maple = maple_search.groups()[0]
        except AttributeError:     # sequence entry has no %p
            self.maple = None

        # parse %t
        try:
            mathematica_search = regex.mathematica.search(sequence_entry)
            self.mathematica = mathematica_search.groups()[0]
        except AttributeError:     # sequence entry has no %t
            self.mathematica = None

        # parse %o
        try:
            otherprogs_findall = regex.other_programs.findall(sequence_entry)
            self.other_programs = otherprogs_findall
        except AttributeError:     # sequence entry has no %o
            self.other_programs = []

        # parse %K
        try:
            keywords_findall = regex.keywords.findall(sequence_entry)
            self.keywords = parse_comma_separated_findall(keywords_findall)
        except AttributeError:
            raise MalformedSequenceError('%K')

        # parse %C
        try:
            comment_findall = regex.comment.findall(sequence_entry)
            self.comments = comment_findall
        except AttributeError:     # sequence entry has no %C
            self.comments = []

        # create generate method
        self.generate = self._make_generate()
        self.generate.__doc__ = """
                                If a parsable formula exists, returns
                                the *n*th term of the sequence, else
                                raises a
                                :exc:`NoFunctionError <errors.NoFunctionError>`
                                """

    def __str__(self):
        return '<Sequence object for "' + self.name + '">'

    def _make_generate(self):
        raw = self.raw_formula
        raw = raw.replace(u' ', u'')
        candidates = raw.split(u'=')
        valid_formula = None
        for s in candidates:
            valid = regex.valid.match(s) is not None
            if valid:
                valid_formula = s
                break

        if valid_formula is None:
            def generate(n):
                raise NoFunctionError(self)
        else:
            def make_evaluable(expr):
                parens = (p[1:-1] for p in regex.parens.findall(expr))
                evaluable = expr
                for pair in zip(parens, map(make_evaluable, parens)):
                    evaluable = evaluable.replace(pair[0], pair[1])
                # Handle factorials ('!')
                evaluable = regex.fac.sub(lambda m: '(fac('+m.groups()[0]+'))',
                                          evaluable)
                # Parenthesise operands (integers and 'n')
                evaluable = regex.operands.sub(lambda m: '('+m.groups()[0]+')',
                                               evaluable)
                # Handle implictit ('(2)(n)' and 'fac(i)fac(j)')
                evaluable = regex.opp_paren.sub(')*(', evaluable)
                # Handle exponentiation ('^')
                evaluable = regex.expo.sub('**', evaluable)
                return evaluable

            to_eval = make_evaluable(valid_formula)

            def generate(n):
                return eval(to_eval)

        return generate

    def unsigned(self, n):
        '''Returns the first *n* unsigned integers in the sequence.'''
        return self.unsigned_list[:n]

    def signed(self, n):
        '''Returns the first *n* signed integers in the sequence.'''
        return self.signed_list[:n]
