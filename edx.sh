#!/bin/bash
IFS=''
counter=0
while read line
do
    case "$line" in
        "") continue ;;
        \#*) continue ;;
    esac
    if [ $counter == 0 ]; then
		cd $line
		let counter=counter+1
	else
		edx-dl -u edx_username -p password
		let counter=0
		cd ..
	fi
done <$1
