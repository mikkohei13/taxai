import socket
import requests

def test_dns():
    hosts = ['api', 'taxai-api-1', 'torchserve']
    for host in hosts:
        try:
            print(f"\nTrying to resolve {host}")
            ip = socket.gethostbyname(host)
            print(f"Successfully resolved {host} to {ip}")
        except socket.gaierror as e:
            print(f"Failed to resolve {host}: {e}")

if __name__ == '__main__':
    test_dns() 