"""Tests for ORCID library."""

import json
import pytest
import re
import sys

from orcid import MemberAPI, PublicAPI
from .helpers import import_httpretty
from .helpers import body_all, body_none, body_single_work
from .helpers import authorization_code, search_result
from .helpers import token_json, token_response

WORK_NAME = u'WY51MF0OCMU37MVGMUX1M92G6FR1IQUW'


httpretty = import_httpretty()


@pytest.fixture
def publicAPI():
    """Get publicAPI handler."""
    return PublicAPI(sandbox=True)


@httpretty.activate
def test_search_public(publicAPI, search_result):
    """Test search_public."""
    search_url = "https\:\/\/pub\.sandbox\.orcid\.org\/v1\.2\/search\/" + \
        "orcid-bio\/\?defType\=lucene&q\=.+"

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

    assert results['error-desc'] is None


@httpretty.activate
def test_read_record_public(publicAPI, body_all, body_single_work):
    """Test reading records."""
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
    return MemberAPI("id", "token",
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
def test_read_record_member(memberAPI, token_response, body_all,
                            body_single_work):
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
def test_work_simple(memberAPI, token_response, body_none, body_all):
    """Test adding, updating and removing an example of a simple work."""

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


@httpretty.activate
def test_get_orcid(memberAPI, authorization_code, token_json):
    """Test fetching user id from authentication."""
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


@httpretty.activate
def test_get_token(memberAPI, authorization_code, token_json):
    """Test getting token."""
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
