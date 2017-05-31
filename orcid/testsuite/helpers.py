# -*- coding: utf-8 -*-
"""Constants and helpers for python-orcid library."""


WORK_NAME2 = u'WY51MF0OCMU37MVGMUX1M92G6FR1IQUW0'

exemplary_work = {
      "title": {
        "title": {
          "value": WORK_NAME2
        },
      },
      "journal-title": {
        "value": "journal # 1"
      },
      "type": "JOURNAL_ARTICLE",
      "external-ids": {
        "external-id": [{
          "external-id-type": "doi",
          "external-id-value": "next-id-2",
          "external-id-url": {
            "value": "http://dx.doi.org/ext-id-1"
          },
          "external-id-relationship": "SELF"
        }]
      }
    }

