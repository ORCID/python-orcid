"""General tests for ORCID library."""

from orcid import MemberAPI, PublicAPI


def test_search_public():
    """Test search_public."""
    api = PublicAPI(sandbox=True)
    results = api.search_public('family-name:Sanchez')
    assert results != 1
