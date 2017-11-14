# -*- coding: utf-8 -*-
"""Constants and helpers for python-orcid library."""

from lxml.etree import XML

WORK_NAME2 = u'WY51MF0OCMU37MVGMUX1M92G6FR1IQUW0'
WORK_NAME3 = u'BN237DFI2GF69DFH4Y60FK2J48DF0SKJ5'

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

exemplary_work_xml = XML("""
<work:work
        xmlns:common="http://www.orcid.org/ns/common"
        xmlns:work="http://www.orcid.org/ns/work">
    <work:title>
        <common:title>""" + WORK_NAME3 + """</common:title>
    </work:title>
    <work:journal-title>journal # 2</work:journal-title>
    <work:type>journal-article</work:type>
    <common:publication-date>
        <common:year>1961</common:year>
    </common:publication-date>
    <common:external-ids>
        <common:external-id>
            <common:external-id-type>doi</common:external-id-type>
            <common:external-id-value>ext-id-3</common:external-id-value>
            <common:external-id-url>http://dx.doi.org/ext-id-3</common:external-id-url>
            <common:external-id-relationship>self</common:external-id-relationship>
        </common:external-id>
    </common:external-ids>
</work:work>
""")
