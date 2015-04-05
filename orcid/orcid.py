"""Implementation of python-orcid library."""

from jinja2 import FileSystemLoader, Environment
from lxml import etree

import json
import os
import requests

# CONFIGURATION ###############################################################


class Config:
    pass

Config.SANDBOX = False

Config.ENDPOINT_PUBLIC = "http://pub.orcid.org"
Config.ENDPOINT_MEMBER = "https://api.orcid.org"

Config.MEMBER_KEY = None
Config.MEMBER_SECRET = None
Config.SANDBOX_KEY = None
Config.SANDBOX_SECRET = None
Config.KEY = None
Config.SECRET = None

VERSION = "/v2.0_rc1"


def set_endpoint(sandbox=False):
    """Set endpoint.

    Change key and secret to appropiate ones. This function is useful if you
    want to test your code using sandbox.

    Parameters
    ----------
    :param sandbox: boolean
        If true, sandbox is used. Otherwise, production endpoint is used.
    """
    Config.SANDBOX = sandbox

    if sandbox:
        Config.ENDPOINT_MEMBER = "http://api.sandbox.orcid.org"
        Config.ENDPOINT_PUBLIC = "http://pub.sandbox.orcid.org"
        Config.KEY = Config.SANDBOX_KEY
        Config.SECRET = Config.SANDBOX_SECRET
    else:
        Config.ENDPOINT_MEMBER = "https://api.orcid.org"
        Config.ENDPOINT_PUBLIC = "http://pub.orcid.org"
        Config.KEY = Config.MEMBER_KEY
        Config.SECRET = Config.MEMBER_SECRET


def set_credentials(key, secret, sandbox=False):
    """Set credentials.

    You can specify sandbox parameter if you want to set sandox credentials.

    Parameters
    ----------
    :param key: string
        The institution's key
    :param secret: string
        The institution's secret
    :param sandbox: bool
        If true, sandbox is used. Otherwise, production endpoint is used.
    """
    if sandbox:
        Config.SANDBOX_KEY = key
        Config.SANDBOX_SECRET = secret
        if Config.SANDBOX:
            Config.KEY = Config.SANDBOX_KEY
            Config.SECRET = Config.SANDBOX_SECRET
    else:
        Config.MEMBER_KEY = key
        Config.MEMBER_SECRET = secret
        if not Config.SANDBOX:
            Config.KEY = Config.MEMBER_KEY
            Config.SECRET = Config.MEMBER_SECRET

# TOKEN HELPERS ###############################################################


def _get_access_token_from_orcid(scope):
    payload = {'client_id': Config.KEY,
               'client_secret': Config.SECRET,
               'scope': scope,
               'grant_type': 'client_credentials'
               }

    request_url = "%s/oauth/token" % Config.ENDPOINT_MEMBER
    headers = {'Accept': 'application/json'}
    response = requests.post(request_url, data=payload, headers=headers)
    code = response.status_code

    res = None
    if code == requests.codes.ok:
        res = json.loads(response.content)['access_token']
    return res

# GETTING INFORMATION #########################################################


def _get_member_info(orcid_id, request_type, response_format, id):
    access_token = _get_access_token_from_orcid('/read-public')
    request_url = '%s/%s/%s' % (Config.ENDPOINT_MEMBER + VERSION,
                                orcid_id, request_type)
    if id:
        request_url += '/%s' % id
    headers = {'Accept': 'application/orcid+%s' % response_format,
               'Authorization': 'Bearer %s' % access_token}
    return requests.get(request_url, headers=headers)


def _get_public_info(orcid_id, request_type, response_format, id):

    request_url = '%s/%s/%s' % (Config.ENDPOINT_PUBLIC + VERSION,
                                orcid_id, request_type)
    if id:
        request_url += '/%s' % id
    headers = {'Accept': 'application/orcid+%s' % response_format}
    return requests.get(request_url, headers=headers)


def get_info(orcid_id, scope, request_type, response_format='json',
             id=None):
    """Get the researcher's ORCID.

    Parameters
    ----------
    :param orcid_id: string
        Id of the queried author
    :param scope: string
        'public' or 'member'
    :param request_type: string
        One of 'activities', 'education', 'employment', 'work', 'funding'
    :param response_format: one of json, xml.
    """
    if request_type != "activities" and not id:
        raise ValueError("""In order to fetch specific record, please specify
                            the 'id' argument.""")
    elif request_type == "activities" and id:
        raise ValueError("""In order to fetch activities summary, the 'id'
                            argument is redundant.""")

    if scope == "member":
        response = _get_member_info(orcid_id, request_type, response_format,
                                    id)
    elif scope == "public":
        response = _get_public_info(orcid_id, request_type, response_format,
                                    id)
    else:
        raise ValueError("""Wrong scope.""")

    code = response.status_code

    response.raise_for_status()

    if response_format == "json":
        return json.loads(response.content)
    elif response_format == "xml":
        return etree.fromstring(response.content)

# UPDATING DATA ###############################################################


def add_external_id(orcid_id, token, formatted_data, render=True):
    """Add an external id to the profile."""

    current_path = os.path.dirname(os.path.abspath(__file__))
    template_dir = '%s/templates/' % current_path
    environment = Environment(loader=FileSystemLoader(template_dir))
    template = environment.get_template("id.xml")
    xml = template.render({'records': formatted_data}) if render \
        else formatted_data

    url = "%s/%s/orcid-bio/external-identifiers" % (Config.ENDPOINT_MEMBER, orcid_id)

    headers = {'Accept': 'application/vnd.orcid+xml',
               'Content-Type': 'application/vnd.orcid+xml',
               'Authorization': 'Bearer ' + token
               }

    response = requests.post(url, xml, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError, exc:
        print exc
        print response.text


def push_data(orcid_id, scope, token, formatted_data, render=True,
              replace=False):
    """Push new works to the profile.

    The token should have a correct scope:
    If the data scope is ``works`` -> create
    If the data scope is ``works`` and you replace the data -> update

    In case of ``works`` and ``replace`` adds works.

    In case of ``works`` and ``replace == False`` replaces all the works.

    :scope: Can be one of works,affiliations,funding
    """
    url = "%s/%s/orcid-%s" % (Config.ENDPOINT_MEMBER, orcid_id, scope)

    current_path = os.path.dirname(os.path.abspath(__file__))
    template_dir = '%s/templates/' % current_path
    environment = Environment(loader=FileSystemLoader(template_dir))
    template = environment.get_template("%s.xml" % scope)
    xml = template.render({'records': formatted_data}) if render \
        else formatted_data

    headers = {'Accept': 'application/vnd.orcid+xml',
               'Content-Type': 'application/vnd.orcid+xml',
               'Authorization': 'Bearer ' + token
               }

    response = None
    if scope == "works" and not replace:
        response = requests.post(url, xml, headers=headers)
    else:
        response = requests.put(url, xml, headers=headers)

    code = response.status_code
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError, exc:
        print exc
        print response.text

# INITIALIZATION ##############################################################

set_endpoint()
