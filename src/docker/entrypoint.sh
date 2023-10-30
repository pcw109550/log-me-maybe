#!/bin/sh

ADDRESS=0x78f3220F17D095a0a397a1DC621aF4EB4C57aB85

timeout 600 \
geth --datadir=data \
--keystore data/keystore/ \
--allow-insecure-unlock \
--networkid 13337 \
--nodiscover --mine \
--password config/password.txt --unlock $ADDRESS --miner.etherbase $ADDRESS \
--http --http.api=eth --http.addr=0.0.0.0 --http.port=8545 --http.corsdomain='*' --http.vhosts='*' \
--rpc.allow-unprotected-txs \
--miner.gaslimit 16777216
