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

.. code-block:: python

    import orcid
    api = orcid.PublicAPI(sandbox=True)
    search_results = api.search_public('text:English')
    # Get the summary
    summary = api.read_record_public('0000-0001-1111-1111', 'activities')


Every record in the `summary` dictionary should contain *put-codes*. Using
them, it is possible to query the specific record for details. Type of the
record and the put-code need to be provided.

.. code-block:: python

    # Get the specific record
    # Available record types are:
    # 'education', 'employment', 'funding', 'peer-review', 'work'
    work = api.read_record_public('0000-0001-1111-1111', 'work', '1111')


MemberAPI
=========

The member API allows the developers to add/change/remove records if their
code led the user through the authentication process. To modify the records
one needs a token which can be obtained following the OAuth 3-legged
authorization process.

The member API lets the developer obtain more information when using the
search API or fetching the records.

To create an instance of the member API handler, the institution key and the
institution secret have to be provided.

.. code-block:: python

    import orcid
    api = orcid.MemberAPI('institution_key', 'institution_secret',
                          sandbox=True)
    search_results = api.search_member('text:English')
    # Get the summary
    summary = api.read_record_member('0000-0001-1111-1111', 'activities')

All the methods from the public API are available in the member API.

Token
-----

So far, the library doesn't provide any way to get the user token. The feature
will be implemented in the future, though.

To obtain a token, you can use one of the libraries below:

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

Using the member API, one can add/update/remove records from the ORCID profile.

.. code-block:: python

    api.add_record('author-orcid', 'token', 'work',
                   {'title': 'Title', 'type': 'artistic-performance'})

    # Change the type to 'other'
    api.update_record('author-orcid', 'token', 'work', 'put-code',
                      {'type': 'other'})
    api.remove_record('author-orcid', 'token', 'work', 'put-code')


The ``token`` is the string received from OAuth 3-legged authorization.

``work`` is of the types of records. Every time a record is modified, the type
has to be specified. The available types are:
+ activities
+ education
+ employment
+ funding
+ peer-review
+ work

The last argument is the record itself. You can pass a python dictionary
(see the explanation below) or an xml.

.. code-block:: python

    api.add_record('author-orcid', 'token', 'work',
                   xml='<work>xml content</work>')


If xml is not provided, it will be rendered by the library. Here are some
examplary dictionaries that can be passed as an argument:

work
----

Minimal example, only the mandatory fields are filled:

.. code-block:: python

    {
        'title': {'title': 'API Test Title'},
        'type': 'journal-article'
    }

An example where all the fields are filled.

In case of doubts, see `work XML <http://members.orcid.org/api/xml-orcid-works>`_

.. code-block:: python

    {
        'title': {'title': 'The best sorting algorithm',
                  'subtitle': 'My Subtitle',
                  'translated_titles': [
                        {'language_code': 'fr',
                         'translated_title': 'API essai Titre'}
                  ]
                 },
        'journal_title': 'Journal Title',
        'short_description': 'My abstract',
        'citation': {
            'citation': '''@article {ORCIDtest2014,
                           author = "Lastname, Firstname",
                           title = "API Test Title",
                           journal = "Journal Title",
                           volume = "25",
                           number = "4",
                           year = "2010",
                           pages = "259-264",
                           doi = "doi:10.1087/20120404"
                         }''',
            # Available types:
            # 'formatted-unspecified'
            # 'bibtex'
            # 'formatted-apa'
            # 'formatted-harvard'
            # 'formatted-ieee'
            # 'formatted-mla'
            # 'formatted-vancouver'
            # 'formatted-chicago'
            'citation_type': 'bibtex'
        },
        # See http://members.orcid.org/api/supported-work-types
        'type': 'journal-article',
        'publication_date': {'year': '2010',
                             'month': '11',
                             'day': '10'
        },
        # See http://members.orcid.org/api/supported-work-identifiers
        'work_external_identifiers': [{
            'type': 'source-work-id',
            'id': '1234'
        }],
        'url': 'https://github.com/MSusik/python-orcid',
        'contributors': [{
            'name': 'LastName, FirstName',
            'orcid': '0000-0001-5109-3700',
            'email': 'somebody@mailinator.com',
            'attributes': {
                # Supported roles:
                # 'author'
                # 'assignee'
                # 'editor'
                # 'chair-or-translator'
                # 'co-investigator'
                # 'co-inventor'
                # 'graduate-student'
                # 'other-inventor'
                # 'principal-investigator'
                # 'postdoctoral-researcher'
                # 'support-staff'
                # 'Lead'
                # 'Co lead'
                # 'Supported by'
                'role': 'author',
                # One of 'additional', 'first'
                'sequence': 'additional'
            }
        }],
        # ISO-629-1: http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        'language_code': 'en',
        'country': {'code': 'US'}
    }


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
