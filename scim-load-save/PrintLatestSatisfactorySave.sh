#!/bin/bash
filename=$(ls -t /home/sparxy/.config/Epic/FactoryGame/Saved/SaveGames/server/ | head -n1)
filename="/home/sparxy/.config/Epic/FactoryGame/Saved/SaveGames/server/$filename"
cat "$filename"
