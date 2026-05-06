import socket
import threading
import time
from datetime import datetime

from config import HOST, PORT
from rsa_utils import generate_keys, decrypt_key
from crypto_utils import (
    decrypt_message,
    encrypt_message
)
from database import init_db, save_message

clients = {}

private_key, public_key = generate_keys()

init_db()


def send_packet(sock, data):

    sock.sendall(
        len(data).to_bytes(4, 'big') + data
    )


def recv_packet(sock):

    header = sock.recv(4)

    if not header:
        return None

    length = int.from_bytes(header, 'big')

    data = b""

    while len(data) < length:

        chunk = sock.recv(length - len(data))

        if not chunk:
            return None

        data += chunk

    return data


def broadcast_users():

    users = ",".join(clients.keys())

    msg = f"__USERS__|{users}".encode()

    for user, info in list(clients.items()):

        try:

            send_packet(
                info["socket"],
                msg
            )

        except:
            pass


def handle_client(client):

    username = None

    try:

        # SEND RSA PUBLIC KEY
        send_packet(
            client,
            public_key.export_key()
        )

        # RECEIVE AES KEY
        encrypted_key = recv_packet(client)

        aes_key = decrypt_key(
            encrypted_key,
            private_key
        )

        # RECEIVE USERNAME
        username = recv_packet(client).decode()

        username = username.strip().lower()

        clients[username] = {
            "socket": client,
            "aes": aes_key
        }

        print(f"[CONNECTED] {username}")

        time.sleep(0.2)

        broadcast_users()

        while True:

            encrypted_data = recv_packet(client)

            if not encrypted_data:
                break

            text = decrypt_message(
                encrypted_data,
                aes_key
            )

            parts = text.split("|", 4)

            msg_type = parts[0]

            # MESSAGE
            if msg_type == "MSG":

                msg_id = parts[1]
                sender = parts[2]
                receiver = parts[3]
                message = parts[4]

                print(
                    f"{sender} -> {receiver}: {message}"
                )

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                save_message(
                    sender,
                    receiver,
                    message,
                    timestamp
                )

                # DELIVERED
                if sender in clients:

                    sender_key = clients[
                        sender
                    ]["aes"]

                    ack = f"DELIVERED|{msg_id}"

                    encrypted_ack = encrypt_message(
                        ack,
                        sender_key
                    )

                    send_packet(
                        clients[sender]["socket"],
                        encrypted_ack
                    )

                # SEND TO RECEIVER
                if receiver in clients:

                    receiver_key = clients[
                        receiver
                    ]["aes"]

                    re_encrypted = encrypt_message(
                        text,
                        receiver_key
                    )

                    send_packet(
                        clients[receiver]["socket"],
                        re_encrypted
                    )

            # TYPING
            elif msg_type == "TYPING":

                sender = parts[1]
                receiver = parts[2]

                if receiver in clients:

                    receiver_key = clients[
                        receiver
                    ]["aes"]

                    re_encrypted = encrypt_message(
                        text,
                        receiver_key
                    )

                    send_packet(
                        clients[receiver]["socket"],
                        re_encrypted
                    )

            # SEEN
            elif msg_type == "SEEN":

                msg_id = parts[1]
                sender = parts[2]

                if sender in clients:

                    sender_key = clients[
                        sender
                    ]["aes"]

                    re_encrypted = encrypt_message(
                        text,
                        sender_key
                    )

                    send_packet(
                        clients[sender]["socket"],
                        re_encrypted
                    )

    except Exception as e:

        print("[ERROR]", e)

    finally:

        if username and username in clients:

            del clients[username]

            print(f"[DISCONNECTED] {username}")

            broadcast_users()

        client.close()


def start_server():

    s = socket.socket()

    s.bind((HOST, PORT))

    s.listen(5)

    print("[SERVER RUNNING]")

    while True:

        client, _ = s.accept()

        threading.Thread(
            target=handle_client,
            args=(client,),
            daemon=True
        ).start()


if __name__ == "__main__":
    start_server()