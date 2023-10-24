import socket
import threading
import json
import os

if not os.path.isdir('SERVER_MEDIA'):
    os.mkdir('SERVER_MEDIA')
CHUNK = 1024

HOST = '127.0.0.1'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f'Server is listening on {HOST}:{PORT}')


def handle_client(client_socket, client_address, clients, rooms):
    print(f'Accepted connection from {client_address}')

    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break

        print(f'Received from {client_address}: {message}')
        data = json.loads(message)
        message_type = data['type']

        if message_type == 'connect':
            handle_connect(client_socket, data, clients, rooms)
        elif message_type == 'disconnect':
            disconnect_client(client_socket, data, clients, rooms)
        elif message_type == 'message':
            send_broadcast_message(client_socket, clients, rooms, message.encode('utf-8'))
        elif message_type == 'upload':
            upload_thread = threading.Thread(target=upload_file, args=(client_socket, data, clients, rooms))
            upload_thread.start()
            upload_thread.join()
        elif data['type'] == 'download':
            stream_thread = threading.Thread(target=download_file, args=(client_socket, data))
            stream_thread.start()
            stream_thread.join()


def handle_connect(client_socket, data, clients, rooms):
    message = json.dumps({
        "type": "connect_ack",
        "payload": {
            "message": f"\nConnected to the room.\n"
        }
    })
    client_socket.send(message.encode('utf-8'))

    room = data['payload']['room']
    if room not in rooms:
        rooms[room] = set()

    rooms[room].add(client_socket)

    notification_message = json.dumps({
        "type": "notification",
        "payload": {
            "message": f"{data['payload']['name']} has joined the room.\n"
        }
    })
    send_broadcast_message(client_socket, clients, rooms, notification_message.encode('utf-8'))


def disconnect_client(client_socket, data, clients, rooms):
    clients.remove(client_socket)

    notification_message = json.dumps({
        "type": "notification",
        "payload": {
            "message": f"{data['payload']['name']} left the room.\n"
        }
    })
    send_broadcast_message(client_socket, clients, rooms, notification_message.encode('utf-8'))

    for room in rooms:
        if room == data['payload']['room']:
            rooms[room].remove(client_socket)
            break


def send_broadcast_message(client_socket, clients, rooms, data):
    for client in clients:
        if client != client_socket:
            for room in rooms:
                if (client in rooms[room]) and (client_socket in rooms[room]):
                    client.sendall(data)
                    break


def upload_file(client_socket, data, clients, rooms):
    filename = data['payload']['file_name']
    filesize = data['payload']['file_size']

    filepath = f"{'SERVER_MEDIA'}/{data['payload']['file_name']}"

    if os.path.exists(filepath):
        option = 'wb' 
    else:
        option = 'xb'

    with open(filepath, option) as received_file:
        index = 0
        while index < filesize:
            chunk = client_socket.recv(CHUNK)
            received_file.write(chunk)
            index += len(chunk)

    notification_message = json.dumps({
        "type": "notification",
        "payload": {
            "message": f"{data['payload']['name']} uploaded {filename}.\n"
        }
    })
    send_broadcast_message(client_socket, clients, rooms, notification_message.encode('utf-8'))

    upload_message = json.dumps({
        "type": "notification",
        "payload": {
            "message": f"{filename} uploaded\n"
        }
    })
    client_socket.sendall(upload_message.encode('utf-8'))


def download_file(client_socket, data):
    filename = data['payload']['file_name']
    filepath = os.path.join('SERVER_MEDIA', filename)

    if os.path.exists(filepath):
        filesize = os.path.getsize(filepath)

        download_ack_message = json.dumps({
            "type": "download-ack",
            "payload": {
                "file_name": filename,
                "file_size": filesize
            }
        })
        client_socket.sendall(download_ack_message.encode('utf-8'))

        with open(filepath, 'rb') as file:
            while filesize > 0:
                chunk = file.read(min(filesize, CHUNK))
                client_socket.sendall(chunk)
                filesize -= len(chunk)
    else:
        not_found_message = json.dumps({
            "type": "notification",
            "payload": {
                "message": f"'{filename}' does not exist\n"
            }
        })
        client_socket.sendall(not_found_message.encode('utf-8'))


def main():
    clients = []
    rooms = {}
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, clients, rooms))
        client_thread.start()


main()
