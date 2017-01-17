#!/bin/bash

DEVICE_IP="10.121.19.69"

source dockerdev.sh

PRODUCT_ID=$(jcurl ${MARKET_URL}/products?q=resourceTypeId:juniper.resourceTypes.NetworkFunction | jparse [\"items\"][0][\"id\"])
SESSION_PROFILE_ID=$(jcurl $MARKET_URL/resources?resourceTypeId=juniper.resourceTypes.SessionProfile\&q=label:jun_89 | jparse [\"items\"][0][\"id\"])
echo "${SESSION_PROFILE_ID}"
cat <<EOF > network_function.json
{
"productId": "${PRODUCT_ID}",
"label": "device_89",
"discovered": false,
"properties": {
    "sessionProfile": "${SESSION_PROFILE_ID}",
    "ipAddress": "${DEVICE_IP}"
}
}
EOF

jcurl -d @network_function.json ${MARKET_URL}/resources | jpp

rm -f network_function.json
