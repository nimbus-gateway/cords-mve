import requests
from requests.auth import HTTPBasicAuth
import pytest
import subprocess

# Assume SERVICE_A_URL, SERVICE_B_URL, and SERVICE_C_URL are set in the environment
import os

RESOURCE_MANAGER_URL = "http://localhost:5000"
SELF_DESC_URL = "https://localhost:8090"
PROXY_ENDPOINT = "https://localhost:8184/proxy"
# Paths to Docker Compose files and project
DOCKER_COMPOSE_FILE = 'docker-compose.yml'
DOCKER_COMPOSE_PROJECT_NAME = 'CORDS-MVE'



def test_policy_role_approve():
    # 1. Trigger a request to Service A
    username = "tharindu.prf@gmail.com"
    password = "password123"

    response = requests.post("{0}/api/users/get-auth-token".format(RESOURCE_MANAGER_URL), auth=HTTPBasicAuth(username, password))
    assert response.status_code == 200

    # 2. Validate Service A response and interaction with Service B
    data = response.json()
    assert "token" in data


    token = data['token']

    headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"  # Adjust content type as necessary
    }

    # Data to send in the POST request
    payload = {
        "name": "TestModel222",
        "version": "1.0",
        "description": "This model is a test model",
        "ml_flow_model_path": "mlflow-artifacts:/208444466607110357/6a7cf4d3ba1b47b3b3abf32b06abf6c6/artifacts/knnmodel"
    }
    # Sending the POST request
    response = requests.post("{0}/api/ml_models/add_model".format(RESOURCE_MANAGER_URL), headers=headers, json=payload)

    assert response.status_code == 201

    data = response.json()
    model_id = data['model_id']


    payload = {
        "connector_id": "https://w3id.org/engrd/connector/provider21",
        "asset_id": "{0}".format(model_id),
        "type": "model"
    }
    
    response = requests.post("{0}/api/dataspace_resource/create_resource".format(RESOURCE_MANAGER_URL), headers=headers, json=payload)

    assert response.status_code == 201

    data = response.json()
    resource_id = data['resource_id']

    # Create payload 

    payload = {
       "resource_id": resource_id,
       "policy_type": "EVALUATION_TIME",
       "policy_metadata": {
            "BEFORE": "2025-08-24T12:17:37Z",
            "AFTER": "2022-06-17T12:17:37Z"
        }
    }


    response = requests.post("{0}/api/policy/add_policy".format(RESOURCE_MANAGER_URL), headers=headers, json=payload)

    assert response.status_code == 201


    # Create resource description

    payload = {
        "title": "Example IDS Resource1",
        "description": "This is an example IDS Resource",
        "keywords": ["cords", "energy prediction"]
    }


    response = requests.post("{0}/api/dataspace_resource/create_resource_description/{1}".format(RESOURCE_MANAGER_URL, resource_id), headers=headers, json=payload)

    assert response.status_code == 200

    data = response.json()

    # Get Self Description
    response = requests.get("{0}/api/selfDescription/".format(SELF_DESC_URL), auth=HTTPBasicAuth('apiUser', 'password'), verify=False)

    assert response.status_code == 200

    self_description = response.json()
    catalog = self_description["ids:resourceCatalog"][0]["@id"]

    headers = {
        "Content-Type": "application/json",
        "catalog": catalog
    }

    payload = data["resource_description"]

    response = requests.post("{0}/api/offeredResource/".format(SELF_DESC_URL), auth=HTTPBasicAuth('apiUser', 'password'), verify=False, headers=headers, json=payload)


    # contract negotiation

    ## description request
    payload = {
        "multipart": "form",
        "Forward-To": "https://ecc-provider:8889/data",
        "messageType": "DescriptionRequestMessage"
    }

    response = requests.post("{0}".format(PROXY_ENDPOINT), auth=HTTPBasicAuth('idsUser', 'password'), verify=False, headers=headers, json=payload)


    assert response.status_code == 200

    target_id = "http://w3id.org/engrd/connector/artifact/{0}".format(resource_id)
    json_data = response.json()
    array = json_data["ids:resourceCatalog"][0]["ids:offeredResource"]

    result = next(
        (
            obj
            for obj in array
            if obj["ids:contractOffer"][0]["ids:permission"][0]["ids:target"]["@id"] == target_id
        ),
        None
    )

    offered_resource = result["@id"]

    ## Offered resource description

    payload = {
        "multipart": "form",
        "Forward-To": "https://ecc-provider:8889/data",
        "messageType": "DescriptionRequestMessage",
        "requestedElement": offered_resource
    }

    response = requests.post("{0}".format(PROXY_ENDPOINT), auth=HTTPBasicAuth('idsUser', 'password'), verify=False, headers=headers, json=payload)

    assert response.status_code == 200

    json_data = response.json()
    contract_artifact = json_data["ids:representation"][0]["ids:instance"][0]["@id"]
    contract_id = json_data["ids:contractOffer"][0]["@id"]
    contract_permission= json_data["ids:contractOffer"][0]["ids:permission"][0]
    contract_provider = json_data["ids:contractOffer"][0]["ids:provider"]["@id"]


    ## Contract Request

    print("offered resource = " + offered_resource)

    payload = {
        "multipart": "form",
        "Forward-To": "https://ecc-provider:8889/data",
        "messageType": "ContractRequestMessage",
        "requestedElement": target_id,
        "payload": {
            "@context": {
                "ids": "https://w3id.org/idsa/core/",
                "idsc": "https://w3id.org/idsa/code/"
            },
            "@type": "ids:ContractRequest",
            "@id": contract_id,
            "ids:permission": [
                contract_permission
            ],
            "ids:provider": {
                "@id": contract_provider
            },
            "ids:obligation": [],
            "ids:prohibition": [],
            "ids:consumer": {
                "@id": "http://w3id.org/engrd/connector/consumer"
            }
        }
    }


    response = requests.post("{0}".format(PROXY_ENDPOINT), auth=HTTPBasicAuth('idsUser', 'password'), verify=False, headers=headers, json=payload)
    assert response.status_code == 200

    contract_agreement = response.json()
    transfer_contract = contract_agreement["@id"]

    print("contract === ")
    print(contract_agreement)
    
    ## Contract Agreement

    payload = {
        "multipart": "form",
        "Forward-To": "https://ecc-provider:8889/data",
        "messageType": "ContractAgreementMessage",
        "requestedArtifact": target_id,
        "payload": contract_agreement
    }

    response = requests.post("{0}".format(PROXY_ENDPOINT), auth=HTTPBasicAuth('idsUser', 'password'), verify=False, headers=headers, json=payload)
    assert response.status_code == 200

    assert response.content == b'MessageProcessedNotificationMessage'

    ## Artifact Request 
    print("transfer_contract====")
    print(transfer_contract)

    payload = {
        "multipart": "form",
        "Forward-To": "https://ecc-provider:8889/data",
        "messageType": "ArtifactRequestMessage",
        "requestedArtifact": target_id,
        "transferContract": transfer_contract,
        "payload" : {
            "consumer_ip": "model-receiver",
            "consumer_port": "8765"
        }
    }


    print("Final Payload ===")
    print(payload)

    response = requests.post("{0}".format(PROXY_ENDPOINT), auth=HTTPBasicAuth('idsUser', 'password'), verify=False, headers=headers, json=payload)


    assert response.status_code == 200


   

    


def test_policy_role_reject():
    # 1. Trigger a request to Service A
    username = "tharindu.prf@gmail.com"
    password = "password123"

    response = requests.post("{0}/api/users/get-auth-token".format(RESOURCE_MANAGER_URL), auth=HTTPBasicAuth(username, password))
    assert response.status_code == 200

    # 2. Validate Service A response and interaction with Service B
    data = response.json()
    assert "token" in data


    token = data['token']

    headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"  # Adjust content type as necessary
    }

    # Data to send in the POST request
    payload = {
        "name": "TestModel222",
        "version": "1.0",
        "description": "This model is a test model",
        "ml_flow_model_path": "mlflow-artifacts:/208444466607110357/6a7cf4d3ba1b47b3b3abf32b06abf6c6/artifacts/knnmodel"
    }
    # Sending the POST request
    response = requests.post("{0}/api/ml_models/add_model".format(RESOURCE_MANAGER_URL), headers=headers, json=payload)

    assert response.status_code == 201

    data = response.json()
    model_id = data['model_id']


    payload = {
        "connector_id": "https://w3id.org/engrd/connector/provider21",
        "asset_id": "{0}".format(model_id),
        "type": "model"
    }
    
    response = requests.post("{0}/api/dataspace_resource/create_resource".format(RESOURCE_MANAGER_URL), headers=headers, json=payload)

    assert response.status_code == 201

    data = response.json()
    resource_id = data['resource_id']

    # Create payload 

    payload = {
       "resource_id": resource_id,
       "policy_type": "EVALUATION_TIME",
       "policy_metadata": {
            "BEFORE": "2023-08-24T12:17:37Z",
            "AFTER": "2022-06-17T12:17:37Z"
        }
    }


    response = requests.post("{0}/api/policy/add_policy".format(RESOURCE_MANAGER_URL), headers=headers, json=payload)

    assert response.status_code == 201


    # Create resource description

    payload = {
        "title": "Example IDS Resource1",
        "description": "This is an example IDS Resource",
        "keywords": ["cords", "energy prediction"]
    }


    response = requests.post("{0}/api/dataspace_resource/create_resource_description/{1}".format(RESOURCE_MANAGER_URL, resource_id), headers=headers, json=payload)

    assert response.status_code == 200

    data = response.json()

    # Get Self Description
    response = requests.get("{0}/api/selfDescription/".format(SELF_DESC_URL), auth=HTTPBasicAuth('apiUser', 'password'), verify=False)

    assert response.status_code == 200

    self_description = response.json()
    catalog = self_description["ids:resourceCatalog"][0]["@id"]

    headers = {
        "Content-Type": "application/json",
        "catalog": catalog
    }

    payload = data["resource_description"]

    response = requests.post("{0}/api/offeredResource/".format(SELF_DESC_URL), auth=HTTPBasicAuth('apiUser', 'password'), verify=False, headers=headers, json=payload)


    # contract negotiation

    ## description request
    payload = {
        "multipart": "form",
        "Forward-To": "https://ecc-provider:8889/data",
        "messageType": "DescriptionRequestMessage"
    }

    response = requests.post("{0}".format(PROXY_ENDPOINT), auth=HTTPBasicAuth('idsUser', 'password'), verify=False, headers=headers, json=payload)


    assert response.status_code == 200

    target_id = "http://w3id.org/engrd/connector/artifact/{0}".format(resource_id)
    json_data = response.json()
    array = json_data["ids:resourceCatalog"][0]["ids:offeredResource"]

    result = next(
        (
            obj
            for obj in array
            if obj["ids:contractOffer"][0]["ids:permission"][0]["ids:target"]["@id"] == target_id
        ),
        None
    )

    offered_resource = result["@id"]

    ## Offered resource description

    payload = {
        "multipart": "form",
        "Forward-To": "https://ecc-provider:8889/data",
        "messageType": "DescriptionRequestMessage",
        "requestedElement": offered_resource
    }

    response = requests.post("{0}".format(PROXY_ENDPOINT), auth=HTTPBasicAuth('idsUser', 'password'), verify=False, headers=headers, json=payload)

    assert response.status_code == 200

    json_data = response.json()
    contract_artifact = json_data["ids:representation"][0]["ids:instance"][0]["@id"]
    contract_id = json_data["ids:contractOffer"][0]["@id"]
    contract_permission= json_data["ids:contractOffer"][0]["ids:permission"][0]
    contract_provider = json_data["ids:contractOffer"][0]["ids:provider"]["@id"]


    ## Contract Request

    print("offered resource = " + offered_resource)

    payload = {
        "multipart": "form",
        "Forward-To": "https://ecc-provider:8889/data",
        "messageType": "ContractRequestMessage",
        "requestedElement": target_id,
        "payload": {
            "@context": {
                "ids": "https://w3id.org/idsa/core/",
                "idsc": "https://w3id.org/idsa/code/"
            },
            "@type": "ids:ContractRequest",
            "@id": contract_id,
            "ids:permission": [
                contract_permission
            ],
            "ids:provider": {
                "@id": contract_provider
            },
            "ids:obligation": [],
            "ids:prohibition": [],
            "ids:consumer": {
                "@id": "http://w3id.org/engrd/connector/consumer"
            }
        }
    }


    response = requests.post("{0}".format(PROXY_ENDPOINT), auth=HTTPBasicAuth('idsUser', 'password'), verify=False, headers=headers, json=payload)
    assert response.status_code == 200

    contract_agreement = response.json()
    transfer_contract = contract_agreement["@id"]

    print("contract === ")
    print(contract_agreement)
    
    ## Contract Agreement

    payload = {
        "multipart": "form",
        "Forward-To": "https://ecc-provider:8889/data",
        "messageType": "ContractAgreementMessage",
        "requestedArtifact": target_id,
        "payload": contract_agreement
    }

    response = requests.post("{0}".format(PROXY_ENDPOINT), auth=HTTPBasicAuth('idsUser', 'password'), verify=False, headers=headers, json=payload)
    assert response.status_code == 200

    assert response.content == b'MessageProcessedNotificationMessage'

    ## Artifact Request 
    print("transfer_contract====")
    print(transfer_contract)

    payload = {
        "multipart": "form",
        "Forward-To": "https://ecc-provider:8889/data",
        "messageType": "ArtifactRequestMessage",
        "requestedArtifact": target_id,
        "transferContract": transfer_contract,
        "payload" : {
            "consumer_ip": "model-receiver",
            "consumer_port": "8765"
        }
    }


    print("Final Payload ===")
    print(payload)


    response = requests.post("{0}".format(PROXY_ENDPOINT), auth=HTTPBasicAuth('idsUser', 'password'), verify=False, headers=headers, json=payload)


    assert response.status_code == 401


