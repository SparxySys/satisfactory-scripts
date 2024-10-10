#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/SatisfactoryToken.sh
mkdir -p /run/satisfactory-tickrate/
filename="/run/satisfactory-tickrate/tickrate.txt"
touch "$filename"
while :; do
	tickrate=$(curl -s -XPOST $serverurl/api/v1 -H 'Content-Type: application/json' -H "Authorization: Bearer $token" --data '{"function":"QueryServerState","data":{"clientCustomData":""}}' | jq .data.serverGameState.averageTickRate)
	ts=$(date +"%H:%M:%S")
	orig=$(cat "$filename" | tail -n299)
	echo -e "$orig\n$ts $tickrate" > "$filename"
	sleep 1
done
