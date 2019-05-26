#!/bin/bash

PI_MAC_ADD="b8:27"
IP_REGEX="\b([0-9]{1,3}\.){3}[0-9]{1,3}\b"

ip=$(arp -a | grep $PI_MAC_ADD | grep -oE $IP_REGEX)
echo "pi ip=$ip"

if [[ -z $ip ]]
then
    echo "pi not found"
else
    ssh pi@$ip
fi