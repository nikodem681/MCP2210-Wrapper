import socket
import subprocess
import ipaddress

def ping_host(ip, timeout=2):  # Таймаут в миллисекундах
    result = subprocess.run(
        ["ping", "-n", "1", "-w", str(timeout), ip],
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

network_range = "192.168.2.0/24"  # Укажи свою сеть
hosts = scan_hosts(network_range)

for host in hosts:
    print(f"IP: {host['ip']}, Hostname: {host['hostname']}")
