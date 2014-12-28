python-orcid
============

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

There are two modes: `sandbox` and `production`. TODO

Getting information
-------------------

Currently works only on production mode.

To get info about a researcher, you need to know his ORCID. Then, using this
library you can do:

``` python
import orcid
orcid.get_info(orcid_id, scope, request_type)
```

`scope` can be one of: `public` or `member`. To use `member` scope, you need to
provide valid values in configuration. So far, it is not possible to use them
in `sandbox` mode.

`request_type` can be one of `orcid-bio`, `orcid-profile`, `orcid-works`.

Every time you fetch the data, you can specify response format. Allowed values
are: `json` and `xml`.

In case of 'json', the library returns a result of `json.loads`.
In case of 'xml', the library returns a result of `etree.fromstring`.

``` python
orcid.get_info(orcid_id, `member`, 'orcid-bio', response_format='json')
```
There is also `get_id` function, which is equivalent to `get_info` with
`request_type` set as `orcid-bio`.

Sending information
-------------------
