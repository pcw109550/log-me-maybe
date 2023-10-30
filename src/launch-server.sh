#!/bin/sh
set -eu

EXTERNAL_IP=$1
if [[ -z "$EXTERNAL_IP" ]]; then
    echo "Must set external IP"
    exit 1
fi

bits=26
nonce=$(head -c12 /dev/urandom | base64)

cat <<EOF
Send the output of: hashcash -mb${bits} ${nonce}
EOF

if head -n1 | hashcash -cqb${bits} -df /dev/null -r "${nonce}"; then
	EXTERNAL_IP=$EXTERNAL_IP python3.10 server.py
else
	echo Stamp verification failed
fi
