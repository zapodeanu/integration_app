#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""



Copyright (c) 2022 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Gabriel Zapodeanu TME, ENB"
__email__ = "gzapodea@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2022 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import requests
import urllib3
import json
from dotenv import load_dotenv
import os

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
from requests.auth import HTTPBasicAuth  # for Basic Auth

from config import JIRA_URL, JIRA_EMAIL


load_dotenv('environment.env')

JIRA_API_KEY = os.getenv('JIRA_API_KEY')


urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

JIRA_AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_KEY)


def get_customer_issues(issue_number):
    """
    This function will return the details for the customer issue with the number {issue_number}
    Sample format for the issue number {JMIS-44}
    :param issue_number: string with the issue number
    :return: the issue details
    """
    url = JIRA_URL + '/rest/api/2/issue/' + issue_number
    header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.get(url, auth=JIRA_AUTH, headers=header)
    print(response.status_code)
    response_json = response.json()
    return response_json


def create_customer_issue(jira_project, jira_component, summary, description, severity, jira_email):
    """
    This function will create a new customer issue
    :param jira_project: The project used for the Service Desk
    :param jira_component: type of issue, example; Cisco DNA Center Notification
    :param summary: issue summary
    :param description: issue description
    :param severity: priority of the issue
    :param jira_email: the email of the Jira user to assign the ticket to
    :return:
    """
    url = JIRA_URL + '/rest/api/2/issue'
    print(url)
    payload = {
        "fields": {
            "issuetype": {
                "id": "10004"  # For system outages or incidents. Created by Jira Service Desk (default)
            },
            "project": {
                "key": jira_project
            },
            "description": description,
            "summary": summary,
            "priority": {
                "id": severity
            },
            "components": [
                {
                    "id": jira_component  # Cisco DNA Center Notification
                }
            ]
        },
        "assignee": {
            "emailAddress": jira_email,  # default for admin account
        },
        "creator": {
            "emailAddress": jira_email,
            "timeZone": "America/Los_Angeles",
        }
    }
    header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.post(url, auth=JIRA_AUTH, data=json.dumps(payload), headers=header)
    print(response.text)
    response_json = response.json()
    return response_json
