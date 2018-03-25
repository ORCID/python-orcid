python-orcid
============

.. image:: https://badges.gitter.im/ORCID/python-orcid.svg
   :alt: Join the chat at https://gitter.im/ORCID/python-orcid
   :target: https://gitter.im/ORCID/python-orcid?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://img.shields.io/travis/ORCID/python-orcid.svg?style=flat-square
  :target: https://travis-ci.org/ORCID/python-orcid
.. image:: https://img.shields.io/coveralls/ORCID/python-orcid.svg?style=flat-square
  :target: https://coveralls.io/r/ORCID/python-orcid?branch=master
.. image:: https://img.shields.io/pypi/dm/orcid.svg?style=flat-square
  :target: https://pypi.python.org/pypi/orcid/
.. image:: https://img.shields.io/pypi/l/orcid.svg?style=flat-square
  :target: https://pypi.python.org/pypi/orcid/
.. image:: https://img.shields.io/badge/status-beta-red.svg?style=flat-square
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

A special case are the tokens for performing search queries. Such queries
do not need user authentication, only institution credentials are needed.

.. code-block:: python

    import orcid
    api = orcid.PublicAPI(institution_key, institution_secret, sandbox=True)
    search_token = api.get_search_token_from_orcid()

By reusing the same token, the search functions will run faster skipping
the authentication process.


Searching
---------

.. code-block:: python

    import orcid
    api = orcid.PublicAPI(institution_key, institution_secret, sandbox=True)
    search_results = api.search('text:English', access_token=Token)


While creating a search query, it is possible to use a generator in
order to reduce time needed to fetch a record.

.. code-block:: python

    search_results = api.search_generator('text:English',
                                          pagination=20)
    first_result = next(search_results)


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
    summary = api.read_record_public('0000-0001-1111-1111', 'record',
                                     token)


Every record in the `summary` dictionary should contain *put-codes*. Using
them, it is possible to query the specific record for details. Type of the
record and the put-code need to be provided.

.. code-block:: python

    # Get the specific record
    work = api.read_record_public('0000-0001-1111-1111', 'work', token,
                                  '1111')

An exception is made for ``works`` `request_type`. It is possible to
fetch multiple selected works at once by selecting multiple
``put_codes`` in a list.

.. code-block:: python

    work = api.read_record_public('0000-0001-1111-1111', 'works', token,
                                  ['1111', '2222', '3333'])

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
    search_results = api.search('text:English')
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

All the types of records are supported.

.. code-block:: python

    put_code = api.add_record(author-orcid, token, 'work', json)
    # Change the type to 'other'
    api.update_record(author-orcid, token, 'work', put-code,
                      {'type': 'OTHER'})
    api.remove_record(author-orcid, token, 'work', put-code)


The ``token`` is the string received from OAuth 3-legged authorization.

The last argument is the record itself. The record should
follow ORCID's JSON records definitions. Here is an
example of a dictionary that can be passed as an argument:

.. code-block:: python

    {
      "title": {
        "title": {
          "value": "Work # 1"
        },
        "subtitle": null,
        "translated-title": null
      },
      "journal-title": {
        "value": "journal # 1"
      },
      "short-description": null,
      "type": "JOURNAL_ARTICLE",
      "external-ids": {
        "external-id": [{
          "external-id-type": "doi",
          "external-id-value": "ext-id-1",
          "external-id-url": {
            "value": "http://dx.doi.org/ext-id-1"
          },
          "external-id-relationship": "SELF"
        }]
      }
    }

If you do not know how to structure your JSON, visit
`ORCID swagger <https://api.orcid.org/v2.0>`_

It is possible to update many works in the same time!
Us ``works`` request type and pass a JSON like this one:

.. code-block:: python

  "bulk": [
  {
    "work": {
      "title": {
        "title": {
          "value": "Work # 1"
        },
      },
      "journal-title": {
        "value": "journal # 1"
      },
      "type": "JOURNAL_ARTICLE",
      "external-ids": {
        "external-id": [{
          "external-id-type": "doi",
          "external-id-value": "ext-id-1",
          "external-id-url": {
            "value": "http://dx.doi.org/ext-id-1"
          },
          "external-id-relationship": "SELF"
        }]
      }
    }
  },
  {
    "work": {
      "title": {
        "title": {
          "value": "Work # 2"
        },
      },
      "journal-title": {
        "value": "journal # 2"
      },
      "type": "JOURNAL_ARTICLE",
      "external-ids": {
        "external-id": [{
          "external-id-type": "doi",
          "external-id-value": "ext-id-2",
          "external-id-url": {
            "value": "http://dx.doi.org/ext-id-2"
          },
          "external-id-relationship": "SELF"
        }]
      }
    }
  }
  ]
