# CORDS Minimum Viable Data Space

CORDS MVDS has several components. These components can be downloaded as docker images to the deployment. 

* [True Connector Components](https://github.com/Engineering-Research-and-Development/true-connector), open-source IDSA Connector designed by ENG. It is leveraged in CORDS MVE for ensuring IDSA complaint artifact exchange. It consist of several services including Execution Core Container (ECC) and Usage-Control (UC) Data Application.

* [CORDS Back End Data App](https://github.com/nimbus-gateway/cords-data-app), A modified version of the ENG Basic Data App to taylor to address the requirments of CORDS. It act as the midleware between the CORDS local and global digital threads.

* [Meta Data Broker](https://github.com/International-Data-Spaces-Association/metadata-broker-open-core), Implementation of an IDS Metadata Broker, which is a registry for IDS Connector self-description documents. It is currenly under development by the IDSA community. 

* [CORDS Resource Manager](https://github.com/nimbus-gateway/cords-resource-manager), It is an API provided to manage artifiact from the ML Flow and genearate their semantic descriptions. Furthermore it can be used to push artifacts into the IDS connector ecosystem. 

* [MLFlow](https://github.com/mlflow/mlflow), Open source platform for the machine learning lifecycle. It can be used to manage the ML workflows and manage the artifacts geneated from every training rounds.  



![MVE](pictures/minimum_viable_ecosystem.png "MVE")

## Index
- [Hardware Requirements](https://github.com/nimbus-gateway/cords-mve/blob/master/README.md#hardware-requirements)
- [Runing Precondifured MVE](https://github.com/nimbus-gateway/cords-mve/blob/master/README.md#running-preconfigured-mve)
- [Exploring CORDS MVE](https://github.com/nimbus-gateway/cords-mve/blob/master/README.md#exploring-cords-mve)
<!-- - [Certificate Authority](https://github.com/Engineering-Research-and-Development/true-connector-mvds/blob/master/README.md#certificate-authority)
- [DAPS](https://github.com/Engineering-Research-and-Development/true-connector-mvds/blob/master/README.md#daps)
- [TRUE Connector](https://github.com/Engineering-Research-and-Development/true-connector-mvds/blob/master/README.md#true-connector)
- [Metadata Broker](https://github.com/Engineering-Research-and-Development/true-connector-mvds/blob/master/README.md#metadata-broker)
- [Stop and delete TRUEConnector-MVDS set up](https://github.com/Engineering-Research-and-Development/true-connector-mvds/blob/master/README.md#stopping-the-TRUEConnector-MVDS) -->

The installation and configuration process is explained below for each of the components. 


# Hardware Requirements

In this section the minimum requirements required for operating the TRUEConnector-MVDS are detailed.

The current minimum requirements for the TRUEConnector-MVDS are:
- 4 GB RAM (however 8GB RAM is recommended)
- 50 GB storage

It is recommended to use 64bit quad core processor to provide enough processing power for all docker containers.

Take into account that if more components are included at the TRUEConnector-MVDS or a huge amount of data is uploaded it is possible to run out of disk free space. In this cases it is recommended to provide more free disk storage.

# Running Preconfigured MVE
The CORDS MVE is already preconfigured out-of-the-box for testing purposes and you can start it by executing in the root folder where the docker-compose.yml is located:

```
docker-compose up -d
```

To see the log lines:

```
docker-compose logs -f
```

# Exploring CORDS MVE

## ML Flow 
ML Flow UI can be access from you browser [http://localhost:4000/](http://localhost:4000/). This can be used to track your assets in ML experiments. [CORDS semantic library](https://github.com/nimbus-gateway/cords-semantics-lib) can be utilized to describe your ML assets using the CORDS ontology. This will ensure the semantic interoprability of ML assets that you will share on the data space. An example for connecting into the MLFLow and using semantic lib is given below. 


```
#for setting up mlflow local server
mlflow.set_tracking_uri('http://localhost:4000')

mlflow.set_experiment("energy-prediction-regression-problem")

#Importing CORDS Tags
import cords_semantics.tags as cords_tags



with mlflow.start_run(run_name = run_name) as mlflow_run:
    mlflow_run_id = mlflow_run.info.run_id
    
    mlflow.set_experiment_tag("second best_model", "K-NeighborsRegressor")
    mlflow.set_tag("tag2", "K-NeighborsRegressor")
    mlflow.set_tag(cords_tags.CORDS_RUN, mlflow_run_id)
    mlflow.set_tag(cords_tags.CORDS_RUN_EXECUTES, "K-NeighborsRegressor")
    mlflow.set_tag(cords_tags.CORDS_IMPLEMENTATION, "python")
    mlflow.set_tag(cords_tags.CORDS_SOFTWARE, "sklearn")
    
    mlflow.sklearn.log_model(models['K-Neighbors Regressor'], "knnmodel")
        
    mlflow.log_metric("test_RMSE", rmse_scores.loc[rmse_scores['Model Name'] == 'K-Neighbors Regressor', 'RMSE_Score'].values[0])
    mlflow.log_metric("test_MAE", mae_scores.loc[mae_scores['Model Name'] == 'K-Neighbors Regressor', 'MAE_Score'].values[0])
    mlflow.log_metric("test_R2_Score", r2_scores.loc[r2_scores['Model Name'] == 'K-Neighbors Regressor', 'R2_Score'].values[0])   
    
    mlflow.log_input(dataset, context="training")
    
    
    print("MLFlow Run ID: ", mlflow_run_id)

```

## CORDS Resource Manager
This API allows the user to prepare the assets to be shared on the Data Space using IDS connectors. It has a feature to extract metadata from MLFlow and convert to a IDS compatible resource description. Finally, when the contract negotation is done ML asset trasfer can be initiated from the API. Once this service is started the API documentation can be accessed from [http://localhost:5000/docs](http://localhost:5000/docs). Use the Resource Manager [Postman Collection](https://github.com/nimbus-gateway/cords-mve/blob/main/CORDS_Resource_Manager_postman_collection.json) to interact with the API.


### 1. Registering a new user for managing ML assets at the provider end.

```
curl -X POST http://localhost:5000/api/users/register \
-H "Content-Type: application/json" \
-H "User-Agent: PostmanRuntime/7.39.0" \
-H "Accept: */*" \
-H "Cache-Control: no-cache" \
-H "Host: localhost:5000" \
-H "Accept-Encoding: gzip, deflate, br" \
-d '{
    "email": "tharindu.prf@gmail.com",
    "password": "password123",
    "first_name": "Tharindu",
    "last_name": "Ranathunga",
    "role": "ML Engineer"
}'
```

### 2. Get auth token to authenticte the other API calls. 

The base64 encorded user name password is added as the header here. 

```
curl -X POST http://localhost:5000/api/users/get-auth-token \
  -H 'Authorization: Basic dGhhcmluZHUucHJmQGdtYWlsLmNvbTpwYXNzd29yZDEyMw==' \
  -H 'User-Agent: PostmanRuntime/7.39.0' \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Host: localhost:5000' \
  -H 'Accept-Encoding: gzip, deflate, br' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 0'
```
Use the response token of this call to authenticate other calls.

### 3. Register a ML Model as an asset to be shared in the data space. 

More details about the request body can be found in the [API doc](http://localhost:5000/docs) 

```
curl -X POST http://localhost:5000/api/ml_models/add_model \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer LNUDU7YPEeYPcXPXqZPF8jDEiFrVnFmwLTbwYwzxrF8' \
  -H 'User-Agent: PostmanRuntime/7.39.0' \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Host: localhost:5000' \
  -H 'Accept-Encoding: gzip, deflate, br' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 224' \
  -d '{
    "name": "Test Model 1",
    "version": "1.0",
    "description": "This model is a test model",
    "ml_flow_model_path": "mlflow-artifacts:/208444466607110357/2c8c2fc3fefe4c56a29ac325c0bac39c/artifacts/knnmodel"
}'
```

### 4. Register a data space connector for sharing assets
```
curl -X POST http://localhost:5000/api/dataspace_connector/add_connector \
  -H 'Content-Type: application/json' \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Accept-Encoding: gzip, deflate, br' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 504' \
  -d '{
    "id": "https://w3id.org/engrd/connector/provider21",
    "name": "CORDS True Connector",
    "type": "ids:BaseConnector",
    "description": "Data Provider Connector description",
    "public_key": "TUlJREdqQ0NBcCtnQXdJQkFnSUJBVEFLQmdncWhrak9QUVFEQWpCTk1Rc3dDUVlEVlFRR0V3SkZVekVNTUFvR0ExVUVDZ3dEVTFGVE1SQXdEZ1lEVlFRTERBZFVaWE4wVEdGaU1SNHdIQVlEVlFRRERCVlNaV1psY21WdVkyVlVaWE4wWW1Wa1U=",
    "access_url": "https://89.19.88.88:8449/",
    "reverse_proxy_url": "https://localhost:8184/proxy"
}'
```


### 4. Creating a resource to be shared in data space. 

This could be a ML model, Raw Data Dump or a Federated Learning Training (Refered by the asset_id). In this version only ML models are supported to be registered as a resource.
This also link to the prefered data space connector that the resource will be shared. 

```
curl -X POST http://localhost:5000/api/dataspace_resource/create_resource \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer LNUDU7YPEeYPcXPXqZPF8jDEiFrVnFmwLTbwYwzxrF8' \
  -H 'User-Agent: PostmanRuntime/7.39.0' \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Host: localhost:5000' \
  -H 'Accept-Encoding: gzip, deflate, br' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 224' \
  -d '{
    "asset_id": "344f0e124bfb7363651bb080c3ca36f43a23094ab6566e1943f7592b7ff620e9",
    "connector_id": "https://w3id.org/engrd/connector/provider21",
    "resource_id": "1b2888f8c6032ee0223373cab9c62380f594e22435170b9cad8a62769d8810ea",
    "timestamp": "2024-05-31T13:37:55.708378",
    "type": "model"
}'
```



### 5. Register the resource on IDS Connector.

This will create the resource description using the IDS Information model. Moreover, metadata of the shared resource (Eg: ML semantics) are embeded to the resource description using the CORDS ontology.  

```
curl -X POST http://localhost:5000/api/dataspace_connector/register_resource/1b2888f8c6032ee0223373cab9c62380f594e22435170b9cad8a62769d8810ea \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer LNUDU7YPEeYPcXPXqZPF8jDEiFrVnFmwLTbwYwzxrF8' \
  -H 'User-Agent: PostmanRuntime/7.39.0' \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Host: localhost:5000' \
  -H 'Accept-Encoding: gzip, deflate, br' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 224' \
  -d '{
    "title": "Example IDS Resource1",
    "description": "This is an example IDS Resource",
    "keywords": ["cords", "energy prediction"],
    "catalog_id": "https://w3id.org/idsa/autogen/resourceCatalog/1ce75044-fd7d-4002-9117-051c7005f4ba"
}'
```



## Data Space Connectors 
Use the [Rest API](https://github.com/Engineering-Research-and-Development/true-connector/blob/main/doc/rest_api/REST_API.md) provided by the True Connector to interact with the IDS components. This can be used to perform the contract negotation and initiate the asset transfer. Once the contract negoting is done following API call at the consumer connector can be invoked to initate the model transfer. This is a True Connector specific API call. 

```
curl -X POST https://localhost:8184/proxy \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Basic aWRzVXNlcjpwYXNzd29yZA==' \
  -H 'User-Agent: PostmanRuntime/7.39.0' \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Postman-Token: a22a80b8-f11a-4a0f-8037-258eb4cb3df5' \
  -H 'Host: localhost:8184' \
  -H 'Accept-Encoding: gzip, deflate, br' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 463' \
  -d '{
    "multipart": "form",
    "Forward-To": "https://ecc-provider:8889/data",
    "messageType": "ArtifactRequestMessage",
    "requestedArtifact": "http://w3id.org/engrd/connector/artifact/8f840986c277d47f3535d47f0d3bdb1652cd988baa55df788deb253f20f2d974",
    "transferContract": "https://w3id.org/idsa/autogen/contractAgreement/65c27aa7-d334-4469-9ad0-e491f512a75b",
    "payload" : {
        "consumer_ip": "127.0.0.1",
        "consumer_port": "8765"
    }
}'
```

<!-- 
Follow this set up of the TRUEConnector-MVDS to configure it to your needs.

# CERTIFICATE AUTHORITY
These certificates are for the omejdn DAPS, for TLS certificates please see [TRUE Connector configuration](#true-connector-configuration).

Move to right directory, and make the files executable in CertificateAuthority.

The official documentation will cover the scope, dependencies and usage of the component.

Official documentation: [CertificateAuthority/README.md](./CertificateAuthority/README.md)

The preconfigured setup includes certificates for:
* a root CA called "ReferenceTestbedCA"
* a subCA called "ReferenceTestbedSubCA" and
* certificates for devices called "testbed1", ... , "testbed4"

## Continue here after the official documentation has been followed

The Certificate Authority provides {CERT_FILENAME}.crt and {CERT_FILENAME}.key formats. Keep in mind that other formats will be required for the different components. Those have to be created.

Now convert the generated certificates in `data/cert` using openssl to then use in the Connector and DAPS.

```
## navigate to the following directory data/cert
cd data/cert
ls
```
The output should look similar to
```
{CERT_FILENAME}.crt  {CERT_FILENAME}.key
```
Obtain a `.p12` file format from the current `.crt` and `.key` formats:
```
## .crt + .key -> .p12
openssl pkcs12 -export -out {CERT_FILENAME}.p12 -inkey {CERT_FILENAME}.key -in {CERT_FILENAME}.crt -passout pass:password
## .p12 -> .cert
openssl pkcs12 -in {CERT_FILENAME}.p12 -out {CERT_FILENAME}.cert -nokeys -nodes -passin pass:password

```

You should now have two additional files in data/cert

```
{CERT_FILENAME}.cert  {CERT_FILENAME}.crt  {CERT_FILENAME}.key  {CERT_FILENAME}.p12
```

The certificate chain (CA, SubCA, Certs) has been created and the user should be able to create as many certificates as they need for their environment.

# DAPS

The official documentation of the Omejdn DAPS is here: https://github.com/International-Data-Spaces-Association/omejdn-daps

## Adding the keys to the DAPS

Every client that wants to use the local Omejdn DAPS must place their `{CERTFILE}.cert` file in the `keys` directory.

The directory can be found in

```
DAPS/keys
```

Add the certificate provided by the local CA, newly created by the local CA or provided by a third party CA. Place the certificate at the folder `DAPS/keys/omejdn/` with name `omejdn.key` to avoid dependency issues later on.

## Adding the clients to the DAPS

**Note:** The user must execute the `register_connector.sh` file in order to add the client to the Omejdn DAPS. Once executed, the certificate will be included in the DAPS's list of clients.

To execute the script

```
cd DAPS
./register_connector.sh {CERT_FILENAME} 
```

It could look something like this
```
./register_connector.sh testbed1
```

The certificate will be added to the list of DAPS's clients. You can check it at the file `DAPS/config/clients.yml`

## Required changes in the configuration

Change the configuration file `.env` with your favorite editor, e.g. `nano`.

```
nano .env
```

**Note** The file could be hidden. Select the option `show hidden files` and it should be placed at TRUEConnector-MVDS root directory.

Replace the following lines with the necessary configuration. It could look something like this

```
COMPOSE_PROJECT_NAME=testbed
OMEJDN_ENVIRONMENT="production"
OMEJDN_PROTOCOL="https"
OMEJDN_VERSION="1.6.0"
OMEJDN_DOMAIN="omejdn"
OMEJDN_PATH="/auth"

ADMIN_USERNAME="admin"
ADMIN_PASSWORD="password"

TLS_KEY="${PWD}/DAPS/keys/TLS/daps.key"
TLS_CERT="${PWD}/DAPS/keys/TLS/daps.cert"
```

Configure the `docker-compose.yml` file with your configuration. Then run the Omejdn DAPS server.

The `docker-compose.yml` could look something like this

```
services

  omejdn:
    image: nginx:1.21.6
    container_name: omejdn
    ports:
      - 80:80
      - 443:443      
    environment:
      - OMEJDN_DOMAIN=${OMEJDN_DOMAIN}
      - OMEJDN_PATH=${OMEJDN_PATH}
      - UI_PATH=${UI_PATH}
    volumes:
      - ./DAPS/nginx.conf:/etc/nginx/templates/default.conf.template
      - ./DAPS/keys/TLS/daps.cert:/etc/nginx/daps.cert
      - ./DAPS/keys/TLS/daps.key:/etc/nginx/daps.key
    networks:
      - local

  omejdn-server:
    image: ghcr.io/fraunhofer-aisec/omejdn-server:${OMEJDN_VERSION}
    container_name: omejdn-server
    environment:
      - OMEJDN_ISSUER=${OMEJDN_ISSUER}
      - OMEJDN_FRONT_URL=${OMEJDN_ISSUER}
      - OMEJDN_OPENID=true
      - OMEJDN_ENVIRONMENT=${OMEJDN_ENVIRONMENT}
      - OMEJDN_ACCEPT_AUDIENCE=idsc:IDS_CONNECTORS_ALL
      - OMEJDN_DEFAULT_AUDIENCE=idsc:IDS_CONNECTORS_ALL
      - OMEJDN_ADMIN=${ADMIN_USERNAME}:${ADMIN_PASSWORD}
    volumes:
      - ./DAPS/config:/opt/config
      - ./DAPS/keys:/opt/keys
    networks:
      - local
      
networks:
  local:
    driver: bridge
```

Place the local CA created certificate at the folder `DAPS/keys/TLS/` and name it as `daps.crt` and `daps.key` to match the above mentioned `docker-compose.yml` file configuration.

# TRUE CONNECTOR

The TRUEConnector-MVDS will have two built-in Connectors which are already preconfigured and ready out-of-the-box. To tailor the TRUE Connector setup to your needs follow the next steps.

For a deep dive in to the TRUE Connector see [here](https://github.com/Engineering-Research-and-Development/true-connector/tree/v1.0.1)

## Generate DAPS certificate using Omejdn DAPS

This step is not mandatory, since the TRUEConnector-MVDS comes with some generated certificates which can be used temporarily. These are for the omejdn DAPS, for TLS certificates please see [TRUE Connector configuration](#true-connector-configuration).

If you want to create new certificate, please follow [instructions](https://github.com/Engineering-Research-and-Development/true-connector-mvds/tree/master/CertificateAuthority/README.md) on how to achieve this.


## DAPS certificate

You can use certificate already provided in Testbed project, in following location - *CertificateAuthority\data\cert* . We need to make some small adjustments, to generate valid p12 file. For this purpose, we need to copy *ReferenceTestbedCA.crt* file from ca folder (one level above) and execute following command:

```
openssl pkcs12 -export -out testbed3.p12 -inkey testbed3.key -in testbed3.crt -certfile ReferenceTestbedCA.crt
```
As Export password insert ***password***, and confirm it.

This will generate valid testbed3.p12 file. Copy this file to certificate folder of the connector.


## TRUE Connector configuration

You can either use the provided certificates out-of-the-box or create your own self-signed ones following the next steps:

Generate private key and certificate with the following openssl command:

```
openssl req -x509 -newkey rsa:2048 -keyout consumer-key.pem -out consumer-cert.pem -sha256 -days 365 -subj "/C=IT/ST=Italy/L=Lecce/O=Engineering Ingegneria Informatica SpA/OU=R&D/CN=TRUEConnector" -addext "subjectAltName=DNS:be-dataapp-consumer,DNS:ecc-consumer,DNS:uc-dataapp-consumer"
 ```

* keyout - key name
* out - certificate name
* subj - information about the certificate owner like Company name, Country etc.
* subjectAltName - host names and/or IP address of the consumer components and host machine

Afterwards you will be prompted to insert the password.
 
To generate a KeyStore with the previous key and cert use the command:

```
openssl pkcs12 -export -out consumer-keyStore.p12 -inkey consumer-key.pem -in consumer-cert.pem -name true-connector-consumer
```

* out - KeyStore name
* inkey - private key
* in - certificate

Since the TRUEConnector uses the Java programming language it is advised to use the .jks format for the KeyStores and TrustStores. To convert the consumer KeyStore from .p12 to .jks use the following keytool command:
 
``` 
keytool -importkeystore -destkeystore true-connector-consumer-keystore.jks -srckeystore consumer-keyStore.p12 -srcstoretype PKCS12 -alias true-connector-consumer
```

* destkeystore - name of the new .jks KeyStore
* srckeystore - name of the .p12 KeyStore


Here are the commands for the same process for the provider:

```
openssl req -x509 -newkey rsa:2048 -keyout provider-key.pem -out provider-cert.pem -sha256 -days 365 -subj "/C=IT/ST=Italy/L=Lecce/O=Engineering Ingegneria Informatica SpA/OU=R&D/CN=TRUEConnector" -addext "subjectAltName=DNS:be-dataapp-provider,DNS:ecc-provider,DNS:uc-dataapp-provider"

openssl pkcs12 -export -out provider-keyStore.p12 -inkey provider-key.pem -in provider-cert.pem -name true-connector-provider

keytool -importkeystore -destkeystore true-connector-provider-keystore.jks -srckeystore provider-keyStore.p12 -srcstoretype PKCS12 -alias true-connector-provider
```

At the end we need the TrustStores for the consumer and provider respectively in which we will both certificates:

```
keytool -import -keystore true-connector-consumer-truststore.jks  -file provider-cert.pem -alias true-connector-provider

keytool -import -keystore true-connector-consumer-truststore.jks  -file consumer-cert.pem -alias true-connector-consumer

keytool -import -keystore true-connector-provider-truststore.jks  -file consumer-cert.pem -alias true-connector-consumer

keytool -import -keystore true-connector-provider-truststore.jks  -file provider-cert.pem -alias true-connector-provider
```

These commands can be also used to add certificates from other services e.g. DAPS, Broker, other providers, to the TrustStores.


After creating the KeyStores and TrustStores, you have insert their name, passwords, aliases and private key passwords in the .env:

```
#Consumer SSL settings
CONSUMER_KEYSTORE_NAME=true-connector-consumer-keystore.jks
CONSUMER_KEY_PASSWORD=password
CONSUMER_KEYSTORE_PASSWORD=password
CONSUMER_ALIAS=true-connector-consumer
#TRUSTORE (used also by IDSCP2)
CONSUMER_TRUSTORE_NAME=true-connector-consumer-truststore.jks
CONSUMER_TRUSTORE_PASSWORD=password

#Provider SSL settings
PROVIDER_KEYSTORE_NAME=true-connector-provider-keystore.jks
PROVIDER_KEY_PASSWORD=password
PROVIDER_KEYSTORE_PASSWORD=password
PROVIDER_ALIAS=true-connector-provider
#TRUSTORE (used also by IDSCP2)
PROVIDER_TRUSTORE_NAME=true-connector-provider-truststore.jks
PROVIDER_TRUSTORE_PASSWORD=password
```

**NOTE** The KeyStores for websocket communication must be set manually in the config.properties found in TRUEConnector/be-dataapp_resources_consumer and TRUEConnector/be-dataapp_resources_provider respectively:

```
server.ssl.key-password=keystorePassword
server.ssl.key-store=/cert/true-connector-consumer-keystore.jks

server.ssl.key-password=keystorePassword
server.ssl.key-store=/cert/true-connector-provider-keystore.jks
```

## Testbed interaction

For interaction with the Testbed you can use the provided [Postman collection](TRUEConnector_MVDS.postman_collection.json)

The endpoints can be configured in the **Variables** section of the collection ![Variables](pictures/postman_variables.png "Postman variables")

The **Forward-To** refers to the provider connector to whom the message should be sent.

### TRUE Connector as consumer

To perform contract negotiation with another connector and get an artifact. For this purpose, you can use ![TC as consumer](pictures/TC_Consumer.png "TC as consumer")

You can execute the whole folder, same as before, or execute each request in that order.

If everything was successful, it should look like the following:

![TC as consumer result](pictures/TC_Consumer_result.png "TC as consumer result")


### TRUE Connector as provider

TRUE Connector comes with predefined Self Description document. You can get more information about it by expecting the document itself on URL:

```
https://localhost:8090/

```

The IDS endpoint where the TRUE Connector provides it's data is:

```
https://localhost:8889/data
```

### Broker interaction

The interaction with MetadataBroker can be checked with the requests from the Broker interaction folder in the same way as the steps from above.

![Broker interaction](pictures/Broker_interaction.png "Broker interaction")

### Self Description API

And finally, the Self Description API, for modifying the Self Description document can be accessed via the 

![Self Description API](pictures/Self_Description_API.png "Self Description API")

# METADATA BROKER

## Component Documentation
The official documentation will cover the pre-requisites, installation and deployment of the component.

Official documentation: https://github.com/International-Data-Spaces-Association/metadata-broker-open-core

## Continue here after reading the official documentation

Download the component from the official repository

```
cd IDS-testbed
git clone -b 5.0.3 https://github.com/International-Data-Spaces-Association/metadata-broker-open-core.git
```

Use the downloaded component to build the broker-core image.

## Changes to the application.properties file
Use nano or your most favourite editor.
```
nano broker-core/src/main/resources/application.properties
```
# DAPS
This will make use of the locally installed DAPS.

```
# DAPS
# daps.url=https://daps.aisec.fraunhofer.de
daps.url=https://omejdn/auth/token
daps.validateIncoming=true
```

### Security-related
Add the local DAPS to the trusted hosts

```
# Security-related
...
jwks.trustedHosts=daps.aisec.fraunhofer.de,omejdn
ssl.certificatePath=/etc/cert/server.crt
ssl.javakeystore=/etc/cert/isstbroker-keystore.jks
```

## Changes to the component's keystore
At the folder `broker-core/src/main/resources/` add the certificate provided by the local CA, newly created by the local CA or provided by Fraunhofer AISEC. If it is NOT provided by the local CA, make sure it is correctly added to the local DAPS.

```
keytool -importkeystore -srckeystore {SRCKEYSTORE} -srcstoretype {STORETYPE} -srcstorepass {SRCSTOREPASS} -destkeystore {DESTKEYSTORE} -deststoretype {DESTSTORETYPE} -deststorepass {DESTSTOREPASS}
```
It could look something like this

```
keytool -importkeystore -srckeystore testbed3.p12 -srcstoretype pkcs12 -srcstorepass password -destkeystore isstbroker-keystore.jks -deststoretype jks -deststorepass password
```

Expected outcome:
```
"Import command completed:  1 entries successfully imported, 0 entries failed or cancelled"
```

To check the content of the created keystore, use the following command:

```
keytool -v -list -keystore {KEYSTORE}
```

It could look something like this

```
keytool -v -list -keystore isstbroker-keystore.jks
```

## Build the broker-core image

Go to the main directory and build the project with `maven`:

```
cd metadata-broker-open-core
mvn clean package
```

This will create a `.jar` file in `broker-core/target` that will have to be copied into `docker/broker-core`.

```
cp broker-core/target/broker-core-5.0.3.jar docker/broker-core
```

Once the file is copied, move to the `docker/broker-core` directory and place there the TLS certificate that corresponds to the DAPS. For the IDS-testbed it is located at `DAPS/keys/TLS/daps.cert` and use the following command to change the certificate format to `daps.crt`

```
openssl x509 -inform PEM -in daps.cert -out daps.crt
```

Then build the `core` image locally using the following command.

```
cd docker/broker-core
docker build -t registry.gitlab.cc-asp.fraunhofer.de/eis-ids/broker-open/core:5.0.3 .
```

## Adding the TLS certificates

At the `IDS-testbed/MetadataBroker/` folder place the TLS certificates created by the local CA together with the keystore.
* `server.crt`
* `server.key`
* `isstbroker-keystore.jks`

## Usage

Take the content from the file `metadata-broker-open-core/docker/composefiles/broker-localhost/docker-compose.yml` and copy it at your docker-compose.yml file. Use nano or your most favourite editor.
```
nano docker-compose.yml
```

Use the TLS certificates and ensure the container names are consistent with other dependencies by adding `container_name:`.

If port 443 is already in use, the `reverseproxy` container will exit with code 1. Follow the steps in the next block to get around this:

```
services:
  broker-reverseproxy:
    image: registry.gitlab.cc-asp.fraunhofer.de/eis-ids/broker-open/reverseproxy
    container_name: broker-reverseproxy
    volumes:
      - ./MetadataBroker/server.crt:/etc/cert/server.crt
      - ./MetadataBroker/server.key:/etc/cert/server.key
    ports:
      - "443:443" # Change to a port of your choosing if taken: "{PORT}:443"
      - "80:80" # Change to a port of your choosing if taken: "{PORT}:80"
    networks:
      - local

  broker-core:
    image: registry.gitlab.cc-asp.fraunhofer.de/eis-ids/broker-open/core:5.0.3
    container_name: broker-core
    volumes:
      - ./MetadataBroker/isstbroker-keystore.jks:/etc/cert/isstbroker-keystore.jks
    environment:
      - SPARQL_ENDPOINT=http://broker-fuseki:3030/connectorData
      - ELASTICSEARCH_HOSTNAME=broker-elasticsearch
      - SHACL_VALIDATION=true
      - DAPS_VALIDATE_INCOMING=true
      - COMPONENT_URI=https://localhost/
      - COMPONENT_CATALOGURI=https://localhost/connectors/
      - DAPS_URL=https://omejdn/auth/token
    expose:
      - "8080" 
    networks:
      - local

  broker-fuseki:
    image: registry.gitlab.cc-asp.fraunhofer.de/eis-ids/broker-open/fuseki
    container_name: broker-fuseki
    volumes:
      - broker-fuseki:/fuseki
    expose:
      - "3030"
    networks:
      - local
      
volumes:
  broker-fuseki:

networks:
  local:
    driver: bridge
```

Go to the compose file and build the Metadata Broker

```
docker-compose up
```

# Stopping the TRUEConnector-MVDS

To stop the TRUEConnector-MVDS just use the following command:

```
docker-compose down
``` -->
