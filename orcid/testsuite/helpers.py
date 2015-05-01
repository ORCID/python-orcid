"""Helper functions and response bodies for tests."""

import pytest


def import_httpretty():
    """Import HTTPretty and monkey patch Python 3.4 issue.

    See https://github.com/gabrielfalcao/HTTPretty/pull/193 and
    as well as https://github.com/gabrielfalcao/HTTPretty/issues/221.
    """
    import sys
    PY34 = sys.version_info[0] == 3 and sys.version_info[1] == 4
    if not PY34:
        import httpretty
    else:
        import functools
        import socket
        old_SocketType = socket.SocketType

        import httpretty
        from httpretty import core

        def sockettype_patch(f):
            @functools.wraps(f)
            def inner(*args, **kwargs):
                f(*args, **kwargs)
                socket.SocketType = old_SocketType
                socket.__dict__['SocketType'] = old_SocketType
            return inner

        core.httpretty.disable = sockettype_patch(
            httpretty.httpretty.disable
        )
    return httpretty


@pytest.fixture
def search_result():
    """XML from the search engine."""
    return '''
    {
      "message-version" : "",
      "orcid-profile" : null,
      "orcid-search-results" : {
        "orcid-search-result" : [ {
          "relevancy-score" : {
            "value" : 0.98850805
          },
          "orcid-profile" : {
            "orcid" : null,
            "orcid-id" : null,
            "orcid-identifier" : {
              "value" : null,
              "uri" : "http://sandbox.orcid.org/0000-0002-3874-0894",
              "path" : "0000-0002-3874-0894",
              "host" : "sandbox.orcid.org"
            },
            "orcid-deprecated" : null,
            "orcid-preferences" : null,
            "orcid-history" : null,
            "orcid-bio" : {
              "personal-details" : {
                "given-names" : {
                  "value" : "inspire003"
                },
                "family-name" : {
                  "value" : "inspire"
                },
                "credit-name" : null,
                "other-names" : null
              },
              "biography" : null,
              "researcher-urls" : null,
              "contact-details" : null,
              "keywords" : null,
              "external-identifiers" : null,
              "delegation" : null,
              "applications" : null,
              "scope" : null
            },
            "orcid-activities" : null,
            "orcid-internal" : null,
            "type" : null,
            "group-type" : null,
            "client-type" : null
          }
        } ],
        "num-found" : 1
      },
      "error-desc" : null
    }
    '''


@pytest.fixture
def body_all():
    """JSON describing the whole profile activity."""
    return """
        {
          "educations" : null,
          "employments" : null,
          "fundings" : {
            "group" : [ ]
          },
          "peer-reviews" : {
            "group" : null
          },
          "works" : {
            "group" : [ {
              "identifiers" : null,
              "work-summary" : [ {
                "put-code" : "477441",
                "created-date" : null,
                "last-modified-date" : null,
                "source" : {
                  "source-orcid" : {
                    "uri" : "http://sandbox.orcid.org/0000-0002-3874-0894",
                    "path" : "0000-0002-3874-0894",
                    "host" : "sandbox.orcid.org"
                  },
                  "source-client-id" : null,
                  "source-name" : {
                    "value" : "inspire003 inspire"
                  }
                },
                "title" : {
                  "title" : {
                    "value" : "WY51MF0OCMU37MVGMUX1M92G6FR1IQUW"
                  },
                  "subtitle" : null,
                  "translated-title" : null
                },
                "external-identifiers" : {
                  "work-external-identifier" : [ {
                    "external-identifier-type" : null,
                    "external-identifier-id" : null
                  } ]
                },
                "type" : "BOOK",
                "publication-date" : null,
                "visibility" : "PUBLIC",
                "path" : "/0000-0002-3874-0894/work/477441",
                "display-index" : "0"
              } ]
            } ]
          }
        }
    """


@pytest.fixture
def body_none():
    """JSON describing the whole profile activity."""
    return """
        {
          "educations" : null,
          "employments" : null,
          "fundings" : {
            "group" : [ ]
          },
          "peer-reviews" : {
            "group" : null
          },
          "works" : {
            "group" : [ ]
          }
        }
    """


@pytest.fixture
def body_single_work():
    """JSON describing single work."""
    return """
        {
          "put-code" : "477441",
          "path" : "/0000-0002-3874-0894/work/477441",
          "source" : {
            "source-orcid" : {
              "uri" : "http://sandbox.orcid.org/0000-0002-3874-0894",
              "path" : "0000-0002-3874-0894",
              "host" : "sandbox.orcid.org"
            },
            "source-client-id" : null,
            "source-name" : {
              "value" : "inspire003 inspire"
            }
          },
          "createdDate" : null,
          "lastModifiedDate" : null,
          "title" : {
            "title" : {
              "value" : "WY51MF0OCMU37MVGMUX1M92G6FR1IQUW"
            },
            "subtitle" : null,
            "translated-title" : null
          },
          "journal-title" : null,
          "short-description" : null,
          "citation" : {
            "citation-type" : "FORMATTED_UNSPECIFIED",
            "citation" : null
          },
          "type" : "BOOK",
          "publication-date" : null,
          "external-identifiers" : {
            "work-external-identifier" : [ {
              "external-identifier-type" : null,
              "external-identifier-id" : null
            } ]
          },
          "url" : null,
          "contributors" : {
            "contributor" : [ ]
          },
          "language-code" : null,
          "country" : null,
          "visibility" : "PUBLIC"
        }
    """


@pytest.fixture
def token_response():
    """JSON with a token."""
    return """
        {
         "access_token":"token",
         "token_type":"bearer",
         "expires_in":631138518,
         "scope":"all of them :)",
         "orcid":null
        }
    """


@pytest.fixture
def authorization_code():
    """JSON with authorization code."""
    return """
        {"errors":[],
         "userName":null,
         "password":null,
         "clientId":{"errors":[],
                     "value":"0000-0002-0970-6486",
                     "required":true,
                     "getRequiredMessage":null},
         "redirectUri":{"errors":[],
                        "value":"https://www.inspirehep.net?code=4zDk4L",
                        "required":true,
                        "getRequiredMessage":null},
         "scope":{"errors":[],
                  "value":"/activities/update",
                  "required":true,
                  "getRequiredMessage":null},
         "responseType":{"errors":[],
                         "value":"code",
                         "required":true,
                         "getRequiredMessage":null},
         "approved":true,
         "persistentTokenEnabled":true}
    """


@pytest.fixture
def token_json():
    """JSON with token included."""
    return """
        {"access_token":"token",
         "token_type":"bearer",
         "expires_in":631138518,
         "scope":"/activities/update",
         "orcid":"0000-0002-3874-0894",
         "name":"inspire003 inspire"}
    """
