"""Implementation of python-orcid library."""

import simplejson as json
import requests

SEARCH_VERSION = "/v1.2"
VERSION = "/v2.0_rc1"

__version__ = "0.5.1"


class PublicAPI(object):

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
            self._endpoint_public = "https://pub.sandbox.orcid.org"
        else:
            self._endpoint_public = "https://pub.orcid.org"

    def read_record_public(self, orcid_id, request_type, put_code=None):
        """Get the public info about the researcher.

        Parameters
        ----------
        :param orcid_id: string
            Id of the queried author.
        :param request_type: string
            One of 'activities', 'education', 'employment', 'funding',
            'peer-review', 'work'.
        :param put_code: string
            The id of the queried work. Must be given if 'request_type' is not
            'activities'.

        Returns
        -------
        :returns: dict
            Records.
        """
        return self._get_info(orcid_id, self._get_public_info, request_type,
                              put_code)

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
            How many papers should be fetched with ine request.

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

    def _get_info(self, orcid_id, function, request_type, put_code=None):
        if request_type != "activities" and not put_code:
            raise ValueError("""In order to fetch specific record,
                                please specify the 'put_code' argument.""")
        elif request_type == "activities" and put_code:
            raise ValueError("""In order to fetch activities summary, the 'id'
                                argument is redundant.""")
        response = function(orcid_id, request_type, put_code)
        response.raise_for_status()
        return response.json()

    def _get_public_info(self, orcid_id, request_type, put_code):
        request_url = '%s/%s/%s' % (self._endpoint_public + VERSION,
                                    orcid_id, request_type)
        if put_code:
            request_url += '/%s' % put_code
        headers = {'Accept': 'application/orcid+json'}
        return requests.get(request_url, headers=headers)

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
            self._endpoint_member = "https://api.sandbox.orcid.org"
            self._auth_url = 'https://sandbox.orcid.org/signin/auth.json'
            self._authorize_url = \
                'https://sandbox.orcid.org/oauth/custom/authorize.json'
            self._token_url = "https://api.sandbox.orcid.org/oauth/token"
        else:
            self._endpoint_member = "https://api.orcid.org"
            self._auth_url = 'https://orcid.org/signin/auth.json'
            self._authorize_url = \
                'https://orcid.org/oauth/custom/authorize.json'
            self._token_url = "https://api.orcid.org/oauth/token"
        PublicAPI.__init__(self, sandbox)

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
        session = requests.session()
        response = self._authenticate(user_id, password, redirect_uri, session,
                                      '/authenticate')

        return response['orcid']

    def get_token(self, user_id, password, redirect_uri):
        """Get the token for updating the records.

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
            The token.
        """
        session = requests.session()
        response = self._authenticate(user_id, password, redirect_uri, session,
                                      '/activities/update')

        return response['access_token']

    def read_record_member(self, orcid_id, request_type, put_code=None):
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
        :param put_code: string
            The id of the queried work. Must be given if 'request_type' is not
            'activities'.

        Returns
        -------
        :returns: dictionary
            Records.
        """
        return self._get_info(orcid_id, self._get_member_info, request_type,
                              put_code)

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
            How many papers should be fetched with ine request.
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

    def _authenticate(self, user_id, password, redirect_uri, session, scope):
        response = session.post(self._auth_url,
                                data={'userId': user_id, 'password': password})
        response.raise_for_status()

        response = session.get('https://sandbox.orcid.org/oauth/' +
                               'authorize?client_id=' + self._key +
                               '&response_type=code&scope=' + scope +
                               '&redirect_uri=' + redirect_uri)

        response.raise_for_status()
        session.close()

        json_dict = {
            "clientId": self._key,
            "redirectUri": redirect_uri,
            "scope": scope,
            "responseType": "code",
            "approved": "true",
            "persistentTokenEnabled": "true"
        }
        headers = {
           'Accept': 'text/plain',
           'Content-Type': 'application/json;charset=UTF-8'
        }
        response = session.post(self._authorize_url,
                                data=json.dumps(json_dict),
                                headers=headers
                                )
        response.raise_for_status()
        session.close()

        uri = json.loads(response.text)['redirectUri']['value']
        authorization_code = uri[uri.rfind('=') + 1:]

        token_dict = {
            "client_id": self._key,
            "client_secret": self._secret,
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": redirect_uri,
        }
        response = session.post(self._token_url, data=token_dict,
                                headers={'Accept': 'application/json'})
        response.raise_for_status()
        return json.loads(response.text)

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

    def _get_member_info(self, orcid_id, request_type, put_code):
        access_token = self. \
            _get_access_token_from_orcid('/activities/read-limited')
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
