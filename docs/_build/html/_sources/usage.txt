Usage
=====

The first thing you must do when using pyoeis is to initialise an
:class:`OEISClient <client.OEISClient>`::

  >>> import pyoeis
  >>> c = pyoeis.OEISClient()

This handles all queries to the OEIS and all methods for querying are accessed
from it. For example, say we want to access the entry for sequence A000040, the
primes::

  >>> primes = c.get_by_id('a40') 
  >>> primes.name 
  u'The prime numbers'
