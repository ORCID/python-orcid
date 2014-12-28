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

Use ``push_data``, to send info:

.. code-block:: python

    orcid.push_data(orcid_id, scope, token, json)

The `token` is the one that you received from OAuth 3-legged authorization.
