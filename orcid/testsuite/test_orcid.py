"""Tests for ORCID library."""

import httpretty
import pytest
import re
import sys

from orcid import MemberAPI, PublicAPI

WORK_NAME = u'WY51MF0OCMU37MVGMUX1M92G6FR1IQUW'


@pytest.fixture
def search_result():
    """XML from the search engine."""
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
              <orcid-message xmlns="http://www.orcid.org/ns/orcid">
              <message-version>1.2</message-version>
              <orcid-search-results num-found="1">
                <orcid-search-result>
                  <relevancy-score>0.988503</relevancy-score>
                    <orcid-profile>
                      <orcid-identifier>
                        <uri>http://sandbox.orcid.org/0000-0002-3874-0894</uri>
                        <path>0000-0002-3874-0894</path>
                        <host>sandbox.orcid.org</host>
                      </orcid-identifier>
                      <orcid-bio>
                        <personal-details>
                        <given-names>inspire003</given-names>
                        <family-name>inspire</family-name>
                        </personal-details>
                      </orcid-bio>
                    </orcid-profile>
                  </orcid-search-result>
                </orcid-search-results>
              </orcid-message>
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
def publicAPI():
    """Get publicAPI handler."""
    return PublicAPI(sandbox=True)


@httpretty.activate
def test_search_public(publicAPI, search_result):
    """Test search_public."""
    SEARCH_URI = "https://pub.sandbox.orcid.org/v1.2/search" + \
        "/orcid-bio/?defType=lucene&q=(\w+)"

    httpretty.register_uri(httpretty.GET,
                           re.compile(SEARCH_URI),
                           body=search_result,
                           content_type='application/orcid+json')
    results = publicAPI.search_public('text:%s' % WORK_NAME)
    assert results['orcid-search-results']['orcid-search-result'][0][
                   'orcid-profile']['orcid-identifier'][
                   'path'] == u'0000-0002-3874-0894'

    results = publicAPI.search_public('family-name:Sanchez', start=2, rows=6)
    # Just check if the request suceeded
    assert results['error-desc'] is None


@httpretty.activate
def test_read_record_public(publicAPI, body_all, body_single_work):
    """Test reading records."""
    READ_URI = ""

    all_works_url = "https://pub.sandbox.orcid.org/v2.0_rc1" + \
        "/0000-0002-3874-0894/activities"
    single_works_url = "https://pub.sandbox.orcid.org/v2.0_rc1" + \
        "/0000-0002-3874-0894/work/477441"

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


@pytest.fixture
def memberAPI():
    """Get memberAPI handler."""
    return MemberAPI(os.environ["MEMBER_ID"], os.environ["MEMBER_TOKEN"],
                     sandbox=True)


@httpretty.activate
def test_search_member(memberAPI, search_result, token_response):
    """Test search_member."""
    SEARCH_URI = "https://api.sandbox.orcid.org/v1.2/search" + \
        "/orcid-bio/?defType=lucene&q=(\w+)"

    TOKEN_URI = "https://api.sandbox.orcid.org/oauth/token"

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
    assert results['orcid-search-results']['orcid-search-result'][0][
                   'orcid-profile']['orcid-identifier'][
                   'path'] == u'0000-0002-3874-0894'


@httpretty.activate
def test_read_record_member(memberAPI, token_response):
    """Test reading records."""
    TOKEN_URI = "https://api.sandbox.orcid.org/oauth/token"

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
    assert work['type'] == u'BOOK'


@httpretty.activate
def test_work_simple(memberAPI):
    """Test adding, updating and removing an example of a simple work."""
    title = "API Test Title " + str(sys.version_info[0]) + "." + \
        str(sys.version_info[1])

    def get_added_works():
        activities = memberAPI.read_record_member('0000-0002-3874-0894',
                                                  'activities')
        return list(filter(lambda x: x['work-summary'][
                                       0]['title']['title'][
                                       'value'] == title,
                           activities['works']['group']))

    httpretty.register_uri(httpretty.POST, "https://api.sandbox.orcid.org/activitie")

    # Add
    work = {
        'title': {'title': title},
        'type': 'journal-article'
    }
    memberAPI.add_record('0000-0002-3874-0894',
                         os.environ['USER_ACTIVITIES_TOKEN'],
                         'work', work)
    added_works = get_added_works()
    assert len(added_works) == 1
    assert added_works[0]['work-summary'][0]['type'] == u'JOURNAL_ARTICLE'
    put_code = added_works[0]['work-summary'][0]['put-code']

    # Update
    memberAPI.update_record('0000-0002-3874-0894',
                            os.environ['USER_ACTIVITIES_TOKEN'],
                            'work', put_code, {'type': 'other'})
    added_works = get_added_works()
    assert len(added_works) == 1
    assert added_works[0]['work-summary'][0]['type'] == u'OTHER'

    # Remove
    memberAPI.remove_record('0000-0002-3874-0894',
                            os.environ['USER_ACTIVITIES_TOKEN'],
                            'work', put_code)
    added_works = get_added_works()
    assert len(added_works) == 0


def test_get_orcid(memberAPI):
    """Test fetching user id from authentication."""
    orcid = memberAPI.get_user_orcid(os.environ['USER_ID'],
                                     os.environ['USER_PASSWORD'],
                                     os.environ['MEMBER_REDIRECT'])
    assert orcid == "0000-0002-3874-0894"


def test_get_token(memberAPI):
    """Test getting token."""
    token = memberAPI.get_token(os.environ['USER_ID'],
                                os.environ['USER_PASSWORD'],
                                os.environ['MEMBER_REDIRECT'])
    # The token doesn't change on the sandbox
    assert token == os.environ['USER_ACTIVITIES_TOKEN']
