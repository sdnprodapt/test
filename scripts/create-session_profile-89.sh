#!/bin/bash

DEVICE_IP="10.121.19.69"

source dockerdev.sh

PRODUCT_ID=$(jcurl ${MARKET_URL}/products?q=resourceTypeId:juniper.resourceTypes.SessionProfile | jparse [\"items\"][0][\"id\"])

cat <<EOF > session_profile.json
{
"productId": "${PRODUCT_ID}",
"label": "jun_89",
"discovered": false,
"properties": {
    "authentication": {
        "netconf": {
            "username": "root",
            "password": "Juniper"
        },
        "snmp": {
            "community": "public",
            "version" : "v2c"
        }
    },
    "connection": {
        "netconf": {
            "hostport": 830
        },
        "snmp": {
            "hostport": 162
        }
    },
    "typeGroup": "/typeGroups/Juniper"
}
}
EOF

jcurl -d @session_profile.json ${MARKET_URL}/resources | jpp

rm -f session_profile.json
