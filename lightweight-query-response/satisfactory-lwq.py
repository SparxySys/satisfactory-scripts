#!/usr/bin/python3
import socket
import numpy as np
import time
import sys
import requests
import json

ADDRESS='localhost'
PORT=7777
current_socket_type=socket.AF_INET
current_address=ADDRESS

def query():
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
            return {'error': 'Incorrect ProtocolMagic.'}

        if response[3:4] != np.uint8(1).tobytes():
            return {'error': 'API version {0} is not supported.'.format(np.frombuffer(response[3:4], dtype=np.uint8).item())}

        if response[2:3] != np.uint8(1).tobytes():
            return {'error': 'Message type {0} is not expected MessageType.'.format(np.frombuffer(response[2:3], dtype=np.uint8).item())}

        if response[-1:] != np.uint8(1).tobytes():
            return {'error': 'Terminator Byte is not correct.'}

        payload = response[4:-1]
        cookie = np.frombuffer(payload[0:8], dtype=np.uint64)
        server_state = np.frombuffer(payload[8:9], dtype=np.uint8)
        change_list = np.frombuffer(payload[9:13], dtype=np.uint32)
        server_flags = np.frombuffer(payload[13:21], dtype=np.uint64)
        sub_states_count = np.frombuffer(payload[21:22], dtype=np.uint8)
        sub_states = []
        for i in range(sub_states_count.item()):
            offset = 22+(3*i)
            sub_states.append([np.frombuffer(payload[offset:offset+1], dtype=np.uint8), np.frombuffer(payload[offset+1:offset+3], dtype=np.uint16)])
        
        offset = 22 + (sub_states_count.item() * 3)
        server_name_length = np.frombuffer(payload[offset:offset+2], dtype=np.uint16)
        offset += 2
        server_name = payload[offset:offset+server_name_length.item()].decode('utf-8')

        if offset + server_name_length.item() != len(payload):
            return {'error': 'Unknown data between ServerName and Terminator Byte.'}

        sub_state_names = ['ServerGameState', 'ServerOptions', 'AdvancedGameSettings', 'SaveCollection', 'Custom1', 'Custom2', 'Custom3', 'Custom4']
        sub_states_parsed = []
        for i in range(len(sub_states)):
            sub_states_parsed.append({
                'SubStateId': {
                    'key': sub_states[i][0].item(),
                    'value': sub_state_names[sub_states[i][0].item()]
                },
                'SubStateVersion': sub_states[i][1].item()
            })

        detected_flags = []
        if np.bitwise_and(0x1, server_flags) == 1:
            detected_flags.append('Modded')
        if np.bitwise_and(0x2, server_flags) == 1:
            detected_flags.append('Custom1')
        if np.bitwise_and(0x4, server_flags) == 1:
            detected_flags.append('Custom2')
        if np.bitwise_and(0x8, server_flags) == 1:
            detected_flags.append('Custom3')
        if np.bitwise_and(0x16, server_flags) == 1:
            detected_flags.append('Custom4')

        state_names = ['Offline', 'Idle', 'Loading', 'Playing']
        return {
            'ServerState': { 
                'key': server_state.item(),
                'value': state_names[server_state.item()]
            },
            'ServerNetCL': change_list.item(),
            'ServerFlags': { 'value': server_flags.item(), 'flags': detected_flags },
            'SubStates': sub_states_parsed,
            'ServerName': server_name
        }
    except socket.timeout:
        return {'error': 'Read timeout.'}

print(json.dumps(query()))
