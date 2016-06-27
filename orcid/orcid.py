"""Implementation of python-orcid library."""

from bs4 import BeautifulSoup
import requests
import simplejson as json
import sys
if sys.version_info[0] == 2:
    from urllib import urlencode
    string_types = basestring,
else:
    from urllib.parse import urlencode
    string_types = str,


SEARCH_VERSION = "/v1.2"
VERSION = "/v2.0_rc2"

__version__ = "0.7.0"


class SearchAPI(object):
    """Search API."""

    def __init__(self, sandbox=False):
        """Initialize search API.

        Parameters
        ----------
        :param sandbox: boolean
            Should the sandbox be used. False (default) indicates production
            mode.
        """
        if sandbox:
            self._endpoint_public = "https://pub.sandbox.orcid.org"
        else:
            self._endpoint_public = "https://pub.orcid.org"

    def search_public(self, query, method="lucene", start=None, rows=None,
                      search_field="orcid-bio"):
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
        :param search_field: string
            Scope used for searching. The default one allows to search
            everywhere.

        Returns
        -------
        :returns: dict
            Search result with error description available. The results can
            be obtained by accessing keys 'orcid-search-results' and
            then 'orcid-search-result'. To get the number of all results,
            access the key 'orcid-search-results' and then 'num-found'.
        """
        headers = {'Accept': 'application/orcid+json'}

        return self._search(query, method, start, rows, search_field,
                            headers, self._endpoint_public)

    def search_public_generator(self, query, method="lucene",
                                search_field="orcid-bio", pagination=10):
        """Search the ORCID database with a generator.

        The generator will yield every result.

        Parameters
        ----------
        :param query: string
            Query in line with the chosen method.
        :param method: string
            One of 'lucene', 'edismax', 'dismax'
        :param search_field: string
            Scope used for seaching. The default one allows to search
            everywhere.
        :param pagination: integer
            How many papers should be fetched with the request.

        Yields
        -------
        :yields: dict
            Single profile from the search results.
        """
        headers = {'Accept': 'application/orcid+json'}

        index = 0

        while True:
            paginated_result = self._search(query, method, index, pagination,
                                            search_field, headers,
                                            self._endpoint_public)
            if not paginated_result['orcid-search-results'][
                                    'orcid-search-result']:
                return

            for result in paginated_result['orcid-search-results'][
                                           'orcid-search-result']:
                yield result
            index += pagination

    def _search(self, query, method, start, rows, search_field, headers,
                endpoint):

        url = endpoint + SEARCH_VERSION + "/search/" + \
            search_field + "/?defType=" + method + "&q=" + query
        if start:
            url += "&start=%s" % start
        if rows:
            url += "&rows=%s" % rows
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


class PublicAPI(SearchAPI):
    """Public API."""

    TYPES_WITH_PUTCODES = set(['education',
                               'employment',
                               'funding',
                               'peer-review',
                               'work'])

    def __init__(self, institution_key, institution_secret, sandbox=False):
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
        """
        self._key = institution_key
        self._secret = institution_secret
        if sandbox:
            self._host = "sandbox.orcid.org"
            self._login_or_register_endpoint = \
                "https://sandbox.orcid.org/oauth/authorize"
            self._login_url = \
                "https://sandbox.orcid.org/oauth/custom/login.json"
            self._token_url = "https://api.sandbox.orcid.org/oauth/token"
        else:
            self._host = "orcid.org"
            self._login_or_register_endpoint = \
                "https://orcid.org/oauth/authorize"
            self._login_url = \
                'https://orcid.org/oauth/custom/login.json'
            self._token_url = "https://api.orcid.org/oauth/token"

        SearchAPI.__init__(self, sandbox)

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
                                 headers={'Accept': 'application/json'})
        response.raise_for_status()
        return json.loads(response.text)

    def read_record_public(self, orcid_id, request_type, token, put_code=None):
        """Get the public info about the researcher.

        Parameters
        ----------
        :param orcid_id: string
            Id of the queried author.
        :param request_type: string
            One of 'activities', 'address', 'education', 'email', 'employment',
            'external-identifiers', 'funding', 'keywords', 'other-names'
            'peer-review', 'personal-details', 'person', 'work'.
        :param token: string
            Token received from OAuth 2 3-legged authorization.
        :param put_code: string
            The id of the queried work. Must be given if 'request_type' is not
            'activities'.

        Returns
        -------
        :returns: dict
            Records.
        """
        return self._get_info(orcid_id, self._get_public_info, request_type,
                              token, put_code)

    def _authenticate(self, user_id, password, redirect_uri, scope):

        session = requests.session()
        session.get('https://' + self._host + '/signout')
        params = {
            'client_id': self._key,
            'response_type': 'code',
            'scope': scope,
            'redirect_uri': redirect_uri
        }

        response = session.get(self._login_or_register_endpoint,
                               params=params,
                               headers={'Host': self._host})

        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
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
                  put_code=None):
        if request_type in self.TYPES_WITH_PUTCODES and not put_code:
            raise ValueError("""In order to fetch specific record,
                                please specify the 'put_code' argument.""")
        elif request_type not in self.TYPES_WITH_PUTCODES and put_code:
            raise ValueError("""In order to fetch activities summary, the 'id'
                                argument is redundant.""")
        response = function(orcid_id, request_type, token, put_code)
        response.raise_for_status()
        return response.json()

    def _get_public_info(self, orcid_id, request_type, access_token, put_code):
        request_url = '%s/%s/%s' % (self._endpoint_public + VERSION,
                                    orcid_id, request_type)
        if put_code:
            request_url += '/%s' % put_code
        headers = {'Accept': 'application/orcid+json',
                   'Authorization': 'Bearer %s' % access_token}
        return requests.get(request_url, headers=headers)


class MemberAPI(PublicAPI):
    """Member API."""

    def __init__(self, institution_key, institution_secret, sandbox=False):
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
        """
        if sandbox:
            self._endpoint_member = "https://api.sandbox.orcid.org"
            self._auth_url = 'https://sandbox.orcid.org/signin/auth.json'
            self._authorize_url = \
                'https://sandbox.orcid.org/oauth/custom/authorize.json'
        else:
            self._endpoint_member = "https://api.orcid.org"
            self._auth_url = 'https://orcid.org/signin/auth.json'
            self._authorize_url = \
                'https://orcid.org/oauth/custom/authorize.json'

        PublicAPI.__init__(self, institution_key, institution_secret, sandbox)

    def add_record(self, orcid_id, token, request_type, data):
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
        :param data: dict
            The record in Python-friendly format. Required if xml is not
            provided.

        Returns
        -------
        :returns: string
            Put-code of the new work.
        """
        return self._update_activities(orcid_id, token, requests.post,
                                       request_type, data)

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

    def read_record_member(self, orcid_id, request_type, token, put_code=None):
        """Get the member info about the researcher.

        Parameters
        ----------
        :param orcid_id: string
            Id of the queried author.
        :param request_type: string
            One of 'activities', 'education', 'employment', 'funding',
            'peer-review', 'work'.
        :param response_format: string
            One of json, xml.
        :param token: string
            Token received from OAuth 2 3-legged authorization.
        :param put_code: string
            The id of the queried work. Must be given if 'request_type' is not
            'activities'.

        Returns
        -------
        :returns: dictionary
            Records.
        """
        return self._get_info(orcid_id, self._get_member_info, request_type,
                              token, put_code)

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

    def search_member(self, query, method="lucene", start=None, rows=None,
                      search_field="orcid-bio"):
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
        :search_field: string
            Scope used for seaching. The default one allows to search
            everywhere.

        Returns
        -------
        :returns: dict
            Search result with error description available. The results can
            be obtained by accessing keys 'orcid-search-results' and
            then 'orcid-search-result'. To get the number of all results,
            access the key 'orcid-search-results' and then 'num-found'.
        """
        access_token = self. \
            _get_access_token_from_orcid('/read-public')

        headers = {'Accept': 'application/orcid+json',
                   'Authorization': 'Bearer %s' % access_token}

        return self._search(query, method, start, rows, search_field, headers,
                            self._endpoint_member)

    def search_member_generator(self, query, method="lucene",
                                search_field="orcid-bio", pagination=10):
        """Search the ORCID database with a generator.

        The generator will yield every result.

        Parameters
        ----------
        :param query: string
            Query in line with the chosen method.
        :param method: string
            One of 'lucene', 'edismax', 'dismax'
        :param search_field: string
            Scope used for seaching. The default one allows to search
            everywhere.
        :param pagination: integer
            How many papers should be fetched with the request.
        """
        access_token = self. \
            _get_access_token_from_orcid('/read-public')

        headers = {'Accept': 'application/orcid+json',
                   'Authorization': 'Bearer %s' % access_token}

        index = 0

        while True:
            paginated_result = self._search(query, method, index, pagination,
                                            search_field, headers,
                                            self._endpoint_member)
            if not paginated_result['orcid-search-results'][
                                    'orcid-search-result']:
                return

            for result in paginated_result['orcid-search-results'][
                                           'orcid-search-result']:
                yield result
            index += pagination

    def update_record(self, orcid_id, token, request_type, data, put_code):
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
        :param data: dict
            The record in Python-friendly format. Required if xml is not
            provided.
         :param put_code: string
            The id of the record. Can be retrieved using read_record_* method.
            In the result of it, it will be called 'put-code'.
        """
        self._update_activities(orcid_id, token, requests.put, request_type,
                                data, put_code)

    def _get_access_token_from_orcid(self, scope):
        payload = {'client_id': self._key,
                   'client_secret': self._secret,
                   'scope': scope,
                   'grant_type': 'client_credentials'
                   }

        url = "%s/oauth/token" % self._endpoint_member
        headers = {'Accept': 'application/json'}

        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        return response.json()['access_token']

    def _get_member_info(self, orcid_id, request_type, access_token, put_code):
        request_url = '%s/%s/%s' % (self._endpoint_member + VERSION,
                                    orcid_id, request_type)
        if put_code:
            request_url += '/%s' % put_code
        headers = {'Accept': 'application/orcid+json',
                   'Authorization': 'Bearer %s' % access_token}
        return requests.get(request_url, headers=headers)

    def _update_activities(self, orcid_id, token, method, request_type,
                           data=None, put_code=None):
        url = "%s/%s/%s" % (self._endpoint_member + VERSION, orcid_id,
                            request_type)

        if put_code:
            url += ('/%s' % put_code)
            if data:
                data['put-code'] = put_code

        headers = {'Accept': 'application/orcid+json',
                   'Content-Type': 'application/orcid+json',
                   'Authorization': 'Bearer ' + token}

        if method == requests.delete:
            response = method(url, headers=headers)
        else:
            xml = json.dumps(data)
            response = method(url, xml, headers=headers)

        response.raise_for_status()

        if 'location' in response.headers:
            # Return the new put-code
            return response.headers['location'].split('/')[-1]
