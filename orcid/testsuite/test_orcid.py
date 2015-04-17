"""Tests for ORCID library."""

import os
import pytest

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
