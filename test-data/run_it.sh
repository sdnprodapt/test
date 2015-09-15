#!/bin/sh

#command=create-virtual-router.json
command=delete-virtual-router.json


session="URHVKBS34SRI37FV3L34HWEZHGU"

echo $command
wget -O - --post-file=/home/tgutjahr/dev/bp-ra-juniperng/test-data/$command --header=Content-Type:application/json "http://localhost:8080/api/v1/devices/$session/execute" | python -m json.tool
echo $results


