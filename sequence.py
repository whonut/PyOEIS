class Sequence(object):
    '''Has attributes to contain information for each field of a sequence entry
       in the OEIS and methods fot retrieving a certain number of the
       sequence's signed or unsigned terms.'''

    def __init__(self):
        self.id = None
        self.alt_ids = []
        self.unsigned = []
        self.signed = []
        self.name = None
        self.references = []
        self.links = []
        self.formulae = []
        self.cross_references = []
        self.author = None
        self.offset = None
        self.errors = []
        self.examples = []
        self.maple = None
        self.mathematica = None
        self.other_programs = []
        self.keywords = []
        self.comments = []

    def __str__(self):
        return '<Sequence object for "' + self.name + '">'

    def unsigned(self, n):
        '''Returns the first *n* unsigned integers in the sequence.'''
        return self.unsigned[:n]

    def signed(self, n):
        '''Returns the first *n* signed integers in the sequence.'''
        return self.signed[:n]
