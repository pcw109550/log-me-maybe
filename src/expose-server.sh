#!/bin/sh

EXTERNAL_IP=$1
if [[ -z "$EXTERNAL_IP" ]]; then
    echo "Must set external IP"
    exit 1
fi

TIMEOUT=120
PORT=33333

echo "socat start"
socat -t$TIMEOUT -T$TIMEOUT "TCP-LISTEN:${PORT},reuseaddr,fork" "EXEC:./launch-server.sh ${EXTERNAL_IP}"
