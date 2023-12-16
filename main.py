from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import paramiko
import os
import getpass
import requests
import tkinter as tk
from tkinter import filedialog
import socket
import paramiko
from dotenv import load_dotenv
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
import threading

instance = None

def select_directory():
    def run_dialog():
        root = tk.Tk()
        root.withdraw()
        folder_selected = filedialog.askdirectory()
        instance.root.directory_input.text = folder_selected
    thread = threading.Thread(target=run_dialog)
    thread.start()

'''
def select_directory(callback):
    file_chooser = FileChooserListView()
    file_chooser.bind(on_submit=lambda instance, x: callback(x[0]))
    popup = Popup(title='Select Directory', content=file_chooser, size_hint=(None, None), size=(600, 400))
    popup.open()

def get_directory(path):
    from kivy.clock import Clock
    Clock.schedule_once(lambda dt: setattr(instance.root.directory_input, 'text', path))
'''
def get_current_username():
    try:
        username = getpass.getuser()
        return username
    except Exception as e:
        instance.root.printc(f"Error getting username: {e}")
        return None

def get_public_ip():
    try:
        response = requests.get('https://api64.ipify.org?format=json')
        if response.status_code == 200:
            ip_address = response.json()['ip']
            return ip_address
        else:
            return "get_public_ip failed"
    except Exception as e:
        instance.root.printc(f"Error: {e}")
        return "get_public_ip failed"

def get_ssh_port(password):
    username = get_current_username()
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('localhost', username=username, password=password)

        transport = ssh.get_transport()
        ssh_port = transport.getpeername()[1]

        return ssh_port

    except paramiko.AuthenticationException:
        instance.root.printc("Authentication failed. Please check your username and password.")
    except paramiko.SSHException as e:
        instance.root.printc(f"Unable to establish SSH connection: {e}")
    except Exception as e:
        instance.root.printc(f"An unexpected error occurred: {e}")
    finally:
        if ssh:
            ssh.close()

    return None

################################################################ App selector

class AppSelector(BoxLayout):
    def __init__(self, **kwargs):
        super(AppSelector, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.host_button = Button(text='Sync files from this machine to another', on_press=self.run_host_app)
        self.getter_button = Button(text='Sync files from another machine', on_press=self.run_getter_app)

        self.add_widget(self.host_button)
        self.add_widget(self.getter_button)

    def run_host_app(self, instance):
        MyAppHost().run()

    def run_getter_app(self, instance):
        MyAppGetter().run()

class AppSelectorApp(App):
    def build(self):
        return AppSelector()

################################################################ Getter app

class AppLayoutGetter(BoxLayout):
    def __init__(self, **kwargs):
        super(AppLayoutGetter, self).__init__(**kwargs)
        self.orientation = 'horizontal'

        left_layout = BoxLayout(orientation='vertical')
        right_layout = BoxLayout(orientation='vertical')

        self.host_input = TextInput(hint_text='IP address')
        self.username_input = TextInput(hint_text='Name')
        self.password_input = TextInput(hint_text='Password', password=True)

        directory_layout = BoxLayout(orientation='horizontal')
        self.directory_input = TextInput(hint_text='Directory')
        self.select_directory_button = Button(text='Select Directory', on_press=self.select_directory_getter)
        directory_layout.add_widget(self.directory_input)
        directory_layout.add_widget(self.select_directory_button)

        self.dest_host_input = TextInput(hint_text='Destination IP address')
        self.dest_username_input = TextInput(hint_text='Destination name')
        self.dest_password_input = TextInput(hint_text='Destination password', password=True)

        self.sync_from_button = Button(text='Sync from Remote')

        self.sync_from_button.bind(on_press=self.sync_from_remote)

        left_layout.add_widget(self.host_input)
        left_layout.add_widget(self.username_input)
        left_layout.add_widget(self.password_input)
        left_layout.add_widget(directory_layout)
        left_layout.add_widget(self.dest_host_input)
        left_layout.add_widget(self.dest_username_input)
        left_layout.add_widget(self.dest_password_input)

        right_layout.add_widget(self.sync_from_button)

        self.console_output = TextInput(readonly=True, multiline=True)
        self.console_output.size_hint = (1, 2)

        self.add_widget(left_layout)
        right_layout.add_widget(self.console_output)
        self.add_widget(right_layout)

    def select_directory_getter(self, instance):
        self.directory_input.text = select_directory()

    def connect_to_ssh(self, host, username, password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host=get_public_ip, username=get_current_username, password=password)
        return ssh

    def test_message(self, message):
        current_text = self.console_output.text
        self.console_output.text = f"{current_text}\n{message}"

    def sync_to_remote(self, instance):
        local_directory = self.directory_input.text
        remote_directory = '/remote/directory/path'  # Adjust this path on the remote machine
        ssh = self.connect_to_ssh(self.host_input.text, self.username_input.text, self.password_input.text)
        sftp = ssh.open_sftp()
        sftp.put(local_directory, remote_directory)
        sftp.close()
        ssh.close()
        self.printc("Sync to remote initiated.")

    def sync_from_remote(self, instance):
        local_directory = select_directory
        remote_directory = self.directory_input.text
        ssh = self.connect_to_ssh(self.dest_host_input.text, self.dest_username_input.text, self.dest_password_input.text)
        sftp = ssh.open_sftp()
        sftp.get(remote_directory, local_directory)
        sftp.close()
        ssh.close()
        self.printc("Sync from remote initiated.")
    
    def printc(self, message):
        current_text = self.console_output.text
        self.console_output.text = f"{current_text}\n{message}"

class MyAppGetter(App):
    def build(self):
        global instance
        instance = self
        return AppLayoutGetter()
    def on_start(self):
        self.root.printc("Welcome to KitchenSync.")
        self.root.printc(f"This machine's IP: {get_public_ip()}")
        self.root.printc(f"This machine's Username: {get_current_username()}")
        self.root.printc(f"This machine's Port: {get_ssh_port('Gage h slack1!')}")

        self.root.host_input.text = get_public_ip()
        self.root.username_input.text = get_current_username()
        self.root.directory_input.text = select_directory()
        # self.root.directory_input.text = select_directory() # temporary

if __name__ == '__main__':

    AppSelectorApp().run()
