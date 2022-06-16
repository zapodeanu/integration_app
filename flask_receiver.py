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

import datetime
import json
import os
import time

import urllib3
from dotenv import load_dotenv
from flask import Flask, request, abort, send_from_directory
from flask_basicauth import BasicAuth
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

import jira_apis
from config import DNAC_URL
from config import JIRA_EMAIL, JIRA_PROJECT

os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

app = Flask(__name__)


load_dotenv('environment.env')

JIRA_API_KEY = os.getenv('JIRA_API_KEY')
WEBHOOK_USERNAME = os.getenv('WEBHOOK_USERNAME')
WEBHOOK_PASSWORD = os.getenv('WEBHOOK_PASSWORD')

app.config['BASIC_AUTH_USERNAME'] = WEBHOOK_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = WEBHOOK_PASSWORD
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)


@app.route('/')  # create a page for testing the flask framework
@basic_auth.required
def index():
    return '<h1>Flask Receiver App is Up!</h1>', 200


@app.route('/detailed_logs', methods=['GET'])  # API to return detailed webhook logged file
@basic_auth.required
def detailed_logs():
    print('File all_webhooks_detailed.log requested, transfer started')
    return send_from_directory('', 'all_webhooks_detailed.log', as_attachment=True)


@app.route('/webhook', methods=['POST'])  # create a route for /webhook, method POST
@basic_auth.required
def webhook():
    if request.method == 'POST':
        print('Webhook Received')
        request_json = request.json

        # print the received notification
        print('Payload: ')

        # save as a file, create new file if not existing, append to existing file, full details of each notification
        with open('all_webhooks_detailed.log', 'a') as filehandle:
            filehandle.write('%s\n' % json.dumps(request_json))
        try:
            if 'NETWORK-' in request_json['eventId']:  # this will select the Cisco DNA Center notifications
                dnac_notification = request_json

                # save all info to variables, prepare to save to file
                severity = str(dnac_notification['severity'])
                category = dnac_notification['category']
                timestamp = str(datetime.datetime.fromtimestamp(int(dnac_notification['timestamp'] / 1000)).strftime(
                    '%Y-%m-%d %H:%M:%S'))
                issue_name = dnac_notification['details']['Assurance Issue Name']
                issue_description = dnac_notification['details']['Assurance Issue Details']
                issue_status = dnac_notification['details']['Assurance Issue Status']
                url = DNAC_URL + '/dna/assurance/issueDetails?issueId=' + dnac_notification['instanceId']

                # create the summary DNAC log
                new_info = {'severity': severity, 'category': category, 'timestamp': dnac_notification['timestamp']}
                new_info.update({'Assurance Issue Name': issue_name, 'Assurance Issue Details': issue_description})
                new_info.update({'Assurance Issue Status': issue_status, 'Assurance Issue URL': url})

                # append, or create, the dnac_webhooks.log - Cisco DNA C summary logs
                with open('dnac_webhooks.log', 'a') as filehandle:
                    filehandle.write('%s\n' % json.dumps(new_info))

                # append, or create, the all_webhooks.log - Summary all logs
                with open('all_webhooks.log', 'a') as filehandle:
                    filehandle.write('%s\n' % json.dumps(new_info))

                # create Jira Issue
                jira_project = JIRA_PROJECT
                jira_component = '10016'  # Component id for Cisco DNA Center Notification, as created in Jira
                jira_apis.create_customer_issue(jira_project, jira_component, issue_name, issue_description, severity,
                                                JIRA_EMAIL)
        finally:
            pass

        return {'response': 'Notification Received'}, 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, ssl_context='adhoc')
