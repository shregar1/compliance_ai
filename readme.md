Setup: Perform the following task to setup the server
1. Populate the google api key in env file

2. Commands: Run the following commands to setup the server
* docker compose build
* docker compose up

Curl: Import the curl in postman to use the api.


curl --location 'http://0.0.0.0:8006/apis/compliance_check' \
--header 'Content-Type: application/json' \
--data '{
    "reference_number": "7ee938cf-5635-4287-a0a1-6bf3846baea1",
    "url": "https://mercury.com/"
}'