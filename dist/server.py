import os
import signal

import requests
from Crypto.Util.number import isPrime
from hidden import TOKENS, FLAG, PORT, ENDPOINT

menu = """1 - launch new instance
2 - kill instance
3 - get flag"""

signal.alarm(120)


def RPC(endpoint, data):
    res = requests.post(
        endpoint, headers={"Content-Type": "application/json"}, json=data, timeout=3
    )
    return res.json()


class Handler:
    def __init__(self, token):
        if token not in TOKENS:
            raise Exception("Not authorized")
        self.token = token
        self.port = PORT
        self.endpoint = ENDPOINT

    def launch_instance(self):
        # not relevant
        pass

    def kill_instance(self):
        # not relevant
        pass

    def get_flag(self):
        try:
            block_number = int(input("block number: "))
            p = int(input("prime: "))
            assert block_number >= 0 and p >= 1
        except:
            raise Exception(f"Invalid input")
        data = {
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": [hex(block_number), False],
            "id": 1,
        }
        try:
            res = RPC(f"{self.endpoint}:{self.port}", data)
            bloom = int(res["result"]["logsBloom"], 16)
            q = bloom // p
            assert p.bit_length() == 1024 and isPrime(p)
            assert q.bit_length() == 1024 and isPrime(q)
            assert p * q == bloom
        except Exception as e:
            raise Exception(f"No flag")
        print(FLAG)

    def handle(self, action):
        if action < 0 or action >= 3:
            raise Exception("Invalid action")
        handlers = [self.launch_instance, self.kill_instance, self.get_flag]
        handlers[action]()


if __name__ == "__main__":
    print(menu)
    try:
        action = int(input("action? ")) - 1
        token = input("token? ")
    except:
        print("Invalid input")
        exit(1)
    try:
        handler = Handler(token)
        handler.handle(action)
    except Exception as e:
        print(str(e))
        exit(1)
    exit(0)
