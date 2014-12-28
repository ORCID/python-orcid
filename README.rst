python-orcid
============

Current state
-------------
Under development, doesn't work yet.

Authors
-------

Mateusz Susik <mateuszsusik@gmail.com>

Notes
-----
Many limitations put on this library are caused by limitations in ORCID API.
The library won't provide back compability if ORCID API won't provide it either.
If there are changes in ORCID API, the library might not work till the changes
will be implemented in this library. Pull requests and submitting issues are
very welcome.

Usage
=====

Installation
------------

TODO, will be released on PyPI.

Configuration
-------------

There are two modes: ``sandbox`` and ``production``. TODO

Getting information
-------------------

Currently works only on production mode.

To get info about a researcher, you need to know his ORCID. Then, using this
library you can do:

.. code-block:: python

    import orcid
    orcid.get_info(orcid_id, scope, request_type)


``scope`` can be one of: ``public`` or ``member``. To use ``member`` scope, you
need to provide valid values in the configuration. If you are using ``member``
scope, the library takes care of authenticating you in ORCID using the values
from the configuration provided by you. So far, it is not possible to
use any of the scopes in the ``sandbox`` mode.

``request_type`` can be one of ``orcid-bio``, ``orcid-profile``,
``orcid-works``.

Every time you fetch the data, you can specify response format. Allowed values
are: ``json`` and ``xml``.

In case of ``json``, the library returns a result of ``json.loads``.
In case of ``xml``, the library returns a result of ``etree.fromstring``.

.. code-block:: python

    orcid.get_info(orcid_id, `member`, 'orcid-bio', response_format='json')

There is also ``get_id`` function, which is equivalent to ``get_info`` with
``request_type`` set as ``orcid-bio``.

Sending information
-------------------

TODO: add possibility of sending XML directly

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

Use ``push_data``, to send info:

.. code-block:: python

    orcid.push_data(orcid_id, scope, token, list_with_data)

or

.. code-block:: python

    orcid.push_data(orcid_id, scope, token, xml, no_render='true')

if you have already prepared the ORCID XML.

The `token` is the one that you received from OAuth 3-legged authorization.

The scope can be one of `orcid-works`, `orcid-affiliations`, `orcid-funding`.
These scopes allow to send different types of information to ORCID. If you
don't have the ORCID XML prepared, you should read detailed info below. It
describes the structure of the list that the `push_data` function should
be provided with.

Note that the majority of fields and subfields can be skipped.

When in doubt, please refer to ORCID documetation:
`ORCID XML <http://support.orcid.org/knowledgebase/topics/32832-orcid-xml>`_

orcid-works
-----------

`orcid-works` can be used when there is a need to add or update researcher's
works. It should a list of dictionaries. Each dictionary describes a single
work. Each dictionary can contain following fields:

.. code-block:: python

    [{
    ...
        'work_title': {'title': 'The best sorting algorithm',
                       'subtitle': 'Better even than quicksort'
                       'translated_titles': [
                                             ('fr', 'Le meilleur algorithme de tri'),
                                             ('pl', 'Najlepszy algorytm sortujący')
                                            ]
                       } 
    ...
    }]

Should contain the title of the work. It is a mandatory field.

.. code-block:: python
    
    [{
    ...
    ...
    }]

[{
...
...
}]