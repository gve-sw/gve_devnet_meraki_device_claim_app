# !/usr/bin/env python3
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

__author__ = "Simon Fang <sifang@cisco.com>"
__copyright__ = "Copyright (c) 2022 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

from flask import Flask, render_template, request
from dotenv import load_dotenv
import json, os
import requests

load_dotenv()

########################
### Global variables ###
########################

base_url = "https://api.meraki.com/api/v1"
api_key = os.getenv("API_KEY")

selected_organization = []
selected_network = []
claim_device_response = []

app = Flask(__name__)

########################
### Helper Functions ###
########################


def get_header():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": api_key
    }
    print(api_key)
    return headers

def get_organizations():
    url = f"{base_url}/organizations"
    payload = None
    response = requests.request('GET', url, headers=get_header(), data=payload)
    return response.json()


def get_networks(organization_id):
    url = f"{base_url}/organizations/{organization_id}/networks"
    payload = None
    response = requests.request('GET', url, headers=get_header(), data=payload)
    return response.json()


def claim_network_device(network_id, serial_number):
    """
    Claim devices into a network: https://developer.cisco.com/meraki/api/#!claim-network-devices
    """
    url = f"{base_url}/networks/{network_id}/devices/claim"
    payload = {
        "serials": [ serial_number ]
    }
    response = requests.post(url, headers=get_header(), data=json.dumps(payload))
    return response



##############
### Routes ###
##############

# Claim Device page
@app.route('/', methods=['GET'])
def claim_device_main():
    global organizations
    organizations = get_organizations()
    return render_template('claim_device.html', organizations=organizations, selected_organization=selected_organization, selected_network=selected_network, claim_device_response=claim_device_response)

# Claim Device page: select organization and network
@app.route('/select_organization_network_claim_device', methods=['POST'])
def select_organization_network_claim_device():
    global organizations
    global selected_organization
    global selected_network
    global networks

    if request.method == 'POST':
        form_data = request.form
        organization_id = form_data['organization_id']

        for organization in organizations:
            if organization_id == organization['id']:
                selected_organization = organization 

        networks = get_networks(organization_id)
        
        if 'network_id' in form_data:
            network_id = form_data['network_id']

            for network in networks:
                if network_id == network['id']:
                    selected_network = network 

            return render_template('claim_device.html', organizations=organizations, networks=networks,
                                   selected_organization=selected_organization,
                                   selected_network=selected_network, claim_device_response=claim_device_response)

    return render_template('claim_device.html', organizations = organizations, networks = networks, selected_organization = selected_organization,
         selected_network = selected_network, claim_device_response=claim_device_response)

# Claim device page: submit serial and claim device
@app.route('/submit_serial', methods=['POST'])
def submit_serial():
    global organizations
    global selected_organization
    global selected_network
    global networks

    if request.method == 'POST':
        form_data = request.form
        serial_number = form_data['serial_number']
        print(serial_number)

        claim_device_response = claim_network_device(selected_network['id'], serial_number)

        if claim_device_response.ok:
            claim_device_response = {'serial_number': serial_number}
        else:
            claim_device_response = claim_device_response.json()

        return render_template('claim_device.html', organizations=organizations, networks=networks,
                                   selected_organization=selected_organization,
                                   selected_network=selected_network, claim_device_response=claim_device_response)
                            
    return render_template('claim_device.html', organizations = organizations, networks = networks, selected_organization = selected_organization,
         selected_network = selected_network, claim_device_response=claim_device_response)

if __name__ == '__main__':

    # app.run()
    app.run(host='127.0.0.1', port=8080, debug=False)
