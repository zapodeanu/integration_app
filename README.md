# Cisco DNA Center Webhook Receiver


This Python script will run on PythonAnywhere, or a Linux container.

 - It will receive Cisco DNA Center webhooks and save them locally to files for reporting
 - It will open a new Jira Service Desk Customer Issue


**Cisco Products & Services:**

- Cisco DNA Center

**Other Products & Services:**

- Jira Service Desk (production or developer instance)
 
**Tools & Frameworks:**

- Python environment running in PythonAnywhere, local, or VM/container

**Usage**

- Update the "config.py" and "environment.env" files with your environment
- Configure a new Cisco DNA Center webhook
- Create a new event to which you subscribed and verify the notifications
- Retrieve the new created ticket in Jira Service Desk

**License**

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).
