#!/usr/bin/python3

"""
Directory server : Download files from a directory in LAN.
https://wingxel.github.io/website/index.html
"""

# If on windows, run the script as administrator.

import getopt
import os
import platform
import socketserver
import subprocess
import sys
from datetime import datetime
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from socket import socket, AF_INET, SOCK_STREAM


def usage() -> None:
    print("""Usage:
-h or --help            This help text.
-p or --port            Port to listen at.
-d or --directory       Directory to serve.
Example:
python3 FileServer.py  -d /home/user/Music -p 8000""")


def get_random_hex(length: int = 8) -> str:
    return os.urandom(length).hex()


def port_is_available(prt: int) -> bool:
    try:
        cs = socket(AF_INET, SOCK_STREAM)
        cs.connect(("localhost", prt))
        cs.close()
    except ConnectionRefusedError:
        return True
    return False


def get_available_port() -> int:
    for p in [1290, 8000, 2671, 2189, 3345, 9019, 1818, 7171, 1123, 8012]:
        if port_is_available(p):
            return p


def get_args() -> dict:
    data = {"directory": str(Path.home()), "port": get_available_port()}
    try:
        opts, _ = getopt.getopt(sys.argv[1::], "d:p:h", ["directory=", "port=", "help"])
        for opt, arg in opts:
            if opt in ["-h", "--help"]:
                usage()
                sys.exit(0)
            if opt in ["-p", "--port"]:
                try:
                    temp_port = eval(arg)
                    if port_is_available(temp_port):
                        data["port"] = temp_port
                    else:
                        print(f"Port {temp_port} is not available, defaulting to {data['port']}")
                except NameError as err:
                    print(f"Invalid port number : {str(err)}")
            if opt in ["-d", "--directory"]:
                data["directory"] = arg
    except Exception as error:
        print(f"An error occurred : {str(error)}")
    return data


ar = get_args()
port = ar["port"]
dr = ar["directory"]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=dr, **kwargs)


def start_network() -> str:
    result = ""
    if platform.system().lower() == "windows":
        identity = get_random_hex()
        key = get_random_hex(4)
        try:
            subprocess.call(["netsh", "wlan", "set", "hostednetwork", "mode=allow", f"ssid={identity}", f"key={key}"])
            subprocess.call(["netsh", "wlan", "start", "hostednetwork"])
            ipconfig_res = subprocess.getoutput("ipconfig")
            print(f"{ipconfig_res}\n\nHotspot ssid: {identity} key: {key}")
            result = "Successfully started hotspot"
        except Exception as error:
            result = f"An error occurred : {error}"
    elif platform.system().lower() == "linux":
        try:
            result = subprocess.getoutput("nmcli connection up Hotspot")
            ifconfig_res = subprocess.getoutput("ifconfig")
            print(f"{ifconfig_res}\n\nTo view the password of the hotspot got to:\nSettings => WI-FI => WI-FI Hotspot")
        except Exception as error:
            result = f"An error occurred : {error}"
    if len(result) > 0:
        print(f"{datetime.now()} : Hotspot started")
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
    net = start_network()
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"{datetime.now()} : Serving {dr} at port {port}")
            print(net)
            print("Press Ctrl + C to exit")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(stop_network())
        print(f"{datetime.now()} : Server exited.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception as err:
        print(f"Error => {str(err)}")
        print(stop_network())


if __name__ == "__main__":
    main()
