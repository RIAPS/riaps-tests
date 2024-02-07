# Note: these fixtures are added for possible future use
#       they are currently not utilized in the testing

import datetime
import time
import pytest
import re
import socket


@pytest.fixture
def test_logger():
    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    return logger


def get_ip_address(hostname):
    try:
        # Use socket to resolve the IP address
        ip_address = socket.gethostbyname_ex(hostname)
        print(ip_address)
        for ip in ip_address[2]:
            return ip
    except socket.gaierror:
        return None


def get_client_list(file_path):
    client_names = []
    ip_addresses = []

    # Regular expression pattern to match lines with desired information
    pattern = r'on\s*\((.*?)\)\s*(\w+)_ACTOR'

    with open(file_path, 'r') as file:
        for line in file:
            # Remove leading and trailing whitespaces
            line = line.strip()
            # Skip lines that start with '//'
            if line.startswith('//'):
                continue
            # Search for matches in the line using the pattern
            matches = re.findall(pattern, line)
            for match in matches:
                # Split the matched portion to extract client names and IP addresses
                parts = match[0].split(',')
                for part in parts:
                    part = part.strip()
                    if part:
                        # Check if it's a valid IP address
                        try:
                            socket.inet_aton(part)
                            ip_addresses.append(part)
                        except socket.error:
                            client_names.append(part)

    # Resolve IP addresses for client names
    resolved_ip_addresses = {}
    for client_name in client_names:
        ip_address = get_ip_address(client_name)
        if ip_address:
            resolved_ip_addresses[client_name] = ip_address

    print("Client Names:", client_names)
    print("Resolved IP Addresses:", resolved_ip_addresses)
    ip_addresses.extend(resolved_ip_addresses.values())
    print("IP Addresses:", ip_addresses)
    return ip_addresses
