import multiprocessing
import os

import tkinter as tk
from tkinter import NW, LEFT
import sys

import queue

import pyAesCrypt

# from os import cpu_count
METHOD_TYPE = ['decrypt', 'encrypt']
fields_decrypt = [['Method Type', 'Decrypt'], ['File Path', None]]

fields_encrypt = [['Method Type', 'Encrypt'], ['File Path', None]]

from tkinter import (Tk, BOTH, E,
                     NORMAL, DISABLED)
from tkinter.ttk import Frame, Label

from multiprocessing import Process, Queue
from queue import Empty

DELAY1 = 80
DELAY2 = 20

# Queue must be global
queue = Queue()
message = None
encrypt_code = 'gdsh@#45chjsdcs'
buffer_size = 64 * 1024


def decrypt_dir(queue, src):
    if os.path.isdir(src):
        list_dir = os.listdir(src)
        for file in list_dir:
            file_path = '{}/{}'.format(src, file)
            if os.path.isdir(file_path):
                decrypt_dir(queue, file_path)
            else:
                decrypt_file = '{}/{}'.format(src, file)
                encrypt_file = '{}/{}'.format(src, file.replace('.', '_decryp.'))
                os.rename(decrypt_file, encrypt_file)
                message = "Decrpting: {}".format(encrypt_file)
                queue.put(message)
                print("Decrpting: {}".format(encrypt_file))
                pyAesCrypt.decryptFile(encrypt_file, decrypt_file, encrypt_code, buffer_size)
                os.remove(encrypt_file)
    else:
        decrypt_file = src.replace('.', '_decryp.')
        os.rename(src, decrypt_file)
        pyAesCrypt.decryptFile(decrypt_file, src, encrypt_code, buffer_size)
        os.remove(decrypt_file)


def encrypt_dir(queue, src):
    if os.path.isdir(src):
        list_dir = os.listdir(src)
        for file in list_dir:
            file_path = '{}/{}'.format(src, file)
            if os.path.isdir(file_path):
                encrypt_dir(queue, file_path)
            else:
                encrypt_file = '{}/{}'.format(src, file)
                unencrypt_file = '{}/{}'.format(src, file.replace('.', '_decryp.'))
                os.rename(encrypt_file, unencrypt_file)
                message = "Encrpting: {}".format(encrypt_file)
                queue.put(message)
                print("Encrpting: {}".format(encrypt_file))
                pyAesCrypt.encryptFile(unencrypt_file, encrypt_file, encrypt_code, buffer_size)
                os.remove(unencrypt_file)
    else:
        unencrypt_file = src.replace('.', '_decryp.')
        os.rename(src, unencrypt_file)
        pyAesCrypt.encryptFile(unencrypt_file, src, encrypt_code, buffer_size)
        os.remove(unencrypt_file)


class Method(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent, name="frame")

        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.parent.title("File Encrypt/Decrypt")
        self.pack(fill=BOTH, expand=True)
        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.lbl1 = Label(self, text="Method Type:", anchor=NW, justify=LEFT)
        self.lbl1.grid(row=0, column=0, sticky=E, padx=20, pady=0)
        self.radiovar = tk.IntVar()
        self.labelvar = tk.StringVar()
        self.entries = {}
        self.labels = {}
        self.frame = None
        self.copy_button = None
        self.quit_button = None
        self.initial_parent = self.parent
        for index, text in enumerate(METHOD_TYPE):
            button = tk.Radiobutton(
                self,
                text=text,
                variable=self.radiovar,
                value=index,
                command=self.on_choose)
            button.grid(row=0, column=index+1, padx=0, pady=5, sticky=tk.W)
        self.on_choose()
        self.labelvar = self.radiovar.get()
        row = tk.Frame(self.initial_parent)
        self.message_box = None
        self.rowconfigure(4, pad=2)
        self.destination = None

    def make_form(self, fields):
        self.destroy_form()

        for field in fields:
            print(field)
            row = tk.Frame(self.initial_parent)
            lab = tk.Label(row, width=22, text=field[0] + ": ", anchor='w')
            ent = tk.Entry(row)
            row.pack(side=tk.TOP,
                     fill=tk.X,
                     padx=5,
                     pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT,
                     expand=tk.YES,
                     fill=tk.X)
            if field[1]:
                ent.insert(1, field[1])
            self.entries[field[0]] = ent
            self.labels[field[0]] = lab
        row = tk.Frame(self.initial_parent)
        row.pack(side=tk.TOP,
                 fill=tk.X,
                 padx=5,
                 pady=5)
        lab = tk.Label(row, width=50, text="", anchor='w', fg='blue')
        lab.pack(side=tk.LEFT)
        self.labels['Status'] = lab

    def destroy_form(self):
        for i in range(len(self.parent.children)*100):
            if i ==0 and self.parent.children.get('!frame'):
                self.parent.children.get('!frame').destroy()
            elif self.parent.children.get('!frame{}'.format(i+1)):
                self.parent.children.get('!frame{}'.format(i+1)).destroy()
            if i ==0 and self.parent.children.get('!button'):
                self.parent.children.get('!button').destroy()
            elif self.parent.children.get('!button{}'.format(i+1)):
                self.parent.children.get('!button{}'.format(i+1)).destroy()

    def on_choose(self):
        self.destroy_form()
        db_type = self.radiovar.get()
        field = fields_decrypt
        if db_type == 1:
            field = fields_encrypt
        self.make_form(field)
        self.buttons()

    def on_get_value(self):
        if (self.p1.is_alive()):
            self.after(DELAY1, self.on_get_value)
            if not queue.empty():
                self.labels['Status']['text'] = queue.get(0)
            return
        else:
            try:
                self.labels['Status']['text'] = ''
                self.copy_button.config(state=NORMAL)
            except Empty:
                print("queue is empty")

    def buttons(self):
        self.copy_button = tk.Button(self.parent, text='Start', fg='blue',
                       command=(lambda e=self.entries: self.base_method(e)))
        self.copy_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.quit_button = tk.Button(self.parent, text='Quit', command=self.parent.quit, fg='red')
        self.quit_button.pack(side=tk.LEFT, padx=5, pady=5)

    def base_method(self, entries):
        self.copy_button.config(state=DISABLED)
        method_type = entries['Method Type'].get()
        file_path = None
        if method_type == 'Decrypt':
            file_path = entries['File Path'].get()
            self.p1 = Process(target=decrypt_dir, args=(
            queue, file_path))
            self.p1.start()
            self.after(DELAY1, self.on_get_value)
        else:
            file_path = entries['File Path'].get()
            self.p1 = Process(target=encrypt_dir, args=(
            queue, file_path))
            self.p1.start()
            self.after(DELAY1, self.on_get_value)

def main():
    root = Tk()
    app = Method(root)
    root.mainloop()


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
    main()


