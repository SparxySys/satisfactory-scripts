#!/usr/bin/python3
import socket
import numpy as np
import time
import sys
import requests
import urllib3
import requests.packages.urllib3.util.connection as urllib3_cn

if len(sys.argv) < 3 or len(sys.argv) > 4:
    print('Incorrect number of arguments. Call with hostname and port, or with hostname, port and address family, i.e.\n\t./satisfactory-test.py localhost 7777\n\t./satisfactory-test.py fe80::5a11:22ff:feb2:23f0 7777 6\n\t./satisfactory-test.py 127.0.0.1 7777 4')
    exit(1)

ADDRESS=sys.argv[1]
PORT=int(sys.argv[2])
current_socket_type=socket.AF_INET
current_address=ADDRESS

test_ipv4=True
test_ipv6=True

if len(sys.argv) == 4:
    if sys.argv[3] == '4' or sys.argv[3].lower() == 'ipv4':
        test_ipv6 = False
    elif sys.argv[3] == '6' or sys.argv[3].lower() == 'ipv6':
        test_ipv4 = False
    else:
        print('Unknown address family ' + sys.argv[3])
        sys.exit(1)

print('Testing connection to Satisfactory Server at ' + ADDRESS + ' port ' + str(PORT))

def test_tcp():
    url = 'https://' + current_address + ':' + str(PORT) + '/api/v1'
    print('Connecting to HTTPS endpoint {0}, expecting 404 with errorCode errors.com.epicgames.httpserver.route_handler_not_found.'.format(url))
    try:
        urllib3.disable_warnings()
        response = requests.get(url, verify=False, timeout=(5, 10))
        response_data = response.json()
        if response.status_code == 404 and response_data['errorCode'] == 'errors.com.epicgames.httpserver.route_handler_not_found':
            print('TCP Test: Success.')
        else:
            print('TCP Test: Failed, unexpected response.')
        print('TCP Response: ' + response.text)
    except requests.exceptions.Timeout:
        print('TCP Test: Connection timeout.')
        return

def test_udp():
    print('Sending UDP LightweightQuery Poll Server State packet to {0}:{1}.'.format(ADDRESS, str(PORT)))
    message=bytearray(bytes.fromhex('D5F6'))
    message.append(np.uint8(0))
    message.append(np.uint8(1))
    message.extend(np.uint64(round(time.time() * 1000)))
    message.append(np.uint8(1))
    connection = socket.socket(current_socket_type, socket.SOCK_DGRAM)
    connection.settimeout(10)
    connection.sendto(message, (ADDRESS, PORT))
    try:
        response, address = connection.recvfrom(1024)

        if response[0:2] != bytes.fromhex('D5F6'):
            print('UDP Test: Failed to read response.')
            print('Incorrect ProtocolMagic.')
            return

        if response[3:4] != np.uint8(1).tobytes():
            print('UDP Test: Failed to read response.')
            print('API version {0} is not supported.'.format(np.frombuffer(response[3:4], dtype=np.uint8).item()))
            return

        if response[2:3] != np.uint8(1).tobytes():
            print('UDP Test: Failed to read response.')
            print('Message type {0} is not expected MessageType.'.format(np.frombuffer(response[2:3], dtype=np.uint8).item()))
            return

        if response[-1:] != np.uint8(1).tobytes():
            print('UDP Test: Failed to read response.')
            print('Terminator Byte is not correct.')
            return

        payload = response[4:-1]
        cookie = np.frombuffer(payload[0:8], dtype=np.uint64)
        server_state = np.frombuffer(payload[8:9], dtype=np.uint8)
        change_list = np.frombuffer(payload[9:13], dtype=np.uint32)
        server_flags = np.frombuffer(payload[13:21], dtype=np.uint64)
        sub_states_count = np.frombuffer(payload[21:22], dtype=np.uint8)
        sub_states = []
        for i in range(sub_states_count.item()):
            offset = 22+(3*i)
            sub_states.append([payload[offset:offset+1], payload[offset+1:offset+3]])
        
        offset = 22 + (sub_states_count.item() * 3)
        server_name_length = np.frombuffer(payload[offset:offset+2], dtype=np.uint16)
        offset += 2
        server_name = payload[offset:offset+server_name_length.item()].decode('utf-8')

        if offset + server_name_length.item() != len(payload):
            print('UDP Test: Failed to read response.')
            print('Unknown data between ServerName and Terminator Byte.')
            return

        state_names = ['Offline', 'Idle', 'Loading', 'Playing']
        print('UDP Test: Success.')
        print('UDP Response: Server "{0}" is in state {1} with game build {2}.'.format(server_name, state_names[server_state.item()], change_list.item()))
    except socket.timeout:
        print('UDP Test: Read timeout.')
        return

def allowed_gai_family():
    return current_socket_type

urllib3_cn.allowed_gai_family = allowed_gai_family

if test_ipv4:
    print('Testing for IPv4')
    try:
        test_tcp()
        test_udp()
    except Exception as e:
        print('Failed due to Exception', e)

if test_ipv6:
    print('Testing for IPv6')
    try:
        current_address = ADDRESS
        if ':' in current_address:
            current_address = '[' + current_address + ']'
        
        current_socket_type=socket.AF_INET6
        test_tcp()
        test_udp()
    except Exception as e:
        print('Failed due to Exception', e)    

print('Test complete.')
