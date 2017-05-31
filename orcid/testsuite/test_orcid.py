"""Tests for ORCID library."""

import os
import pytest
import re
from uuid import uuid4

from orcid import MemberAPI
from orcid import PublicAPI
from requests.exceptions import HTTPError

from .helpers import exemplary_work
from .helpers import WORK_NAME2

CLIENT_KEY = os.environ['CLIENT_KEY']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
USER_PASSWORD = os.environ['USER_PASSWORD']
USER_EMAIL = os.environ['USER_EMAIL']
REDIRECT_URL = os.environ['REDIRECT_URL']
USER_ORCID = os.environ['USER_ORCID']
TOKEN_RE = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
WORK_NAME = u'WY51MF0OCMU37MVGMUX1M92G6FR1IQUW'


def fullmatch(regex, string, flags=0):
    """Emulate python-3.4 re.fullmatch()."""
    return re.match("(?:" + regex + r")\Z", string, flags=flags)


@pytest.fixture
def publicAPI():
    """Get PublicAPI handler."""
    return PublicAPI(sandbox=True,
                     institution_key=CLIENT_KEY,
                     institution_secret=CLIENT_SECRET)


def test_get_login_url(publicAPI):
    """Test constructing a login/registration URL."""
    redirect_uri = "https://www.inspirehep.net"
    expected_url = "https://sandbox.orcid.org/oauth/authorize?client_id=" + \
        CLIENT_KEY + \
        "&scope=%2Forcid-profile%2Fread-limited&response_type=code&" \
        "redirect_uri=https%3A%2F%2Fwww.inspirehep.net"
    assert publicAPI.get_login_url("/orcid-profile/read-limited",
                                   redirect_uri) == expected_url
    assert publicAPI.get_login_url(["/orcid-profile/read-limited"],
                                   redirect_uri) == expected_url
    assert publicAPI.get_login_url(2 * ["/orcid-profile/read-limited"],
                                   redirect_uri) == expected_url
    import sys
    if sys.version_info[0] == 2:
        family_names = "M\xc3\xb6\xc3\x9fbauer".decode("utf-8")
    else:
        family_names = "M\xf6\xdfbauer"
    kwargs = {"state": "F0OCMU37MV3GMUX1",
              "family_names": family_names, "given_names": "Rudolf Ludwig",
              "email": "r.moessbauer@example.com",
              "lang": "en", "show_login": True}
    assert publicAPI.get_login_url(
        ["/orcid-profile/read-limited", "/affiliations/create",
         "/orcid-works/create"], redirect_uri, **kwargs) == \
        "https://sandbox.orcid.org/oauth/authorize?client_id=" + CLIENT_KEY + \
        "&scope=%2Faffiliations%2Fcreate+%2Forcid-profile%2Fread-limited+" \
        "%2Forcid-works%2Fcreate&response_type=code&" \
        "redirect_uri=https%3A%2F%2Fwww.inspirehep.net&" \
        "state=F0OCMU37MV3GMUX1&family_names=M%C3%B6%C3%9Fbauer&" \
        "given_names=Rudolf+Ludwig&email=r.moessbauer%40example.com&" \
        "lang=en&show_login=true"


def test_read_record_public(publicAPI):
    """Test reading records."""
    token = publicAPI.get_token(USER_EMAIL,
                                USER_PASSWORD,
                                REDIRECT_URL,
                                '/read-limited')

    activities = publicAPI.read_record_public(USER_ORCID,
                                              'activities',
                                              token)
    first_work = activities['works']['group'][0]['work-summary'][0]
    assert first_work['title'][
                      'title']['value'] == WORK_NAME
    put_code = first_work['put-code']
    work = publicAPI.read_record_public(USER_ORCID, 'work', token,
                                        put_code)
    assert work['type'] == u'JOURNAL_ARTICLE'

    with pytest.raises(ValueError) as excinfo:
        publicAPI.read_record_public(USER_ORCID, 'activities', token, '1')
    assert 'argument is redundant' in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        publicAPI.read_record_public(USER_ORCID, 'work', token)
    assert "please specify the 'put_code' argument" in str(excinfo.value)


def test_search_public(publicAPI):
    """Test search_public."""

    results = publicAPI.search('text:%s' % WORK_NAME)
    assert results['result'][0]['orcid-identifier']['path'] == USER_ORCID

    results = publicAPI.search('family-name:Sanchez', start=2, rows=6)
    # Just check if the request suceeded

    assert results['num-found'] > 0


def test_search_public_generator(publicAPI):
    """Test search public with a generator."""

    results = publicAPI.search('text:%s' % WORK_NAME)
    assert results['result'][0]['orcid-identifier']['path'] == USER_ORCID

    generator = publicAPI.search_generator('family-name:Sanchez')
    result = next(generator)
    result = next(generator)
    # Just check if the request suceeded

    assert 'orcid-identifier' in result


def test_search_public_generator_no_results(publicAPI):
    generator = publicAPI.search_generator('family-name:' +
                                           str(uuid4()))

    with pytest.raises(StopIteration):
        next(generator)


def test_search_public_generator_pagination(publicAPI):
    generator = publicAPI.search_generator('family-name:Sanchez',
                                           pagination=1)
    result = next(generator)
    result = next(generator)
    # Just check if the request suceeded

    assert 'orcid-identifier' in result


@pytest.fixture
def memberAPI():
    """Get memberAPI handler."""
    return MemberAPI(CLIENT_KEY, CLIENT_SECRET,
                     sandbox=True)


def test_apis_common_functionalities(memberAPI):
    """Check if the member API has functionalities of the other apis."""
    assert hasattr(getattr(memberAPI, 'search'), '__call__')
    assert hasattr(getattr(memberAPI, 'get_token'), '__call__')


def test_search_member(memberAPI):
    """Test search_member."""
    results = memberAPI.search('text:%s' % WORK_NAME)
    assert results['result'][0]['orcid-identifier']['path'] == USER_ORCID


def test_search_member_generator(memberAPI):
    """Test search_member with generator."""
    generator = memberAPI.search_generator('text:%s' % WORK_NAME)
    results = next(generator)
    assert results['orcid-identifier']['path'] == USER_ORCID


def test_read_record_member(memberAPI):
    """Test reading records."""
    token = memberAPI.get_token(USER_EMAIL,
                                USER_PASSWORD,
                                REDIRECT_URL,
                                '/read-limited')
    activities = memberAPI.read_record_member(USER_ORCID,
                                              'activities',
                                              token)
    first_work = activities['works']['group'][0]['work-summary'][0]
    assert first_work['title'][
                      'title']['value'] == WORK_NAME
    put_code = first_work['put-code']
    work = memberAPI.read_record_member(USER_ORCID, 'work', token,
                                        put_code)
    assert work['type'] == u'JOURNAL_ARTICLE'


def test_work_simple(memberAPI):
    """Test adding, updating and removing an example of a simple work."""

    def get_added_works(token):
        activities = memberAPI.read_record_member(USER_ORCID,
                                                  'activities',
                                                  token)
        return list(filter(lambda x: x['work-summary'][
                                       0]['title']['title'][
                                       'value'] == WORK_NAME2,
                           activities['works']['group']))

    # Add
    work = exemplary_work
    token = memberAPI.get_token(USER_EMAIL,
                                USER_PASSWORD,
                                REDIRECT_URL)

    memberAPI.add_record(USER_ORCID, token, 'work', work)

    added_works = get_added_works(token)
    assert len(added_works) == 1
    assert added_works[0]['work-summary'][0]['type'] == u'JOURNAL_ARTICLE'
    put_code = added_works[0]['work-summary'][0]['put-code']

    # Update
    work['type'] = 'OTHER'

    memberAPI.update_record(USER_ORCID, token, 'work', work, put_code)

    added_works = get_added_works(token)
    assert len(added_works) == 1

    # Remove
    memberAPI.remove_record(USER_ORCID, token,
                            'work', put_code)
    added_works = get_added_works(token)
    assert len(added_works) == 0


def test_get_orcid(memberAPI):
    """Test fetching user id from authentication."""
    orcid = memberAPI.get_user_orcid(USER_EMAIL,
                                     USER_PASSWORD,
                                     REDIRECT_URL)
    assert orcid == USER_ORCID


def test_get_token(memberAPI):
    """Test getting token."""
    token = memberAPI.get_token(USER_EMAIL,
                                USER_PASSWORD,
                                REDIRECT_URL)

    assert fullmatch(TOKEN_RE, token) is not None
