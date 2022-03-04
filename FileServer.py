#!/usr/bin/python3

"""
Directory server : Download files from a directory in LAN.
https://wingxel.github.io/website/index.html
"""

# If on windows, run the script as administrator.

import os
import sys
import getopt
import platform
import subprocess
import socketserver


from pathlib import Path
from random import randint
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
from http.server import HTTPServer, SimpleHTTPRequestHandler


def usage() -> None:
	print("""Usage:
-h or --help            This help text.
-p or --port			Port to listen at.
-d or --directory       Directory to serve.
Example FileServer.py  -d /home/user/Music -p 8000""")


def port_is_available(prt: int) -> bool:
	try:
		cs = socket(AF_INET, SOCK_STREAM)
		cs.connect(("", prt))
		cs.close()
	except ConnectionRefusedError as error:
		return True
	return False


def get_available_port() -> int:
	for p in [1290, 8000, 2671, 2189, 3345, 9019, 1818, 7171, 1123, 8012]:
		if port_is_available(p):
			return p


def get_args() -> str:
	data = {"directory":str(Path.home()), "port": get_available_port()}
	try:
		opts, _ = getopt.getopt(sys.argv[1::], "d:p:h", ["directory=", "port=", "help"])
		for opt, arg in opts:
			if opt in ["-h", "--help"]:
				usage()
				sys.exit(0)
			if opt in ["-p", "--port"]:
				try:
					tempPort = eval(arg)
					if port_is_available(tempPort):
						data["port"]
				except NameError as err:
					pass
			if opt in ["-d", "--directory"]:
				data["directory"] = arg
	except Exception as error:
		print(f"An error occurred : {str(error)}")
	return data


port = get_args()["port"]
dr = get_args()["directory"]


class Handler(SimpleHTTPRequestHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, directory=dr, **kwargs)


def get_random_text(length: int) -> str:
	name_list = []
	for i in range(0, length):
		name_list.append(chr(randint(ord('a'), ord('z'))))
	return "".join(name_list) + str(randint(12, 100))


def get_random_key(length: int = 8) -> str:
	key_list = []
	for i in range(0, (length * 2)):
		key_list.append(chr(randint(ord('a'), ord('z'))))
		key_list.append(chr(randint(ord('A'), ord('Z'))))
		key_list.append(str(randint(1, 9)))
	key = []
	for i in range(0, length):
		key.append(key_list[randint(0, len(key_list) - 1)])
	return "".join(key)


def start_network() -> str:
	result = ""
	if platform.system().lower() == "windows":
		identity = get_random_text(10)
		key = get_random_key(10)
		try:
			subprocess.call(["netsh", "wlan", "set", "hostednetwork", "mode=allow", f"ssid={identity}", f"key={key}"])
			subprocess.call(["netsh", "wlan", "start", "hostednetwork"])
		except Exception as error:
			print(f"An error occurred : {error}")
		result = "Successfully started hotspot"
	elif platform.system().lower() == "linux":
		try:
			result = subprocess.getoutput("nmcli connection up Hotspot")
			print("To view the password of the hotspot got to:\nSettings => WI-FI => WI-FI Hotspot")
		except Exception as error:
			print(f"An error occurred : {error}")
	return result


def stop_network() -> str:
	result = ""
	if platform.system().lower() == "windows":
		try:
			subprocess.call(["netsh", "wlan", "stop", "hostednetwork"])
			result = "Successfully stopped the hotspot"
		except Exception as error:
			print(f"An error occurred : {error}")
	elif platform.system().lower() == "linux":
		try:
			result = subprocess.getoutput("nmcli connection down Hotspot")
		except Exception as error:
			print(f"An error occurred : {error}")
	return result


def main() -> None:
	identity = ""
	key = ""
	net = start_network()
	try:
		with socketserver.TCPServer(("", port), Handler) as httpd:
			print(f"{datetime.now()} : Serving {dr} at port {port}")
			print(f"Network: {identity} key: {key} =>" if platform.system().lower() == "windows" else net)
			httpd.serve_forever()
	except KeyboardInterrupt:
		print(stop_network())
		print(f"{datetime.now()} : Server exited.")
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
	except Exception:
		print(stop_network())


if __name__ == "__main__":
	main()
