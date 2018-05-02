"""Implementation of python-orcid library."""

from bs4 import BeautifulSoup
import requests
import simplejson as json
import sys
from lxml import etree
if sys.version_info[0] == 2:
    from urllib import urlencode
    string_types = basestring,
else:
    from urllib.parse import urlencode
    string_types = str,


SEARCH_VERSION = "/v2.0"
VERSION = "/v2.0"

__version__ = "1.0.2"


class PublicAPI(object):
    """Public API."""

    TYPES_WITH_PUTCODES = set(['address',
                               'education',
                               'email',
                               'employment',
                               'external-identifier',
                               'funding',
                               'keywords',
                               'other-names',
                               'peer-review',
                               'researcher-urls',
                               'work'])

    TYPES_WITH_MULTIPLE_PUTCODES = set(['works'])

    def __init__(self, institution_key, institution_secret, sandbox=False,
                 timeout=None):
        """Initialize public API.

        Parameters
        ----------
        :param institution_key: string
            The ORCID key given to the institution
        :param institution_secret: string
            The ORCID secret given to the institution
        :param sandbox: boolean
            Should the sandbox be used. False (default) indicates production
            mode.
        :param timeout: float or tuple
            The request timeout in seconds. If None, no timeout is used. See
            `requests documentation
            <http://docs.python-requests.org/en/master/user/advanced/#timeouts>`_
            for more information.
        """
        self._key = institution_key
        self._secret = institution_secret
        self._timeout = timeout
        if sandbox:
            self._host = "sandbox.orcid.org"
            self._login_or_register_endpoint = \
                "https://sandbox.orcid.org/oauth/authorize"
            self._login_url = \
                "https://sandbox.orcid.org/oauth/custom/login.json"
            self._token_url = "https://api.sandbox.orcid.org/oauth/token"
            self._endpoint = "https://pub.sandbox.orcid.org"
        else:
            self._host = "orcid.org"
            self._login_or_register_endpoint = \
                "https://orcid.org/oauth/authorize"
            self._login_url = \
                'https://orcid.org/oauth/custom/login.json'
            self._token_url = "https://api.orcid.org/oauth/token"
            self._endpoint = "https://pub.orcid.org"

    def get_login_url(self, scope, redirect_uri, state=None,
                      family_names=None, given_names=None, email=None,
                      lang=None, show_login=None):
        """Return a URL for a user to login/register with ORCID.

        Parameters
        ----------
        :param scope: string or iterable of strings
            The scope(s) of the authorization request.
            For example '/authenticate'
        :param redirect_uri: string
            The URI to which the user's browser should be redirected after the
            login.
        :param state: string
            An arbitrary token to prevent CSRF. See the OAuth 2 docs for
            details.
        :param family_names: string
            The user's family name, used to fill the registration form.
        :param given_names: string
            The user's given name, used to fill the registration form.
        :param email: string
            The user's email address, used to fill the sign-in or registration
            form.
        :param lang: string
            The language in which to display the authorization page.
        :param show_login: bool
            Determines whether the log-in or registration form will be shown by
            default.

        Returns
        -------
        :returns: string
            The URL ready to be offered as a link to the user.
        """
        if not isinstance(scope, string_types):
            scope = " ".join(sorted(set(scope)))
        data = [("client_id", self._key), ("scope", scope),
                ("response_type", "code"), ("redirect_uri", redirect_uri)]
        if state:
            data.append(("state", state))
        if family_names:
            data.append(("family_names", family_names.encode("utf-8")))
        if given_names:
            data.append(("given_names", given_names.encode("utf-8")))
        if email:
            data.append(("email", email))
        if lang:
            data.append(("lang", lang))
        if show_login is not None:
            data.append(("show_login", "true" if show_login else "false"))
        return self._login_or_register_endpoint + "?" + urlencode(data)

    def search(self, query, method="lucene", start=None,
               rows=None, access_token=None):
        """Search the ORCID database.

        Parameters
        ----------
        :param query: string
            Query in line with the chosen method.
        :param method: string
            One of 'lucene', 'edismax', 'dismax'
        :param start: string
            Index of the first record requested. Use for pagination.
        :param rows: string
            Number of records requested. Use for pagination.
        :param access_token: string
            If obtained before, the access token to use to pass through
            authorization. Note that if this argument is not provided,
            the function will take more time.

        Returns
        -------
        :returns: dict
            Search result with error description available. The results can
            be obtained by accessing key 'result'. To get the number
            of all results, access the key 'num-found'.
        """
        if access_token is None:
            access_token = self. \
                get_search_token_from_orcid()

        headers = {'Accept': 'application/orcid+json',
                   'Authorization': 'Bearer %s' % access_token}

        return self._search(query, method, start, rows, headers,
                            self._endpoint)

    def search_generator(self, query, method="lucene",
                         pagination=10, access_token=None):
        """Search the ORCID database with a generator.

        The generator will yield every result.

        Parameters
        ----------
        :param query: string
            Query in line with the chosen method.
        :param method: string
            One of 'lucene', 'edismax', 'dismax'
        :param pagination: integer
            How many papers should be fetched with the request.
        :param access_token: string
            If obtained before, the access token to use to pass through
            authorization. Note that if this argument is not provided,
            the function will take more time.

        Yields
        -------
        :yields: dict
            Single profile from the search results.
        """
        if access_token is None:
            access_token = self. \
                get_search_token_from_orcid()

        headers = {'Accept': 'application/orcid+json',
                   'Authorization': 'Bearer %s' % access_token}

        index = 0

        while True:
            paginated_result = self._search(query, method, index, pagination,
                                            headers, self._endpoint)
            if not paginated_result['result']:
                return

            for result in paginated_result['result']:
                yield result
            index += pagination

    def get_search_token_from_orcid(self, scope='/read-public'):
        """Get a token for searching ORCID records.

        Parameters
        ----------
        :param scope: string
            /read-public or /read-member

        Returns
        -------
        :returns: string
            The token.
        """
        payload = {'client_id': self._key,
                   'client_secret': self._secret,
                   'scope': scope,
                   'grant_type': 'client_credentials'
                   }

        url = "%s/oauth/token" % self._endpoint
        headers = {'Accept': 'application/json'}

        response = requests.post(url, data=payload, headers=headers,
                                 timeout=self._timeout)
        response.raise_for_status()
        return response.json()['access_token']

    def get_token(self, user_id, password, redirect_uri,
                  scope='/read-limited'):
        """Get the token.

        Parameters
        ----------
        :param user_id: string
            The id of the user used for authentication.
        :param password: string
            The user password.
        :param redirect_uri: string
            The redirect uri of the institution.
        :param scope: string
            The desired scope. For example '/activities/update',
            '/read-limited', etc.

        Returns
        -------
        :returns: string
            The token.
        """
        response = self._authenticate(user_id, password, redirect_uri,
                                      scope)
        return response['access_token']

    def get_token_from_authorization_code(self,
                                          authorization_code, redirect_uri):
        """Like `get_token`, but using an OAuth 2 authorization code.

        Use this method if you run a webserver that serves as an endpoint for
        the redirect URI. The webserver can retrieve the authorization code
        from the URL that is requested by ORCID.

        Parameters
        ----------
        :param redirect_uri: string
            The redirect uri of the institution.
        :param authorization_code: string
            The authorization code.

        Returns
        -------
        :returns: dict
            All data of the access token.  The access token itself is in the
            ``"access_token"`` key.
        """
        token_dict = {
            "client_id": self._key,
            "client_secret": self._secret,
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": redirect_uri,
        }
        response = requests.post(self._token_url, data=token_dict,
                                 headers={'Accept': 'application/json'},
                                 timeout=self._timeout)
        response.raise_for_status()
        return json.loads(response.text)

    def read_record_public(self, orcid_id, request_type, token, put_code=None,
                           accept_type='application/orcid+json'):
        """Get the public info about the researcher.

        Parameters
        ----------
        :param orcid_id: string
            Id of the queried author.
        :param request_type: string
            For example: 'record'.
            See https://members.orcid.org/api/tutorial/read-orcid-records
            for possible values.
        :param token: string
            Token received from OAuth 2 3-legged authorization.
        :param put_code: string | list of strings
            The id of the queried work. In case of 'works' request_type
            might be a list of strings
        :param accept_type: expected MIME type of received data

        Returns
        -------
        :returns: dict | lxml.etree._Element
            Record(s) in JSON-compatible dictionary representation or
            in XML E-tree, depending on accept_type specified.
        """
        return self._get_info(orcid_id, self._get_public_info, request_type,
                              token, put_code, accept_type)

    def _authenticate(self, user_id, password, redirect_uri, scope):

        session = requests.session()
        session.get('https://' + self._host + '/signout',
                    timeout=self._timeout)
        params = {
            'client_id': self._key,
            'response_type': 'code',
            'scope': scope,
            'redirect_uri': redirect_uri
        }

        response = session.get(self._login_or_register_endpoint,
                               params=params,
                               headers={'Host': self._host},
                               timeout=self._timeout)

        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html5lib')
        csrf = soup.find(attrs={'name': '_csrf'}).attrs['content']
        headers = {
            'Host': self._host,
            'Origin': 'https://' + self._host,
            'Content-Type': 'application/json;charset=UTF-8',
            'X-CSRF-TOKEN': csrf
        }

        data = {
            "userName": user_id,
            "password": password,
            "approved": True,
            "persistentTokenEnabled": True,
            "redirectUrl": None
        }

        response = session.post(
            self._login_url,
            data=json.dumps(data),
            headers=headers
        )
        response.raise_for_status()

        uri = json.loads(response.text)['redirectUrl']
        authorization_code = uri[uri.rfind('=') + 1:]

        return self.get_token_from_authorization_code(authorization_code,
                                                      redirect_uri)

    def _get_info(self, orcid_id, function, request_type, token,
                  put_code=None, accept_type='application/orcid+json'):
        if request_type in self.TYPES_WITH_PUTCODES and not put_code:
            raise ValueError("""In order to fetch specific record,
                                please specify the 'put_code' argument.""")
        elif request_type not in self.TYPES_WITH_PUTCODES and \
                request_type not in self.TYPES_WITH_MULTIPLE_PUTCODES \
                and isinstance(put_code, str):
            raise ValueError("""In order to fetch a summary, the
                                'put_code' argument is redundant.""")
        elif request_type in self.TYPES_WITH_MULTIPLE_PUTCODES \
                and put_code is not None and not isinstance(put_code, list):
            raise ValueError("""In order to fetch multiple records,
                               the 'put_code' should be a list.""")
        response = function(orcid_id, request_type, token,
                            put_code, accept_type)
        response.raise_for_status()
        return self._deserialize_by_content_type(response.content, accept_type)

    def _get_public_info(self, orcid_id, request_type, access_token, put_code,
                         accept_type):
        request_url = '%s/%s/%s' % (self._endpoint + VERSION,
                                    orcid_id, request_type)
        if put_code:
            if request_type in self.TYPES_WITH_MULTIPLE_PUTCODES:
                request_url += '/%s' % ','.join(put_code)
            else:
                request_url += '/%s' % put_code
        headers = {'Accept': accept_type,
                   'Authorization': 'Bearer %s' % access_token}
        return requests.get(request_url, headers=headers,
                            timeout=self._timeout)

    def _search(self, query, method, start, rows, headers,
                endpoint):
        url = endpoint + SEARCH_VERSION + \
                "/search/?defType=" + method + "&q=" + query
        if start:
            url += "&start=%s" % start
        if rows:
            url += "&rows=%s" % rows

        response = requests.get(url, headers=headers,
                                timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def _deserialize_by_content_type(self, data, content_type):
        if content_type == 'application/orcid+json':
            return json.loads(data)
        if content_type == 'application/orcid+xml':
            return etree.XML(data)
        raise NotImplementedError('No deserializer for content of type %s'
                                  % content_type)


class MemberAPI(PublicAPI):
    """Member API."""

    def __init__(self, institution_key, institution_secret, sandbox=False,
                 timeout=None):
        """Initialize member API.

        Parameters
        ----------
        :param institution_key: string
            The ORCID key given to the institution
        :param institution_secret: string
            The ORCID secret given to the institution
        :param sandbox: boolean
            Should the sandbox be used. False (default) indicates production
            mode.
        :param timeout: float or tuple
            The request timeout in seconds. If None, no timeout is used. See
            `requests documentation
            <http://docs.python-requests.org/en/master/user/advanced/#timeouts>`_
            for more information.
        """
        super(MemberAPI, self).__init__(institution_key,
                                        institution_secret, sandbox, timeout)

        if sandbox:
            self._endpoint = "https://api.sandbox.orcid.org"
            self._auth_url = 'https://sandbox.orcid.org/signin/auth.json'
            self._authorize_url = \
                'https://sandbox.orcid.org/oauth/custom/authorize.json'
        else:
            self._endpoint = "https://api.orcid.org"
            self._auth_url = 'https://orcid.org/signin/auth.json'
            self._authorize_url = \
                'https://orcid.org/oauth/custom/authorize.json'

    def add_record(self, orcid_id, token, request_type, data,
                   content_type='application/orcid+json'):
        """Add a record to a profile.

        Parameters
        ----------
        :param orcid_id: string
            Id of the author.
        :param token: string
            Token received from OAuth 2 3-legged authorization.
        :param request_type: string
            One of 'activities', 'education', 'employment', 'funding',
            'peer-review', 'work'.
        :param data: dict | lxml.etree._Element
            The record in Python-friendly format, as either JSON-compatible
            dictionary (content_type == 'application/orcid+json') or
            XML (content_type == 'application/orcid+xml')
        :param content_type: string
            MIME type of the passed record.

        Returns
        -------
        :returns: string
            Put-code of the new work.
        """
        return self._update_activities(orcid_id, token, requests.post,
                                       request_type, data,
                                       content_type=content_type)

    def get_token(self, user_id, password, redirect_uri,
                  scope='/activities/update'):
        """Get the token.

        Parameters
        ----------
        :param user_id: string

            The id of the user used for authentication.
        :param password: string
            The user password.
        :param redirect_uri: string
            The redirect uri of the institution.
        :param scope: string
            The desired scope. For example '/activities/update',
            '/read-limited', etc.

        Returns
        -------
        :returns: string
            The token.
        """
        return super(MemberAPI, self).get_token(user_id, password,
                                                redirect_uri, scope)

    def get_user_orcid(self, user_id, password, redirect_uri):
        """Get the user orcid from authentication process.

        Parameters
        ----------
        :param user_id: string
            The id of the user used for authentication.
        :param password: string
            The user password.
        :param redirect_uri: string
            The redirect uri of the institution.

        Returns
        -------
        :returns: string
            The orcid.
        """
        response = self._authenticate(user_id, password, redirect_uri,
                                      '/authenticate')

        return response['orcid']

    def read_record_member(self, orcid_id, request_type, token, put_code=None,
                           accept_type='application/orcid+json'):
        """Get the member info about the researcher.

        Parameters
        ----------
        :param orcid_id: string
            Id of the queried author.
        :param request_type: string
            For example: 'record'.
            See https://members.orcid.org/api/tutorial/read-orcid-records
            for possible values..
        :param response_format: string
            One of json, xml.
        :param token: string
            Token received from OAuth 2 3-legged authorization.
        :param put_code: string | list of strings
            The id of the queried work. In case of 'works' request_type
            might be a list of strings
        :param accept_type: expected MIME type of received data

        Returns
        -------
        :returns: dict | lxml.etree._Element
            Record(s) in JSON-compatible dictionary representation or
            in XML E-tree, depending on accept_type specified.
        """
        return self._get_info(orcid_id, self._get_member_info, request_type,
                              token, put_code, accept_type)

    def remove_record(self, orcid_id, token, request_type, put_code):
        """Add a record to a profile.

        Parameters
        ----------
        :param orcid_id: string
            Id of the author.
        :param token: string
            Token received from OAuth 2 3-legged authorization.
        :param request_type: string
            One of 'activities', 'education', 'employment', 'funding',
            'peer-review', 'work'.
         :param put_code: string
            The id of the record. Can be retrieved using read_record_* method.
            In the result of it, it will be called 'put-code'.
        """
        self._update_activities(orcid_id, token, requests.delete, request_type,
                                put_code=put_code)

    def search(self, query, method="lucene", start=None, rows=None,
               access_token=None):
        """Search the ORCID database.

        Parameters
        ----------
        :param query: string
            Query in line with the chosen method.
        :param method: string
            One of 'lucene', 'edismax', 'dismax'
        :param start: string
            Index of the first record requested. Use for pagination.
        :param rows: string
            Number of records requested. Use for pagination.
        :param access_token: string
            If obtained before, the access token to use to pass through
            authorization. Note that if this argument is not provided,
            the function will take more time.

        Returns
        -------
        :returns: dict
            Search result with error description available. The results can
            be obtained by accessing key 'result'.
            To get the number of all results, access the key 'num-found'.
        """
        if access_token is None:
            access_token = self. \
                get_search_token_from_orcid()

        headers = {'Accept': 'application/orcid+json',
                   'Authorization': 'Bearer %s' % access_token}

        return self._search(query, method, start, rows, headers,
                            self._endpoint)

    def search_generator(self, query, method="lucene", pagination=10,
                         access_token=None):
        """Search the ORCID database with a generator.

        The generator will yield every result.

        Parameters
        ----------
        :param query: string
            Query in line with the chosen method.
        :param method: string
            One of 'lucene', 'edismax', 'dismax'
        :param pagination: integer
            How many papers should be fetched with the request.
        :param access_token: string
            If obtained before, the access token to use to pass through
            authorization. Note that if this argument is not provided,
            the function will take more time.
        """
        if access_token is None:
            access_token = self. \
                get_search_token_from_orcid()

        headers = {'Accept': 'application/orcid+json',
                   'Authorization': 'Bearer %s' % access_token}

        index = 0

        while True:
            paginated_result = self._search(query, method, index, pagination,
                                            headers, self._endpoint)
            if not paginated_result['result']:
                return

            for result in paginated_result['result']:
                yield result
            index += pagination

    def update_record(self, orcid_id, token, request_type, data, put_code,
                      content_type='application/orcid+json'):
        """Add a record to a profile.

        Parameters
        ----------
        :param orcid_id: string
            Id of the author.
        :param token: string
            Token received from OAuth 2 3-legged authorization.
        :param request_type: string
            One of 'activities', 'education', 'employment', 'funding',
            'peer-review', 'work'.
        :param data: dict | lxml.etree._Element
            The record in Python-friendly format, as either JSON-compatible
            dictionary (content_type == 'application/orcid+json') or
            XML (content_type == 'application/orcid+xml')
        :param put_code: string
            The id of the record. Can be retrieved using read_record_* method.
            In the result of it, it will be called 'put-code'.
        :param content_type: string
            MIME type of the data being sent.
        """
        self._update_activities(orcid_id, token, requests.put, request_type,
                                data, put_code, content_type)

    def _get_member_info(self, orcid_id, request_type, access_token, put_code,
                         accept_type):
        request_url = '%s/%s/%s' % (self._endpoint + VERSION,
                                    orcid_id, request_type)
        if put_code:
            if request_type in self.TYPES_WITH_MULTIPLE_PUTCODES:
                request_url += '/%s' % ','.join(put_code)
            else:
                request_url += '/%s' % put_code
        headers = {'Accept': accept_type,
                   'Authorization': 'Bearer %s' % access_token}
        return requests.get(request_url, headers=headers,
                            timeout=self._timeout)

    def _update_activities(self, orcid_id, token, method, request_type,
                           data=None, put_code=None,
                           content_type='application/orcid+json'):
        url = "%s/%s/%s" % (self._endpoint + VERSION, orcid_id,
                            request_type)

        if put_code:
            url += ('/%s' % put_code)
            if data is not None:
                self._add_put_code_by_content_type(content_type, data,
                                                   put_code)

        headers = {'Accept': 'application/orcid+json',
                   'Content-Type': content_type,
                   'Authorization': 'Bearer ' + token}

        if method == requests.delete:
            response = method(url, headers=headers, timeout=self._timeout)
        else:
            xml = self._serialize_by_content_type(data, content_type)
            response = method(url, xml, headers=headers, timeout=self._timeout)

        response.raise_for_status()

        if 'location' in response.headers:
            # Return the new put-code
            return response.headers['location'].split('/')[-1]

    def _add_put_code_by_content_type(self, content_type, data, put_code):
        if content_type == 'application/orcid+json':
            data['put-code'] = put_code
        elif content_type == 'application/orcid+xml':
            data.attrib['put-code'] = '%s' % put_code
        else:
            raise NotImplementedError('Cannot add to content of type %s'
                                      % content_type)

    def _serialize_by_content_type(self, data, content_type):
        if content_type == 'application/orcid+json':
            return json.dumps(data)
        if content_type == 'application/orcid+xml':
            return etree.tostring(data)
        raise NotImplementedError('No serializer for content of type %s'
                                  % content_type)
