# =========================
# client.py
# MODERN FIXED VERSION
# =========================

import socket
import threading
import tkinter as tk

from tkinter import (
    messagebox,
    Toplevel
)

from tkinter.scrolledtext import ScrolledText

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

import uuid

from config import HOST, PORT

from rsa_utils import encrypt_key

from crypto_utils import (
    encrypt_message,
    decrypt_message
)

from auth import (
    signup,
    login,
    create_users_table
)


class ChatApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Secure Messenger"
        )

        self.root.geometry(
            "1200x720"
        )

        self.root.configure(
            bg="#0B141A"
        )

        self.root.minsize(
            900,
            600
        )

        # =========================
        # AUTH WINDOW
        # =========================

        create_users_table()

        auth_window = Toplevel()

        auth_window.title(
            "Authentication"
        )

        auth_window.geometry(
            "350x320"
        )

        auth_window.configure(
            bg="#111B21"
        )

        auth_window.grab_set()

        self.username = None

        # TITLE
        title = tk.Label(
            auth_window,
            text="Secure Messenger",
            bg="#111B21",
            fg="#25D366",
            font=("Segoe UI", 18, "bold")
        )

        title.pack(
            pady=25
        )

        # USERNAME
        username_entry = tk.Entry(
            auth_window,
            font=("Segoe UI", 11),
            width=25
        )

        username_entry.pack(
            pady=10,
            ipady=5
        )

        username_entry.insert(
            0,
            "Username"
        )

        # PASSWORD
        password_entry = tk.Entry(
            auth_window,
            font=("Segoe UI", 11),
            width=25,
            show="*"
        )

        password_entry.pack(
            pady=10,
            ipady=5
        )

        # LOGIN
        def do_login():

            username = username_entry.get(
            ).strip().lower()

            password = password_entry.get()

            if not username or not password:

                messagebox.showerror(
                    "Error",
                    "Fill all fields"
                )

                return

            success = login(
                username,
                password
            )

            if not success:

                messagebox.showerror(
                    "Error",
                    "Invalid login"
                )

                return

            self.username = username

            auth_window.destroy()

        # SIGNUP
        def do_signup():

            username = username_entry.get(
            ).strip().lower()

            password = password_entry.get()

            if not username or not password:

                messagebox.showerror(
                    "Error",
                    "Fill all fields"
                )

                return

            success = signup(
                username,
                password
            )

            if not success:

                messagebox.showerror(
                    "Error",
                    "Username exists"
                )

                return

            messagebox.showinfo(
                "Success",
                "Signup successful"
            )

            self.username = username

            auth_window.destroy()

        # BUTTON FRAME
        btn_frame = tk.Frame(
            auth_window,
            bg="#111B21"
        )

        btn_frame.pack(
            pady=20
        )

        # LOGIN BUTTON
        login_btn = tk.Button(
            btn_frame,
            text="Login",
            bg="#25D366",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=12,
            border=0,
            command=do_login
        )

        login_btn.pack(
            side=tk.LEFT,
            padx=10
        )

        # SIGNUP BUTTON
        signup_btn = tk.Button(
            btn_frame,
            text="Signup",
            bg="#202C33",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=12,
            border=0,
            command=do_signup
        )

        signup_btn.pack(
            side=tk.RIGHT,
            padx=10
        )

        self.root.wait_window(
            auth_window
        )

        if not self.username:

            exit()

        # =========================
        # VARIABLES
        # =========================

        self.selected_user = None

        self.chats = {}

        # =========================
        # SOCKET
        # =========================

        self.client = socket.socket()

        self.client.connect(
            (HOST, PORT)
        )

        # RECEIVE PUBLIC KEY
        public_key = RSA.import_key(
            self.recv_packet()
        )

        # AES KEY
        self.aes_key = get_random_bytes(16)

        encrypted_key = encrypt_key(
            self.aes_key,
            public_key
        )

        self.send_packet(
            encrypted_key
        )

        # SEND USERNAME
        self.send_packet(
            self.username.encode()
        )

        # =========================
        # SIDEBAR
        # =========================

        sidebar = tk.Frame(
            root,
            bg="#202C33",
            width=320
        )

        sidebar.pack(
            side=tk.LEFT,
            fill=tk.Y
        )

        # LOGO
        logo = tk.Label(
            sidebar,
            text="Secure Messenger",
            bg="#202C33",
            fg="#25D366",
            font=("Segoe UI", 18, "bold")
        )

        logo.pack(
            pady=20
        )

        # SEARCH
        search_entry = tk.Entry(
            sidebar,
            bg="#2A3942",
            fg="white",
            relief=tk.FLAT,
            insertbackground="white",
            font=("Segoe UI", 10)
        )

        search_entry.pack(
            fill=tk.X,
            padx=10,
            pady=10,
            ipady=8
        )

        # USER LIST
        self.users = tk.Listbox(
            sidebar,
            bg="#202C33",
            fg="white",
            selectbackground="#25D366",
            selectforeground="white",
            font=("Segoe UI", 11),
            border=0,
            activestyle="none"
        )

        self.users.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

        self.users.bind(
            "<<ListboxSelect>>",
            self.select_user
        )

        # =========================
        # CHAT AREA
        # =========================

        chat_container = tk.Frame(
            root,
            bg="#0B141A"
        )

        chat_container.pack(
            side=tk.RIGHT,
            fill=tk.BOTH,
            expand=True
        )

        # HEADER
        header = tk.Frame(
            chat_container,
            bg="#202C33",
            height=70
        )

        header.pack(
            fill=tk.X
        )

        self.chat_title = tk.Label(
            header,
            text="Select a user",
            bg="#202C33",
            fg="white",
            font=("Segoe UI", 14, "bold")
        )

        self.chat_title.pack(
            side=tk.LEFT,
            padx=20,
            pady=15
        )

        # CHAT BOX
        self.chat = ScrolledText(
            chat_container,
            bg="#0B141A",
            fg="white",
            font=("Segoe UI", 11),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0,
            insertbackground="white",
            padx=15,
            pady=15
        )

        self.chat.pack(
            fill=tk.BOTH,
            expand=True
        )

        self.chat.tag_configure(
            "sent",
            foreground="white"
        )

        self.chat.tag_configure(
            "received",
            foreground="#25D366"
        )

        self.chat.config(
            state=tk.DISABLED
        )

        # =========================
        # BOTTOM BAR
        # =========================

        bottom = tk.Frame(
            chat_container,
            bg="#202C33",
            height=75
        )

        bottom.pack(
            fill=tk.X
        )

        # MESSAGE ENTRY
        self.entry = tk.Entry(
            bottom,
            bg="#2A3942",
            fg="white",
            relief=tk.FLAT,
            insertbackground="white",
            font=("Segoe UI", 11)
        )

        self.entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=15,
            pady=15,
            ipady=10
        )

        self.entry.bind(
            "<Return>",
            self.send_message
        )

        # SEND BUTTON
        send_btn = tk.Button(
            bottom,
            text="➤",
            bg="#25D366",
            fg="white",
            activebackground="#20BD5A",
            activeforeground="white",
            relief=tk.FLAT,
            font=("Segoe UI", 16, "bold"),
            width=3,
            command=self.send_message,
            cursor="hand2"
        )

        send_btn.pack(
            side=tk.RIGHT,
            padx=15,
            pady=10
        )

        # RECEIVE THREAD
        threading.Thread(
            target=self.receive,
            daemon=True
        ).start()

    # =========================
    # SEND PACKET
    # =========================

    def send_packet(self, data):

        self.client.sendall(
            len(data).to_bytes(4, 'big') + data
        )

    # =========================
    # RECEIVE PACKET
    # =========================

    def recv_packet(self):

        header = self.client.recv(4)

        if not header:

            return None

        length = int.from_bytes(
            header,
            'big'
        )

        data = b""

        while len(data) < length:

            chunk = self.client.recv(
                length - len(data)
            )

            if not chunk:

                return None

            data += chunk

        return data

    # =========================
    # UPDATE USERS
    # =========================

    def update_users(self, users):

        self.users.delete(
            0,
            tk.END
        )

        for user in users:

            if user != self.username:

                self.users.insert(
                    tk.END,
                    user
                )

    # =========================
    # SELECT USER
    # =========================

    def select_user(self, e):

        try:

            self.selected_user = self.users.get(
                self.users.curselection()
            )

            self.chat_title.config(
                text=self.selected_user
            )

            self.load_chat()

        except:

            pass

    # =========================
    # LOAD CHAT
    # =========================

    def load_chat(self):

        self.chat.config(
            state=tk.NORMAL
        )

        self.chat.delete(
            1.0,
            tk.END
        )

        if self.selected_user in self.chats:

            for msg, tag in self.chats[
                self.selected_user
            ]:

                self.chat.insert(
                    tk.END,
                    msg + "\n\n",
                    tag
                )

        self.chat.see(
            tk.END
        )

        self.chat.config(
            state=tk.DISABLED
        )

    # =========================
    # SEND MESSAGE
    # =========================

    def send_message(self, e=None):

        if not self.selected_user:

            return

        msg = self.entry.get().strip()

        if not msg:

            return

        msg_id = str(
            uuid.uuid4()
        )[:8]

        text = (
            f"MSG|{msg_id}|"
            f"{self.username}|"
            f"{self.selected_user}|"
            f"{msg}"
        )

        encrypted = encrypt_message(
            text,
            self.aes_key
        )

        self.send_packet(
            encrypted
        )

        display = f"You: {msg}"

        self.chats.setdefault(
            self.selected_user,
            []
        ).append(
            (
                display,
                "sent"
            )
        )

        self.load_chat()

        self.entry.delete(
            0,
            tk.END
        )

    # =========================
    # RECEIVE
    # =========================

    def receive(self):

        while True:

            try:

                data = self.recv_packet()

                if not data:

                    break

                # USER LIST
                if data.startswith(
                    b"__USERS__"
                ):

                    users = data.decode().split(
                        "|"
                    )[1].split(",")

                    self.root.after(
                        0,
                        self.update_users,
                        users
                    )

                    continue

                # DECRYPT
                text = decrypt_message(
                    data,
                    self.aes_key
                )

                parts = text.split(
                    "|",
                    4
                )

                msg_type = parts[0]

                # MESSAGE
                if msg_type == "MSG":

                    sender = parts[2]

                    receiver = parts[3]

                    message = parts[4]

                    if receiver == self.username:

                        display = (
                            f"{sender}: "
                            f"{message}"
                        )

                        self.chats.setdefault(
                            sender,
                            []
                        ).append(
                            (
                                display,
                                "received"
                            )
                        )

                        self.root.after(
                            0,
                            self.load_chat
                        )

            except Exception as e:

                print(
                    "ERROR:",
                    e
                )

                break


# =========================
# START APP
# =========================

root = tk.Tk()

app = ChatApp(root)

root.mainloop()