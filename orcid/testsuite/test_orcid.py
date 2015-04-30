"""Tests for ORCID library."""

import json
import pytest
import re
import sys

from orcid import MemberAPI, PublicAPI

WORK_NAME = u'WY51MF0OCMU37MVGMUX1M92G6FR1IQUW'


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

httpretty = import_httpretty()


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


@pytest.fixture
def publicAPI():
    """Get publicAPI handler."""
    return PublicAPI(sandbox=True)


def test_search_public(publicAPI, search_result):
    """Test search_public."""
    search_url = "https\:\/\/pub\.sandbox\.orcid\.org\/v1\.2\/search\/" + \
        "orcid-bio\/\?defType\=lucene&q\=.+"

    httpretty.enable()
    httpretty.register_uri(httpretty.GET,
                           re.compile(search_url),
                           body=search_result,
                           content_type='application/orcid+json',
                           match_querystring=True)
    results = publicAPI.search_public('text:%s' % WORK_NAME)
    assert results['orcid-search-results']['orcid-search-result'][0][
                   'orcid-profile']['orcid-identifier'][
                   'path'] == u'0000-0002-3874-0894'

    results = publicAPI.search_public('family-name:Sanchez', start=2, rows=6)
    # Just check if the request suceeded

    httpretty.disable()
    assert results['error-desc'] is None


def test_read_record_public(publicAPI, body_all, body_single_work):
    """Test reading records."""
    all_works_url = "https://pub.sandbox.orcid.org/v2.0_rc1" + \
        "/0000-0002-3874-0894/activities"
    single_works_url = "https://pub.sandbox.orcid.org/v2.0_rc1" + \
        "/0000-0002-3874-0894/work/477441"

    httpretty.enable()
    httpretty.register_uri(httpretty.GET,
                           all_works_url,
                           body=body_all,
                           content_type='application/orcid+json')

    httpretty.register_uri(httpretty.GET,
                           single_works_url,
                           body=body_single_work,
                           content_type='application/orcid+json')

    activities = publicAPI.read_record_public('0000-0002-3874-0894',
                                              'activities')
    first_work = activities['works']['group'][0]['work-summary'][0]
    assert first_work['title'][
                      'title']['value'] == WORK_NAME
    put_code = first_work['put-code']
    work = publicAPI.read_record_public('0000-0002-3874-0894', 'work',
                                        put_code)
    assert work['type'] == u'BOOK'

    with pytest.raises(ValueError) as excinfo:
        publicAPI.read_record_public('0000-0002-3874-0894', 'activities', '1')
    assert 'argument is redundant' in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        publicAPI.read_record_public('0000-0002-3874-0894', 'work')
    assert "please specify the 'put_code' argument" in str(excinfo.value)

    httpretty.disable()


@pytest.fixture
def memberAPI():
    """Get memberAPI handler."""
    return MemberAPI("id", "token",
                     sandbox=True)


def test_search_member(memberAPI, search_result, token_response):
    """Test search_member."""
    SEARCH_URI = "https://api.sandbox.orcid.org/v1.2/search" + \
        "/orcid-bio/?defType=lucene&q=(\w+)"

    TOKEN_URI = "https://api.sandbox.orcid.org/oauth/token"

    httpretty.enable()
    httpretty.register_uri(httpretty.POST, TOKEN_URI,
                           body=token_response,
                           content_type="application/json")

    httpretty.register_uri(httpretty.GET, SEARCH_URI,
                           body=search_result,
                           content_type='application/orcid+json',
                           adding_headers={
                               "Authorization": "Bearer token"
                           })
    results = memberAPI.search_member('text:%s' % WORK_NAME)
    httpretty.disable()
    assert results['orcid-search-results']['orcid-search-result'][0][
                   'orcid-profile']['orcid-identifier'][
                   'path'] == u'0000-0002-3874-0894'


def test_read_record_member(memberAPI, token_response, body_all,
                            body_single_work):
    """Test reading records."""
    TOKEN_URI = "https://api.sandbox.orcid.org/oauth/token"
    httpretty.enable()
    httpretty.register_uri(httpretty.POST, TOKEN_URI,
                           body=token_response,
                           content_type="application/json")

    all_works_url = "https://api.sandbox.orcid.org/v2.0_rc1" + \
        "/0000-0002-3874-0894/activities"
    single_works_url = "https://api.sandbox.orcid.org/v2.0_rc1" + \
        "/0000-0002-3874-0894/work/477441"

    httpretty.register_uri(httpretty.GET,
                           all_works_url,
                           body=body_all,
                           content_type='application/orcid+json',
                           adding_headers={
                               "Authorization": "Bearer token"
                           })

    httpretty.register_uri(httpretty.GET,
                           single_works_url,
                           body=body_single_work,
                           content_type='application/orcid+json',
                           adding_headers={
                               "Authorization": "Bearer token"
                           })

    activities = memberAPI.read_record_member('0000-0002-3874-0894',
                                              'activities')
    first_work = activities['works']['group'][0]['work-summary'][0]
    assert first_work['title'][
                      'title']['value'] == WORK_NAME
    put_code = first_work['put-code']
    work = memberAPI.read_record_member('0000-0002-3874-0894', 'work',
                                        put_code)
    httpretty.disable()
    assert work['type'] == u'BOOK'


def test_work_simple(memberAPI, token_response, body_none, body_all):
    """Test adding, updating and removing an example of a simple work."""
    httpretty.enable()

    TOKEN_URI = "https://api.sandbox.orcid.org/oauth/token"
    httpretty.register_uri(httpretty.POST, TOKEN_URI,
                           body=token_response,
                           content_type="application/json")

    title = WORK_NAME

    def get_added_works():
        activities = memberAPI.read_record_member('0000-0002-3874-0894',
                                                  'activities')
        return list(filter(lambda x: x['work-summary'][
                                       0]['title']['title'][
                                       'value'] == title,
                           activities['works']['group']))

    workurl = "https://api.sandbox.orcid.org/v2.0_rc1/0000-0002-3874-0894/work"
    all_works_url = "https://api.sandbox.orcid.org/v2.0_rc1" + \
        "/0000-0002-3874-0894/activities"
    httpretty.register_uri(httpretty.POST, workurl)
    specific_workurl = "https://api.sandbox.orcid.org/v2.0_rc1/" + \
        "0000-0002-3874-0894/work/477441"
    httpretty.register_uri(httpretty.PUT, specific_workurl)
    httpretty.register_uri(httpretty.DELETE, specific_workurl)

    # Add
    work = {
        'title': {'title': title},
        'type': 'journal-article'
    }
    memberAPI.add_record('0000-0002-3874-0894', 'token', 'work', work)

    httpretty.register_uri(httpretty.GET, all_works_url,
                           body=str(body_all),
                           content_type="application/orcid+json")

    added_works = get_added_works()
    assert len(added_works) == 1
    assert added_works[0]['work-summary'][0]['type'] == u'BOOK'
    put_code = added_works[0]['work-summary'][0]['put-code']

    # Update
    memberAPI.update_record('0000-0002-3874-0894', 'token', 'work', put_code,
                            {'type': 'other'})

    body_all_json = json.loads(body_all)
    body_all_json['works']['group'][0]['work-summary'][0]['type'] = 'OTHER'
    body_all = json.dumps(body_all_json)
    httpretty.register_uri(httpretty.GET, all_works_url,
                           body=body_all,
                           content_type="application/orcid+json")
    added_works = get_added_works()
    assert len(added_works) == 1
    assert added_works[0]['work-summary'][0]['type'] == u'OTHER'

    # Remove
    memberAPI.remove_record('0000-0002-3874-0894', 'token',
                            'work', put_code)
    httpretty.register_uri(httpretty.GET, all_works_url,
                           body=body_none,
                           content_type="application/orcid+json")
    added_works = get_added_works()
    assert len(added_works) == 0
    httpretty.disable()


def test_get_orcid(memberAPI, authorization_code, token_json):
    """Test fetching user id from authentication."""
    httpretty.enable()
    authresp = '{"success": true, "url": "https://sandbox.orcid.org/my-orcid"}'
    httpretty.register_uri(httpretty.POST, memberAPI._auth_url,
                           body=authresp)
    weburl = "https://sandbox.orcid.org/oauth/authorize?client_id=" + \
        "id&response_type=code&scope=/activities/" + \
        "update&redirect_uri=redirect"
    httpretty.register_uri(httpretty.GET, weburl, body="")
    httpretty.register_uri(httpretty.POST, memberAPI._authorize_url,
                           body=authorization_code)
    httpretty.register_uri(httpretty.POST, memberAPI._token_url,
                           body=token_json)
    orcid = memberAPI.get_user_orcid("id",
                                     "password",
                                     "redirect")
    assert orcid == "0000-0002-3874-0894"
    httpretty.disable()


def test_get_token(memberAPI, authorization_code, token_json):
    """Test getting token."""
    httpretty.enable()
    authresp = '{"success": true, "url": "https://sandbox.orcid.org/my-orcid"}'
    httpretty.register_uri(httpretty.POST, memberAPI._auth_url,
                           body=authresp)
    weburl = "https://sandbox.orcid.org/oauth/authorize?client_id=" + \
        "id&response_type=code&scope=/activities/" + \
        "update&redirect_uri=redirect"

    httpretty.register_uri(httpretty.GET, weburl, body="")
    httpretty.register_uri(httpretty.POST, memberAPI._authorize_url,
                           body=authorization_code)
    httpretty.register_uri(httpretty.POST, memberAPI._token_url,
                           body=token_json)
    token = memberAPI.get_token("id",
                                "password",
                                "redirect")
    # The token doesn't change on the sandbox
    assert token == "token"
    httpretty.disable()
