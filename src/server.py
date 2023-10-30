import os
import signal
import subprocess
import time

import requests
from Crypto.Util.number import isPrime

from hidden import FLAG, TOKENS

menu = """1 - launch new instance
2 - kill instance
3 - get flag"""

signal.alarm(120)

BLOCKCHAIN_TIMEOUT = 600
DOCKER_CMD_TIMEOUT = 60
DOCKER_IMAGE_NAME = os.environ.get("DOCKER_IMAGE_NAME", "log-me-maybe-0")
EXTERNAL_IP = os.environ.get("EXTERNAL_IP", "127.0.0.1")
# external port must be different with this nc program
EXTERNAL_PORT = int(os.environ.get("EXTERNAL_PORT", "12345"))

PRIVATE_KEY = "0x6ed331d598be80ecd073da21977446a31e9d0eb25378e0b902f3d7df5038ac74"


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
        self.index = TOKENS.index(token)
        self.port = 20000 + self.index
        self.container_name = f"{DOCKER_IMAGE_NAME}-{self.index}-{self.token}"

    @staticmethod
    def docker_cmd_run(cmd):
        subprocess.run(
            cmd.split(),
            timeout=DOCKER_CMD_TIMEOUT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def launch_instance(self):
        try:
            self.docker_cmd_run(f"docker stop {self.container_name}")
            self.docker_cmd_run(f"docker rm {self.container_name}")
            self.docker_cmd_run(f"docker run -idt --name {self.container_name} -p 127.0.0.1:{self.port}:8545 {DOCKER_IMAGE_NAME}")
        except:
            raise Exception(f"Container error: {self.token}")
        time.sleep(1)
        try:
            self.healthcheck()
        except Exception as e:
            raise e
        print("your private blockchain has been deployed")
        print(f"it will automatically terminate in {BLOCKCHAIN_TIMEOUT} seconds")
        print(f"rpc endpoint:   http://{EXTERNAL_IP}:{EXTERNAL_PORT}/rpc/{self.token}")
        print(f"private key:    {PRIVATE_KEY}")

    def kill_instance(self):
        try:
            self.docker_cmd_run(f"docker stop {self.container_name}")
            self.docker_cmd_run(f"docker rm {self.container_name}")
        except:
            raise Exception(f"Container error: {self.token}")
        try:
            # must fail
            self.healthcheck()
        except:
            pass
        else:
            raise Exception(f"Not killed: {self.token}")
        print("your private blockchain has been killed")

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
            res = RPC(f"http://127.0.0.1:{self.port}", data)
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

    def healthcheck(self):
        data = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1,
        }
        try:
            res = RPC(f"http://127.0.0.1:{self.port}", data)
            assert int(res["result"], 16) >= 1
        except:
            raise Exception(f"HC Failure: {self.token}")


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
