python-orcid
============

.. image:: https://img.shields.io/travis/ORCID/python-orcid.svg?style=flat-square
  :target: https://travis-ci.org/ORCID/python-orcid
.. image:: https://img.shields.io/coveralls/ORCID/python-orcid.svg?style=flat-square
  :target: https://coveralls.io/r/ORCID/python-orcid?branch=master
.. image:: https://img.shields.io/pypi/dm/orcid.svg?style=flat-square
  :target: https://pypi.python.org/pypi/orcid/
.. image:: https://img.shields.io/pypi/l/orcid.svg?style=flat-square
  :target: https://pypi.python.org/pypi/orcid/
.. image:: https://img.shields.io/badge/python-2.6%202.7%203.3%203.4-blue.svg?style=flat-square
  :target: https://pypi.python.org/pypi/orcid/
.. image:: https://img.shields.io/badge/status-alpha-red.svg?style=flat-square
  :target: https://pypi.python.org/pypi/orcid/

Authors
-------

Mateusz Susik <mateuszsusik@gmail.com>

Installation
------------

.. code-block:: bash

    pip install orcid

Notes
-----

Currently the library works fully only for the sandbox. It uses API version
2.0_rc2 wherever it's applicable. Use at your own risk for production systems.

The library will be stable when the 2.0_rc2 API is released.

If there are changes in ORCID API, the library might not work till the changes
are implemented by me in this library. Pull requests and submitting issues
are very welcome. Please read CONTRIBUTING.rst in case of suggestions.

Error handling
--------------

The methods of this library might throw client or server errors. An error is 
an exception coming from the proven
`requests <http://docs.python-requests.org/en/latest/>`_ library. The usual
way to work with them should be:

.. code-block:: python
  
    from requests import RequestException
    import orcid
    api = orcid.MemberAPI(key, secret, sandbox=True)
    try:
        api.add_record(author-orcid, token, 'work',
                       {'title': 'Title', 'type': 'artistic-performance'})
    except RequestException as e:
        # Here the error should be handled. As the exception message might be
        # too generic, additional info can be obtained by:
        print(e.response.text)
        # The response is a requests Response instance.


Introduction
------------

`ORCID <http://orcid.org/>`_ is an open, non-profit, community-based effort to
provide a registry of unique researcher identifiers and a transparent method
of linking research activities and outputs to these identifiers. ORCID is
unique in its ability to reach across disciplines, research sectors, and
national boundaries and its cooperation with other identifier systems.

ORCID offers an API (Application Programming Interface) that allows your
systems and applications to connect to the ORCID registry, including reading
from and writing to ORCID records.

There are two types of API available for developers.

SearchAPI
=========

The search API allows the developers to use the search engine provided
bo ORCiD. This is the only API that does not require any credentials.
Please note that currently it uses API 1.2 and will be migrated to 2.0
in the future. The functionality of this API is available in public
and member APIs.

Searching
---------

.. code-block:: python

    import orcid
    api = orcid.SearchAPI(sandbox=True)
    search_results = api.search_public('text:English')


While creating a search query, it is possible to use a generator in
order to reduce time needed to fetch a record.

.. code-block:: python

    search_results = api.search_public_generator('text:English',
                                                 pagination=20)
    first_result = next(search_results)

PublicAPI
=========

The public API allows the developers to use the search engine and read author
records. In order to use it, you need to pass institution's key and secret.

The functionality of this API is also available in the member API.

Token
-----

In order to read or update records, the ``token`` is needed. The tokens come
from OAuth 3-legged authorization. You can perform the authorization using
this library (examples below).

However, if the user is already connected to ORCiD and authenticated (so you
have an authorization code), this process can be simplified:

.. code-block:: python

    import orcid
    api = orcid.PublicAPI(institution_key, institution_secret, sandbox=True)
    token = api.get_token_from_authorization_code(authorization_code,
                                                  redirect_uri)

Reading records
---------------

.. code-block:: python

    import orcid
    api = orcid.PublicAPI(institution_key, institution_secret, sandbox=True)
    search_results = api.search_public('text:English')
    # Get the summary
    token = api.get_token(user_id, user_password, redirect_uri)
    summary = api.read_record_public('0000-0001-1111-1111', 'activities',
                                     token)


Every record in the `summary` dictionary should contain *put-codes*. Using
them, it is possible to query the specific record for details. Type of the
record and the put-code need to be provided.

.. code-block:: python

    # Get the specific record
    # Available record types are:
    # 'education', 'employment', 'funding', 'peer-review', 'work'
    work = api.read_record_public('0000-0001-1111-1111', 'work', token,
                                  '1111')

Additional utilities
--------------------

Python-orcid offers a function for creating a login/register URL.

.. code-block:: python

    url = api.get_login_url('/authenticate', redirect_uri, email=email)


MemberAPI
=========

The member API allows the developers to add/change/remove records.
To modify the records one needs a token which can be obtained following
the OAuth 3-legged authorization process.

The member API lets the developer obtain more information when using the
search API or fetching the records.

To create an instance of the member API handler, the institution key and the
institution secret have to be provided.

.. code-block:: python

    import orcid
    api = orcid.MemberAPI(institution_key, institution_secret,
                          sandbox=True)
    search_results = api.search_member('text:English')
    # Get the summary
    token = api.get_token(user_id, user_password, redirect_uri,
                          '/read-limited')
    summary = api.read_record_member('0000-0001-1111-1111', 'activities',
                                     token)

All the methods from the public API are available in the member API.

Getting ORCID
-------------

If the ORCID of an author is not known, one can obtain it by authorizing the
user:

.. code-block:: python

    orcid = api.get_user_orcid(user_id, password, redirect_uri)


Adding/updating/removing records
--------------------------------

Using the member API, one can add/update/remove records from the ORCID profile.

.. code-block:: python

    put_code = api.add_record(author-orcid, token, 'work',
                              {'title': {'title': 'Title'},
                               'type': 'ARTISTIC_PERFORMANCE'})

    # Change the type to 'other'
    api.update_record(author-orcid, token, 'work', put-code,
                      {'type': 'OTHER'})
    api.remove_record(author-orcid, token, 'work', put-code)


The ``token`` is the string received from OAuth 3-legged authorization.

``work`` is one of the types of records. Every time a record is modified, the type
has to be specified. The available types are:

* activities
* education
* employment
* funding
* peer-review
* work

The last argument is the record itself. Here are some
examplary dictionaries that can be passed as an argument:

work
~~~~

In case of doubts, see `work XML <http://members.orcid.org/api/xml-orcid-works>`_.

A minimal example, only the mandatory fields are filled.

.. code-block:: python

    {
        'title': {'title': 'API Test Title'},
        'type': 'JOURNAL_ARTICLE',
        'external-ids': [{
            'external-id': [{
                'external-id-type': 'source-work-id',
                'external-id-value': '1234'
            }]
        }]
    }

An example where all the fields are filled.

.. code-block:: python

    {
        'title': {'title': 'API Test Title',
                  'subtitle': 'My Subtitle',
                  'translated-title':
                        {'language-code': 'pl',
                         'value': u'API Tytuł testowy'}
                 },
        'journal-title': 'Journal Title',
        'short-description': 'My abstract',
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
            # 'FORMATTED-UNSPECIFIED'
            # 'BIBTEX'
            # 'FORMATTED_APA'
            # 'FORMATTED_HARVARD'
            # 'FORMATTED_IEEE'
            # 'FORMATTED_MLA'
            # 'FORMATTED_VANCOUVER'
            # 'FORMATTED_CHICAGO'
            'citation-type': 'BIBTEX'
        },
        # See http://members.orcid.org/api/supported-work-types
        'type': 'JOURNAL_ARTICLE',
        'publication-date': {'year': '2010',
                             'month': '11',
                             'day': '10'
        },
        # See http://members.orcid.org/api/supported-work-identifiers
        'external-ids': { 'external-id':[{
            'external-id-type': 'source-work-id',
            'external-id-value': '1234',
            'external-id-url': 'www.example.com/12344'
        }]},
        'url': 'https://github.com/MSusik/python-orcid',
        'contributors': {'contributor': [{
            'credit-name': 'LastName, FirstName',
            'contributor-orcid': '0000-0001-5109-3700',
            'contributor-email': 'somebody@mailinator.com',
            'contributor-attributes': {
                # Supported roles:
                # 'AUTHOR'
                # 'ASSIGNEE'
                # 'EDITOR'
                # 'CHAIR_OR_TRANSLATOR'
                # 'CO_INVESTIGATOR'
                # 'CO_INVENTOR'
                # 'GRADUATE_STUDENT'
                # 'OTHER_INVENTOR'
                # 'PRINCIPAL_INVESTIGATOR'
                # 'POSTDOCTORAL_RESEARCHER'
                # 'SUPPORT_STAFF'
                'contributor-role': 'SUPPORT_STAFF',
                # One of 'ADDITIONAL', 'FIRST'
                'contributor-sequence': 'ADDITIONAL'
            }
        }]},
        # ISO-629-1: http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        'language-code': 'en',
        'country': {'value': 'US', 'visibility': 'PUBLIC'}
    }


education or employment
~~~~~~~~~~~~~~~~~~~~~~~

In case of doubts, see `affiliation XML <http://members.orcid.org/api/xml-affiliations>`_.

A minimal example using only the required fields.

.. code-block:: python

    {
        'organization': {
            'name': 'My college',
            'address': {
                'city': 'Some city',
                'country': 'US'
            }
        }
    }

An example with all the fields used.

.. code-block:: python

    {
        'department-name': 'Department',
        'role-title': 'Researcher (Academic)',
        'start-date': {'year': 2012,
                       'month': 4,
                       'day': 10
        },
        'end-date': {'year': 2013,
                     'month': 4,
                     'day': 10
        },
        'organization': {
            'address': {
                'city': 'Some City',
                'region': 'NY',
                'country': 'US'
            },
            'disambiguated-organization': {
                'disambiguated-organization-identifier': 'XXXXXX',
                # Only RINGGOLD is available so far.
                'disambiguation-source': 'RINGGOLD'
            },
            'name': 'My college'
        }
    }



funding
~~~~~~~

In case of doubts, see `funding XML <http://members.orcid.org/api/xml-funding>`_.

A minimal example using only the required fields.

.. code-block:: python

    {
        # One of 'AWARD', 'CONTRACT', 'GRANT', 'SALARY_AWARD'
        'type': 'AWARD',
        'title': {
            'title': 'Title of the Funding',
        },
        'organization': {
            'address': {
                'city': 'London',
                'country': 'GB'
            },
            'name': 'Funding Agency Name'
        },
        'external-ids': {'external-id': [{
           'external-id-type': 'grant_number',
           'external-id-value': '1234',
           'external-id-url': 'www.funding.com/1234'
        }]},
    }

An example with all the fields used.

.. code-block:: python

    {
        'type': 'AWARD',
        'title': {
            'title': 'Title of the Funding',
            'translated-title': {
                'value': u'Tytuł Finansowania',
                'language-code': 'pl'
            }
        },
        'short-description': 'Description of the funding',
        'amount': {'currency-code': 'USD',
                   'value': 1000},
        'url': 'www.orcid.org',
        'start-date': {'year': 2013,
                       'month': 1,
                       'day': 10
                       },
        'end-date': {'year': 2014,
                     'month': 1,
                     'day': 10
                     },
        'external-ids': {'external-id': [{
           'external-id-type': 'grant_number',
           'external-id-value': '1234',
           'external-id-url': 'www.funding.com/1234'
         }]},
        'contributors': {'contributor': [{
            'contributor-orcid': '0000-0003-4494-0734',
            'credit-name': {
                'value': 'Smith, John.',
                'visibility': 'PUBLIC'
            },
            'contributor-email': 'john@mailinator.com',
            'contributor-attributes': {
                # One of 'LEAD', 'CO_LEAD', 'SUPPORTED_BY', 'OTHER_CONTRIBUTION'
                'contributor-role': 'LEAD',
            }
        }]},
        'organization': {
            'address': {
                'city': 'London',
                'region': 'London',
                'country': 'GB'
            },
            'disambiguated-organization': {
                'disambiguated-organization-identifier': 'XXXXXX',
                # Only FUNDREF is available so far.
                'disambiguation-source': 'FUNDREF'
            },
            'name': 'Funding Agency Name'
        }
    }

peer-review
~~~~~~~~~~~

TBA
