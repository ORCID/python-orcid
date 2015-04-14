python-orcid
============

Current state
-------------

Under development, few features work. Readme is outdated.

Authors
-------

Mateusz Susik <mateuszsusik@gmail.com>

Notes
-----
If there are changes in ORCID API, the library might not work till the changes
will be implemented by me in this library. Pull requests and submitting issues
are very welcome.

Installation
------------

TODO, will be released on PyPI.

Introduction
------------

`ORCID <http://orcid.org/>`_ is an open, non-profit, community-based effort to
provide a registry of unique researcher identifiers and a transparent method of
linking research activities and outputs to these identifiers. ORCID is unique
in its ability to reach across disciplines, research sectors, and national
boundaries and its cooperation with other identifier systems.

ORCID offers an API (Application Programming Interface) that allows your
systems and applications to connect to the ORCID registry, including reading
from and writing to ORCID records.

There are two types of API available for developers.

PublicAPI
=========

The public API allows the developers to use the search engine and read author
records. It is available for everybody.

``` python
    import orcid
    api = orcid.PublicAPI(sandbox=True)
    # api.search (to do)
    # Get the summary
    summary = api.read_record_public('0000-0001-1111-1111', 'activities')
```

Every record in the `summary` dictionary should contain _put-codes_. Using
them, it is possible to query the specific record for details. Type of the
record and the put-code need to be provided.

``` python
    # Get the specific record
    # Available record types are:
    # 'education', 'employment', 'funding', 'peer-review', 'work'
    work = api.read_record_public('0000-0001-1111-1111', 'work', '1111')
```

MemberAPI
=========

Token
-----

This library won't help you with obtaining correct user's authentication
token. I believe it is a responsibility of the service you provide to ask a
user for the token. There are numerous Python libraries to help you with
this task. Here are few popular choices (the order below is quite random):

* `OAuthLib <https://pypi.python.org/pypi/oauthlib>`_
* `RAuth <https://rauth.readthedocs.org/en/latest/>`_
* `Requests OAuth <https://github.com/maraujop/requests-oauth>`_
* `Django OAuth Toolkit <https://github.com/evonove/django-oauth-toolkit>`_
* `Flask OAuthLib <https://github.com/lepture/flask-oauthlib>`_
* `Flask Dance <https://github.com/singingwolfboy/flask-dance>`_

If you want more options or you know more libraries worth recommending, please
check `this page. <http://oauth.net/code/>`_

Adding/updating/removing records
--------------------------------

Use ``push_data``, to send more data:

.. code-block:: python

    orcid.push_data(orcid_id, scope, token, list_with_data)

or

.. code-block:: python

    orcid.push_data(orcid_id, scope, token, xml, render=False)

if you have already prepared the ORCID XML.

The `token` is the one that you received from OAuth 3-legged authorization.

The scope can be one of ``orcid-works``, ``orcid-affiliations``, ``orcid-funding``.
These scopes allow to send different types of information to ORCID. If you
don't have the ORCID XML prepared, you should read detailed info below. It
describes the structure of the list that the ``push_data`` function should
be provided with.

Note that the majority of fields and subfields can be skipped.

When in doubt, please refer to the ORCID documetation:
`ORCID XML <http://support.orcid.org/knowledgebase/topics/32832-orcid-xml>`_

work
----

``orcid-works`` can be used when there is a need to add or update researcher's
works. It should be a list of dictionaries. Each dictionary describes a single
work. There are two mandatory fields: ``work_title`` and ``work_type``.
Each dictionary can contain following fields:

.. code-block:: python

    [{
    ...
        # Should contain the title of the work. It is a mandatory field.
        'work_title': {'title': 'The best sorting algorithm',
                       'subtitle': 'Better even than quicksort'
                       'translated_titles': [
                                             ('fr', 'Le meilleur algorithme de tri'),
                                             ('pl', 'Najlepszy algorytm sortujący')
                                            ]
                       },
    ...
    }]


.. code-block:: python
    
    [{
    ...
        'journal_title': 'The best sorting algorithm ever',
    ...
    }]


.. code-block:: python

    [{
    ...
        'short_description': 'We present an algorithm sorting any list in O(1)`,
    ...
    }]


.. code-block:: python

    [{
    ...
        # See http://support.orcid.org/knowledgebase/articles/135758-anatomy-of-a-citation
        'work_citation': (`bibtex`, `@article {Haak:2012:0953-1513:259,
                          author = "Haak, Laurel L. and Fenner, Martin and Paglione,
                          Laura and Pentz, Ed and Ratner, Howard",
                          title = "ORCID: a system to uniquely identify researchers",
                          journal = "Learned Publishing",
                          volume = "25",
                          number = "4",
                          year = "2012",
                          pages = "259-264",
                          doi = "doi:10.1087/20120404"}`
                          ),
    ...
    }]


.. code-block:: python

    [{
    ...
        # See http://support.orcid.org/knowledgebase/articles/118795
        # It is a mandatory field
        'work_type': 'report',
    ...
    }]


.. code-block:: python

    [{
    ...
        'publication_date': {'year': '2017',
                             'month': '02',
                             'day': '10'
        },
    ...
    }]


.. code-block:: python

    [{
    ...
        # See http://support.orcid.org/knowledgebase/articles/118807
        'work_external_identifiers': [('other-id', 'very unique id')],
    ...
    }]


.. code-block:: python

    [{
    ...
        'url': 'https://github.com/MSusik/python-orcid',
    ...
    }]


.. code-block:: python

    [{
    ...
        # See http://support.orcid.org/knowledgebase/articles/118843-anatomy-of-a-contributor
        'contributors': {
            'name': 'Some Body',
            'orcid': '0000-0002-1233-3422',
            'email': 'somebody@mailinator.com',
            'attributes': {
                'role': 'author',
                'sequence': 'first'
            }
        },
    ...
    }]


.. code-block:: python

    [{
    ...
        'language_code': 'en',
    ...
    }]


.. code-block:: python

    [{
    ...
        'country': ('limited', 'US')
    ...
    }]


education
---------

``orcid-affiliations`` can be used when there is a need to add or update researcher's
affiliations. It should be a list of dictionaries. Each dictionary describes a single
affiliation. Each dictionary can contain following fields:

.. code-block:: python

    [{
    ...
        # Can contain one of tho values: 'education' or 'employment'.
        # It is a mandatory field.
        'type': 'education',
    ...
    }]


.. code-block:: python

    [{
    ...
        # The name of the department
        'department': 'University of Nothing',
    ...
    }]


.. code-block:: python

    [{
    ...
        'role': 'senior professor',
    ...
    }]


.. code-block:: python

    [{
    ...
        'start_date': {'year': '2010',
                       'month': '02',
                       'day': '10'
        },
    ...
    }]


.. code-block:: python

    [{
    ...
        'end_date': {'year': '2011',
                     'month': '02',
                     'day': '10'
        },
    ...
    }]


.. code-block:: python

    [{
    ...
        'organization': ...
    ...
    }]

See `organization XML <https://github.com/MSusik/python-orcid#organization-xml>`_
for details.

employment
----------

funding
-------

``orcid-funding`` can be used when there is a need to add or update a funding
given to the researcher. It should be a list of dictionaries. 
Each dictionary describes a single funding. Each dictionary can contain
following fields:

.. code-block:: python

    [{
    ...
        # Can contain one of tho values: 'award', 'contract', 'salary-award',
        # 'grant'.
        # It is a mandatory field.
        'type': 'grant',
    ...
    }]


.. code-block:: python

    [{
    ...
        'title': 'Super grant',
    ...
    }]


.. code-block:: python

    [{
    ...
        'description': 'I got this grant because I'm very smart. I'm planning
        to buy a yacht for it.',
    ...
    }]


.. code-block:: python

    [{
    ...
        # mandatory field
        'amount': {'currency': 'USD',
                   'value': 10000},
    ...
    }]

.. code-block:: python

    [{
    ...
        'url': 'www.mypapawasarollingstone.org',
    ...
    }]


.. code-block:: python

    [{
    ...
        'start_date': {'year': '2010',
                       'month': '02',
                       'day': '10'
        },
    ...
    }]


.. code-block:: python

    [{
    ...
        'end_date': {'year': '2011',
                     'month': '02',
                     'day': '10'
        },
    ...
    }]

.. code-block:: python

    [{
    ...
        'external_ids': [{'type': 'other-id',
                          'value': 'someid',
                          'url': 'www.example.com'}],
    ...
    }]

.. code-block:: python

    [{
    ...
        'contributors': [{
            'orcid': {
                'uri': 'http://orcid.org/0000-0003-4494-0734',
                'path': '0000-0003-4494-0734',
                'host': 'orcid.org'
            },
            # credit name
            'name': 'Smith, John.',
            'email': 'john@mailinator.com',
            'attributes': {
                # one of 'lead', 'co lead', 'supported by', 'other'
                'role': 'lead',
            }
            'organization': ...
        }]
    ...
    }]

See `organization XML <https://github.com/MSusik/python-orcid#organization-xml>`_ for contributor's organization subfield

organization XML
----------------

``organization`` is a field used by ``funding`` and ``affiliations``.

It can contain following fields:

.. code-block:: python
    
    'organization': {
        ..
        'name': 'The Name Of The Organization',
        ..
    }

.. code-block:: python
    
    'organization': {
        ..
        'address': {
            'city': 'Boston',
            'region': 'MA',
            'country': 'USA'
        },
        ..
    }

.. code-block:: python

    'organization': {
        ..
        'disambiguated-organization': {
            'id': 'someid',
            # 'Ringgold' or 'ISNI'
            'source': 'ISNI'
        },
        ..
    }

additional options
------------------

Every work/affiliation/funding can have it's privacy level set by setting
``visibility`` field:

.. code-block:: python

    [{
    ...
        # one of 'private', 'limited', 'public'
        'visibility': 'private',
    ...
    }]

To do
-----

+ Peer review XMLs
+ Error handling
+ Write tests, add travis and coverage
