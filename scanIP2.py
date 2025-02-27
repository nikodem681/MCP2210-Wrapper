import socket
import ipaddress

def is_host_up(ip, port=80, timeout=0.5):
    """Check if a host is reachable by attempting to connect to a specific port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((ip, port)) == 0

def get_hostname(ip):
    """Try to resolve the hostname of an IP address."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "Unknown"

def scan_network(subnet, port=80, timeout=0.5):
    """Scan a given subnet for active hosts and retrieve their hostnames."""
    network = ipaddress.ip_network(subnet, strict=False)
    active_hosts = []

    for ip in network.hosts():
        ip = str(ip)
        if is_host_up(ip, port, timeout):
            hostname = get_hostname(ip)
            active_hosts.append((ip, hostname))
            print(f"Host is up: {ip} | Hostname: {hostname}")

    return active_hosts

# Get subnet input from the user
subnet = input("Enter subnet (e.g., 192.168.1.0/24): ").strip()

# Scan the network
active_hosts = scan_network(subnet)

print(f"\nTotal active hosts found: {len(active_hosts)}")
for ip, hostname in active_hosts:
    print(f"IP: {ip} | Hostname: {hostname}")
