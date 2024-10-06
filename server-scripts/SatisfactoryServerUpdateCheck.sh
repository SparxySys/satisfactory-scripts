#!/bin/bash
remoteBuildId=$(curl -s https://api.steamcmd.net/v1/info/1690800 | jq -r '.data."1690800".depots.branches.public.buildid')
localBuildId=$(cat /home/sparxy/SatisfactoryDedicatedServer/steamapps/appmanifest_1690800.acf | grep \"buildid\" -i | awk '{ print $2; }' | jq -r)
if [ "$remoteBuildId" = "null" ] || [ "$remoteBuildId" = "" ]; then
	sleep 1
	echo "Satisfactory server update check failed. remoteBuildId=$remoteBuildId"
	exit 1
elif [ "$remoteBuildId" = "$localBuildId" ]; then
	echo "Satisfactory server up to date. $localBuildId == $remoteBuildId."
else
	/home/sparxy/SendMatrixMessage.sh '['$(date +'%H:%M:%S')']' "Server restarting to update from $localBuildId to $remoteBuildId."
	echo "Satisfactory server $localBuildId should be updated to $remoteBuildId."
	echo "Restarting service satisfactory-server.service"
	systemctl restart satisfactory-server.service
fi
