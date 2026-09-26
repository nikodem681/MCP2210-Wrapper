"""Ping every host in a subnet (Windows ping syntax) and print the ones that answer."""
import ipaddress
import socket
import subprocess
import sys


def ping_host(ip, timeout_ms=2):
    result = subprocess.run(
        ["ping", "-n", "1", "-w", str(timeout_ms), ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0


def scan_hosts(network="192.168.2.0/24"):
    network = ipaddress.ip_network(network, strict=False)
    active_hosts = []

    for ip in network.hosts():
        ip = str(ip)
        print(f"Scanning ip address: {ip}")
        if ping_host(ip):
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                print(f"Hostname is: {hostname}")
            except socket.herror:
                hostname = "Unknown"
            active_hosts.append({"ip": ip, "hostname": hostname})

    return active_hosts


if __name__ == "__main__":
    network_range = sys.argv[1] if len(sys.argv) > 1 else "192.168.2.0/24"  # lab network by default
    for host in scan_hosts(network_range):
        print(f"IP: {host['ip']}, Hostname: {host['hostname']}")
