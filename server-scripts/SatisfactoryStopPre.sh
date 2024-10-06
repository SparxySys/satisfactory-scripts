#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/SatisfactoryToken.sh
savename=prestopsave$(date +"%Y%m%d%H%M%S")
curl -s -XPOST $serverurl/api/v1 -H 'Content-Type: application/json' -H "Authorization: Bearer $token" --data '{"function":"SaveGame","data":{"SaveName":"'$savename'","clientCustomData":""}}' | jq .
if [ $? -eq 0 ]; then
	echo "Pre-shutdown: Saved $savename"
else
	echo "Pre-shutdown: Failed to save game"
fi
sleep 1
