#!/bin/bash

source dockerdev.sh

PRODUCT_ID=$(jcurl ${MARKET_URL}/products?q=resourceTypeId:juniper.resourceTypes.L2Circuit | jparse [\"items\"][0][\"id\"])
DEVICE_RID=$(jcurl ${MARKET_URL}/resources?resourceTypeId=juniper.resourceTypes.NetworkFunction\&label=jun_89 | jparse [\"items\"][0][\"providerResourceId\"])

cat <<EOF > l2vpn_124.json
{
"productId": "${PRODUCT_ID}",
"discovered": false,
"properties":{
			"device": "${DEVICE_RID}",
			"name": "202.123.47.88",
			"encapsulation-type": "ethernet-vlan",
			"virtual-circuit-id": "3395",
			"interface-name": "ge-0-0-2.3395",
			"operation": "delete",
			"no-control-word": true,
			"neighbor": "202.123.47.88",
			"ignore-encapsulation-mismatch": true,
			"mtu": 9216,
			"extension": {
				"interface": {
					"name": "ge-0-0-2.3395",
					"description": "TANA-ML2-32-2-Gandhinager-H-Way-2048k-TATA-COMMUNICATION-LIMITED-737905-050213",
					"logicalEncapsulation": "vlan-ccc",
					"dot1q": 3395,
					"operation" : "delete",
					"ccc_policer":{
						"input": "2048k",
						"output": "2048k"
					}
				}
			}
        }
}
EOF

jcurl -d @l2vpn_124.json ${MARKET_URL}/resources | jpp

rm -f l2vpn_124.json
