#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
commandsToExecute=()
mapfile -t commandsToExecute < <( cat ue5variables.json| jq -r '.[] | select(.type=="Var") | .name')
source $SCRIPT_DIR/SatisfactoryToken.sh
for command in "${commandsToExecute[@]}"
do
	result=$(curl -s -XPOST $serverurl/api/v1 -H 'Content-Type: application/json' -H "Authorization: Bearer $token" --data '{"function":"RunCommand","data":{"Command":"'"$command"'","clientCustomData":""}}' | jq -r '.data | select(.returnValue == true) | .commandResult')
	[[ ! -z "$result" ]] && echo -e "$result"
done
