API
===   

:class:`OEISClient <client.OEISClient>` objects
-----------------------------------------------

.. autoclass:: client.OEISClient
  :members: lookup_by, lookup_by_keywords, lookup_by_terms

  .. method:: get_by_id(id)
  
    Returns a :class:`Sequence <sequence.Sequence>` for the sequence with the
    ID *id*, or else raises :exc:`NoResultsError <errors.NoResultsError>`.

    .. note::

      On the OEIS website, IDs are displayed with an uppercase letter and 6
      (for A IDs) or 4 (for M and N IDs) digits. However, this method does not
      require an uppercase letter or leading zeros to be used.

  .. method:: lookup_by_name(name, max_seqs=10)

    Returns a list of at most *max_seqs* :class:`Sequence <sequence.Sequence>` 
    objects whose names contain *name*.

    .. note::

      Sequences are retrieved in sets of 10 and sequences are then removed if
      necessary. So, there is no speed improvement between, for example, a 
      *max_seqs* of 10 and one of 15. This applies to all methods with a
      *max_seqs* argument.


  .. method:: lookup_by_author(author, max_seqs=10)

     Returns a list of at most *max_seqs* :class:`Sequence <sequence.Sequence>`
     objects whose authors contain *author*.
  
  
:class:`Sequence <sequence.Sequence>` objects
---------------------------------------------
.. autoclass:: sequence.Sequence
   :members: signed, unsigned

   .. method:: generate(n)

      If a parsable formula exists, returns the *nth* term of the sequence, else
      raises a :exc:`NoFunctionError <errors.NoFunctionError>`.


Attributes
^^^^^^^^^^

================ ==============================================================
id               The sequence's unique ID in the OEIS, as a string. Begins 'A'.
alt_ids          Other IDs, as a list of strings beginning 'M' and 'N' which 
                 the sequence carried in the "The Encyclopedia of Integer
                 Sequences", 1995 or the "Handbook of Integer Sequences", 1973,
                 respectively.
unsigned_list    A list of terms in the sequence without any minus signs.
signed_list      A list of terms in the sequence *including* any minus signs.
name             The name of the sequence, as a string.
references       A list of references to the sequence.
links            A list of links about the sequence.
formulae         Formulae for generating the sequence, as a list of strings.
cross_references Cross-references to the sequence from elsewhere in the OEIS,
                 as a list of strings.
author           The author of the sequence entry, as a string.
offset           The subscript of the first term and the position of the first
                 term whose modulus exceeds 1, as a tuple of two numbers.
errors           Errors in the sequence entry, as a list of strings.
examples         Examples to illustrate the sequence, as a list of strings.
maple            Maple code to generate the sequence, as a string.
mathematica      Mathematica code to generate the sequence, as a string.
other_programs   Code to generate the sequence in other programs/languages, as
                 a list of strings.
keywords         The sequence's keywords, as a list of strings.
comments         Comments on the sequence entry, as a list of strings.
================ ==============================================================

More information about the fields in a sequence entry can be found `here
<http://oeis.org/eishelp2.html>`_.

:mod:`Errors <errors>`
----------------------

.. automodule:: errors
  :members:
