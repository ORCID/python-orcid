# -*- coding: utf-8 -*-
"""Constants and helpers for python-orcid library."""


WORK_NAME2 = u'WY51MF0OCMU37MVGMUX1M92G6FR1IQUW0'

exemplary_work = {
        'title': {'title': WORK_NAME2,
                  'subtitle': 'My Subtitle',
                  'translated-title': {
                    'language-code': 'pl',
                    'value': u'API Tytuł testowy'}
                  },
        'journal-title': 'Journal Title',
        'short-description': 'My abstract',
        'citation': {
            'citation': '''@article {ORCIDtest2014,
                           author = "Lastname, Firstname",
                           title = "API Test Title",
                           journal = "Journal Title",
                           volume = "25",
                           number = "4",
                           year = "2010",
                           pages = "259-264",
                           doi = "doi:10.1087/20120404"
                         }''',
            # Available types:
            # 'FORMATTED-UNSPECIFIED'
            # 'BIBTEX'
            # 'FORMATTED_APA'
            # 'FORMATTED_HARVARD'
            # 'FORMATTED_IEEE'
            # 'FORMATTED_MLA'
            # 'FORMATTED_VANCOUVER'
            # 'FORMATTED_CHICAGO'
            'citation-type': 'BIBTEX'
        },
        # See http://members.orcid.org/api/supported-work-types
        'type': 'JOURNAL_ARTICLE',
        'publication-date': {'year': 2010,
                             'month': 11,
                             'day': 10
                             },
        # See http://members.orcid.org/api/supported-work-identifiers
        'external-ids': {'external-id': [{
            'external-id-type': 'source-work-id',
            'external-id-value': '1234',
            'external-id-url': 'www.example.com/12344'
        }]},
        'url': 'https://github.com/MSusik/python-orcid',
        'contributors': {'contributor': [{
            'credit-name': 'LastName, FirstName',
            'contributor-orcid': '0000-0001-5109-3700',
            'contributor-email': 'somebody@mailinator.com',
            'contributor-attributes': {
                # Supported roles:
                # 'AUTHOR'
                # 'ASSIGNEE'
                # 'EDITOR'
                # 'CHAIR_OR_TRANSLATOR'
                # 'CO_INVESTIGATOR'
                # 'CO_INVENTOR'
                # 'GRADUATE_STUDENT'
                # 'OTHER_INVENTOR'
                # 'PRINCIPAL_INVESTIGATOR'
                # 'POSTDOCTORAL_RESEARCHER'
                # 'SUPPORT_STAFF'
                'contributor-role': 'SUPPORT_STAFF',
                # One of 'ADDITIONAL', 'FIRST'
                'contributor-sequence': 'ADDITIONAL'
            }
        }]},
        # ISO-629-1: http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        'language-code': 'en',
        'country': {'value': 'US', 'visibility': 'PUBLIC'}
    }
