"""Implementation of python-orcid library."""

from jinja2 import FileSystemLoader, Environment
from lxml import etree

import json
import os
import requests

VERSION = "/v2.0_rc1"


class PublicAPI:

    """Public API."""

    def __init__(self, sandbox=False):
        """Initialize public API.

        Parameters
        ----------
        :param sandbox: boolean
            Should the sandbox be used. False (default) indicates production
            mode.
        """
        if sandbox:
            self._endpoint_public = "http://pub.sandbox.orcid.org"
        else:
            self._endpoint_public = "http://pub.orcid.org"

    def read_record_public(self, orcid_id, request_type, id=None,
                           response_format='json'):
        """Get the public info about the researcher.

        Parameters
        ----------
        :param orcid_id: string
            Id of the queried author
        :param request_type: string
            One of 'activities', 'education', 'employment', 'funding',
            'peer-review', 'work'
        :param response_format: string
            One of json, xml.
        :param id: string
            The id of the queried work. Must be given if 'request_type' is not
            'activities'.
        """
        return self._get_info(orcid_id, self._get_public_info, request_type,
                              response_format, id)

    def _get_info(self, orcid_id, function, request_type,
                  response_format='json', id=None):
        if request_type != "activities" and not id:
            raise ValueError("""In order to fetch specific record, please specify
                                the 'id' argument.""")
        elif request_type == "activities" and id:
            raise ValueError("""In order to fetch activities summary, the 'id'
                                argument is redundant.""")

        response = function(orcid_id, request_type, response_format, id)

        code = response.status_code

        response.raise_for_status()

        if response_format == "json":
            return json.loads(response.content)
        elif response_format == "xml":
            return etree.fromstring(response.content)

    def _get_public_info(self, orcid_id, request_type, response_format, id):
        request_url = '%s/%s/%s' % (self._endpoint_public + VERSION,
                                    orcid_id, request_type)
        if id:
            request_url += '/%s' % id
        headers = {'Accept': 'application/orcid+%s' % response_format}
        return requests.get(request_url, headers=headers)


class MemberAPI(PublicAPI):

    """Member API."""

    def __init__(self, institution_key, institution_secret, sandbox=False):
        """Initialize member API.

        Parameters
        ----------
        :param sandbox: boolean
            Should the sandbox be used. False (default) indicates production
            mode.
        """
        self._key = institution_key
        self._secret = institution_secret
        if sandbox:
            self._endpoint_member = "http://api.sandbox.orcid.org"
        else:
            self._endpoint_member = "https://api.orcid.org"
        PublicAPI.__init__(self, sandbox)

    def add_record(self, orcid_id, token, request_type, data=None, xml=None):
        self._update_activities(orcid_id, token, requests.post, request_type,
                                data, xml)

    def read_record_member(self, orcid_id, request_type, id=None,
                           response_format='json'):
        """Get the member info about the researcher.

        Parameters
        ----------
        :param orcid_id: string
            Id of the queried author
        :param request_type: string
            One of 'activities', 'education', 'employment', 'funding',
            'peer-review', 'work'
        :param response_format: string
            One of json, xml.
        :param id: string
            The id of the queried work. Must be given if 'request_type' is not
            'activities'.
        """
        return self._get_info(orcid_id, self._get_member_info, request_type,
                              response_format, id)

    def remove_record(self, orcid_id, token, request_type, id):
        self._update_activities(orcid_id, token, requests.delete, request_type,
                                None, None, id)

    def update_record(self, orcid_id, token, request_type, id, data=None,
                      xml=None):
        self._update_activities(orcid_id, token, requests.put, request_type,
                                data, xml, id)

    def _get_access_token_from_orcid(self, scope):
        payload = {'client_id': self._key,
                   'client_secret': self._secret,
                   'scope': scope,
                   'grant_type': 'client_credentials'
                   }

        request_url = "%s/oauth/token" % self._endpoint_member
        headers = {'Accept': 'application/json'}
        response = requests.post(request_url, data=payload, headers=headers)
        code = response.status_code

        res = None
        if code == requests.codes.ok:
            res = json.loads(response.content)['access_token']
        return res

    def _get_member_info(self, orcid_id, request_type, response_format, id):
        access_token = self. \
            _get_access_token_from_orcid('/activities/read-limited')
        request_url = '%s/%s/%s' % (self._endpoint_member + VERSION,
                                    orcid_id, request_type)
        if id:
            request_url += '/%s' % id
        headers = {'Accept': 'application/orcid+%s' % response_format,
                   'Authorization': 'Bearer %s' % access_token}
        return requests.get(request_url, headers=headers)

    def _update_activities(self, orcid_id, token, method, request_type, data,
                           xml, id=None):
        url = "%s/%s/%s" % (self._endpoint_member + VERSION, orcid_id,
                            request_type)
        if id:
            url += ('/%s' % id)
            if not xml and method != requests.delete:
                data['put_code'] = id

        if not xml and method != requests.delete:
            current_path = os.path.dirname(os.path.abspath(__file__))
            template_dir = '%s/templates/' % current_path
            environment = Environment(loader=FileSystemLoader(template_dir))
            template = environment.get_template("%s.xml" % request_type)
            xml = template.render({'record': data})

        headers = {'Accept': 'application/vnd.orcid+xml',
                   'Content-Type': 'application/vnd.orcid+xml',
                   'Authorization': 'Bearer ' + token}

        if method == requests.delete:
            response = method(url, headers=headers)
        else:
            print xml
            response = method(url, xml, headers=headers)

        code = response.status_code
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError, exc:
            print exc
            print response.text
