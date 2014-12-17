"""Initialization file for python-orcid."""

from .orcid import get_id, get_info, push_data
from .orcid import set_credentials, set_endpoint

__all__ = ('get_id', 'get_info', 'push_data',
           'set_credentials', 'set_endpoint')
