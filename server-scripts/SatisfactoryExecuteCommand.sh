#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
command="$@"
source $SCRIPT_DIR/SatisfactoryToken.sh
curl -s -XPOST $serverurl/api/v1 -H 'Content-Type: application/json' -H "Authorization: Bearer $token" \
--data '{"function":"RunCommand","data":{"Command":"'"$command"'","clientCustomData":""}}' | jq -r .data.commandResult
