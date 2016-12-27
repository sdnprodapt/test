#!/bin/bash

source dockerdev.sh

PRODUCT_ID=$(jcurl ${MARKET_URL}/products?q=resourceTypeId:juniper.resourceTypes.L3VPN | jparse [\"items\"][0][\"id\"])
DEVICE_RID=$(jcurl ${MARKET_URL}/resources?resourceTypeId=juniper.resourceTypes.NetworkFunction\&label=jun_89 | jparse [\"items\"][0][\"providerResourceId\"])

cat <<EOF > l3vpn_123.json
{
"productId": "${PRODUCT_ID}",
"discovered": false,
"label": "",
"properties":{
            "device": "${DEVICE_RID}",
            "tpe": "some_interface",
            "service":{
                "svc-bandwidth": 10000
            },

            "extension": {
                "interface": {
                    "name": "ge-0-0-1.500",
                    "description": "NAPC-ML3-6-1-MUMBAI-20480K-NATIONAL-PAYMENTS",
                    "dot1q": 500,
                    "inservicePolicy": "in_STANDARD_20480",
                    "outservicePolicy": "out_STANDARD_20480",
                    "address": "10.100.0.1/30"
                },
                "VrfPolicy": {
                    "device": "${DEVICE_RID}",
                    "community": [{
                        "community_name": "NATIONAL-PAYMENT-6-H-export-COMM",
                        "members": [
                            "target:9730:17053"
                        ]
                    }, {
                        "community_name": "NATIONAL-PAYMENT-6-H-import-COMM",
                        "members": [
                            "target:9730:17053"
                        ]
                    }, {
                        "community_name": "NATIONAL-PAYMENT-6-H-import-COMM1",
                        "members": [
                            "target:9730:17054"
                        ]
                    }],
                    "policy-statement": [{
                        "name": "NATIONAL-PAYMENT-6-H-export",
                        "terms": [{
                            "name": "11",
                            "from": {
                                "protocol": [
                                    "direct",
                                    "static",
                                    "bgp"
                                ]
                            },
                            "then": {
                                "community": [{
                                    "community_name": "NATIONAL-PAYMENT-6-H-export-COMM",
                                    "operation": "add"
                                }],
                                "next-hop": {
                                    "self": true
                                },
                                "accept": true
                            }
                        }, {
                            "name": "last",
                            "then": {
                                "accept": true
                            }
                        }]
                    }, {
                        "name": "NATIONAL-PAYMENT-6-H-import",
                        "terms": [{
                            "name": "10",
                            "from": {
                                "protocol": [
                                    "direct",
                                    "static",
                                    "bgp"
                                ],
                                "community": [
                                    "NATIONAL-PAYMENT-6-H-import-COMM",
                                    "NATIONAL-PAYMENT-6-H-import-COMM1"
                                ]
                            },
                            "then": {
                                "next-hop": {
                                    "self": true
                                },
                                "accept": true
                            }
                        }, {
                            "name": "last",
                            "then": {
                                "reject": true
                            }
                        }]
                    }]
                }
            },
            "attachment": {
                "connection": {
                    "routing-instance": {
                        "device": "${DEVICE_RID}",
                        "name": "NATIONAL-PAYMENT-6-H",
                        "instance-type": "vrf",
                        "interface": ["ge-0-0-1.500"],
                        "route-distinguisher": "9730:20160912",
                        "vrf-import": ["NATIONAL-PAYMENT-6-H-import"],
                        "vrf-export": ["NATIONAL-PAYMENT-6-H-export"],
                        "vrf-table-label": "",
                        "routing-options": {
                            "auto_export": true,
                            "maximum-prefixes": {
                                "limit": 5000,
                                "threshold": 80
                            }
                        },
                        "protocols_bgp": {
                            "groups": [{
                                "name": "NATIONAL-PAYMENT-6-H",
                                "type": "external",
                                "as-override": true,
                                "peer-as": 100,
                                "local-address": "",
                                "local_as": 100,
                                "neighbors": [{
                                    "address": "10.100.0.2",
                                    "local-address": "10.100.0.1",
                                    "peer-as": 65001,
                                    "as-override": true
                                }],
                                "export_policies": ["STATIC", "CONNECTED"]
                            }]
                        }
                    },
                    "class-of-service": {
                        "device": "${DEVICE_RID}",
                        "routing-instance": [{
                            "name": "NATIONAL-PAYMENT-6-H",
                            "classifier-name": "BACKBONE_QOS_Classifiers"
                        }]
                    }
                }
            }
        }
}
EOF

jcurl -d @l3vpn_123.json ${MARKET_URL}/resources | jpp

rm -f l3vpn_123.json
