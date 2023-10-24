import socket
import threading
import json
import os
import re

if not os.path.isdir('CLIENT_MEDIA'):
    os.mkdir('CLIENT_MEDIA')
CHUNK = 1024

HOST = '127.0.0.1'
PORT = 8080

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")


def connect_to_server():
    name = input('Enter your name: ')
    room = input('Enter room name: ')

    message = json.dumps({
        "type": "connect",
        "payload": {
            "name": name,
            "room": room
        }
    })
    client_socket.sendall(message.encode('utf-8'))

    return name, room


def receive_messages():
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break

        data = json.loads(message)
        message_type = data.get('type')

        if message_type == 'connect_ack':
            print(data['payload']['message'])
        elif message_type == 'notification':
            print(data['payload']['message'])
        elif message_type == 'message':
            sender = data['payload']['sender']
            room = data['payload']['room']
            text = data['payload']['text']
            print(f"\n{sender}({room}): {text}")
        elif message_type == 'download-ack':
            download_thread = threading.Thread(target=download_file, args=(client_socket, data))
            download_thread.start()
            download_thread.join()


def send_messages(name, room, message):
    data = json.dumps({
            "type": "message",
            "payload": {
                "sender": name,
                "room": room,
                "text": f'{message}\n'
            }
        })
    client_socket.sendall(data.encode('utf-8'))


def upload_file(filepath, name, room):
    if os.path.exists(filepath):
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        upload_message = json.dumps({
            "type": "upload",
            "payload": {
                "file_name": filename,
                "file_size": filesize,
                "name": name,
                "room": room
            }
        })
        client_socket.sendall(upload_message.encode('utf-8'))

        with open(filepath, 'rb') as file:
            while True:
                chunk = file.read(CHUNK)
                if not chunk:
                    break
                client_socket.sendall(chunk)
    else:
        print(f'{filepath} does not exist!')


def download_file(client_socket, data):
    filename = data['payload']['file_name']
    filesize = data['payload']['file_size']

    filepath = os.path.join('CLIENT_MEDIA', filename)
    mode = 'wb' if not os.path.exists(filepath) else 'ab'

    with open(filepath, mode) as received_file:
        while filesize > 0:
            chunk = client_socket.recv(min(filesize, CHUNK))
            if not chunk:
                break
            received_file.write(chunk)
            filesize -= len(chunk)

    print(f"'{filename}' has been downloaded")


def main():
    name, room = connect_to_server()

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()

    print(f"\nEnter a message (or 'exit' to quit).\
            \nType 'upload: <file-path>' to upload a file.\
            \nType 'download: <file-name>' to download a file.\n")
    
    while True:
        message = input()
        if message.lower() == 'exit':
            data = json.dumps({
                "type": "disconnect",
                "payload": {
                    "name": name,
                    "room": room
                }
            })
            client_socket.sendall(data.encode('utf-8'))
            break

        if re.match(r'upload: ([A-Za-z\./]+)', message):
            upload_thread = threading.Thread(target=upload_file, args=(message.split(' ')[-1], name, room))   
            upload_thread.start() 
            upload_thread.join()
        elif re.match(r'download: ([A-Za-z\.]+)', message):
            download_message = json.dumps({
                "type": "download",
                "payload": {
                    "file_name": message.split(' ')[-1],
                }
            })
            client_socket.sendall(download_message.encode('utf-8'))
        else: 
            send_messages(name, room, message)

    client_socket.close()


main()
