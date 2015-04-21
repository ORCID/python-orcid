"""Tests for ORCID library."""

import os
import pytest
import sys

from orcid import MemberAPI, PublicAPI

WORK_NAME = u'WY51MF0OCMU37MVGMUX1M92G6FR1IQUW'


@pytest.fixture
def publicAPI():
    """Get publicAPI handler."""
    return PublicAPI(sandbox=True)


def test_search_public(publicAPI):
    """Test search_public."""
    results = publicAPI.search_public('text:%s' % WORK_NAME)
    assert results['orcid-search-results']['orcid-search-result'][0][
                   'orcid-profile']['orcid-identifier'][
                   'path'] == u'0000-0002-3874-0894'

    results = publicAPI.search_public('family-name:Sanchez', start=2, rows=6)
    # Just check if the request suceeded
    assert results['error-desc'] is None


def test_read_record_public(publicAPI):
    """Test reading records."""
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
    assert "please specify the 'id' argument" in str(excinfo.value)


@pytest.fixture
def memberAPI():
    """Get memberAPI handler."""
    return MemberAPI(os.environ["MEMBER_ID"], os.environ["MEMBER_TOKEN"],
                     sandbox=True)


def test_search_member(memberAPI):
    """Test search_member."""
    results = memberAPI.search_member('text:%s' % WORK_NAME)
    assert results['orcid-search-results']['orcid-search-result'][0][
                   'orcid-profile']['orcid-identifier'][
                   'path'] == u'0000-0002-3874-0894'


def test_read_record_member(memberAPI):
    """Test reading records."""
    activities = memberAPI.read_record_member('0000-0002-3874-0894',
                                              'activities')
    first_work = activities['works']['group'][0]['work-summary'][0]
    assert first_work['title'][
                      'title']['value'] == WORK_NAME
    put_code = first_work['put-code']
    work = memberAPI.read_record_member('0000-0002-3874-0894', 'work',
                                        put_code)
    assert work['type'] == u'BOOK'


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
