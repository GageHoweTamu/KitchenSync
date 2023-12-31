from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import paramiko
import os
import getpass
import requests
import socket
import paramiko
from kivy.uix.popup import Popup
from kivy.core.window import Window
from paramiko import SSHClient

getterInstance = None
hostInstance = None
pw = None



def get_current_username():
    try:
        username = getpass.getuser()
        return username
    except Exception as e:
        getterInstance.root.printc(f"Error getting username: {e}")
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
        getterInstance.root.printc(f"Error: {e}")
        return "get_public_ip failed"

'''
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
        getterInstance.root.printc("Authentication failed. Please check your username and password.")
    except paramiko.SSHException as e:
        getterInstance.root.printc(f"Unable to establish SSH connection: {e}")
    except Exception as e:
        getterInstance.root.printc(f"An unexpected error occurred: {e}")
    finally:
        if ssh:
            ssh.close()

    return None
'''

def connect_ssh(username):
    client = SSHClient()
    client.load_system_host_keys() # if necessary
    #client.load_host_keys('~/.ssh/known_hosts') # from file, not used
    client.set_missing_host_key_policy(AutoAddPolicy()) # updates known hosts
    client.connect('98.44.42.172', username='gage', password='Unresponsi1!')
    client.close()

################################################################ App selector

class AppSelector(BoxLayout):
    def __init__(self, **kwargs):
        super(AppSelector, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.host_button = Button(text='Sync files from this machine to another (Host)', on_press=self.run_host_app)
        self.getter_button = Button(text='Sync files from another machine (Fetch)', on_press=self.run_getter_app)

        self.add_widget(self.host_button)
        self.add_widget(self.getter_button)

    def run_host_app(self, getterInstance):
        MyAppHost().run()

    def run_getter_app(self, getterInstance):
        MyAppGetter().run()

    def exit_app(self):
       App.get_running_app().stop() # Add this method

class AppSelectorApp(App):
    def build(self):
        return AppSelector()

################################################################ Getter app

class AppLayoutGetter(BoxLayout):
    def __init__(self, **kwargs):
        super(AppLayoutGetter, self).__init__(**kwargs)

        Window.bind(on_dropfile=self._on_file_drop)

        self.orientation = 'horizontal'

        left_layout = BoxLayout(orientation='vertical')
        right_layout = BoxLayout(orientation='vertical')

        self.host_input = TextInput(hint_text='IP address')
        self.username_input = TextInput(hint_text='Username')
        self.password_input = TextInput(hint_text='Password', password=True)

        directory_layout = BoxLayout(orientation='horizontal')
        self.directory_input = TextInput(hint_text='folder to sync to (you can drag and drop a folder here)')
        directory_layout.add_widget(self.directory_input)

        self.dest_host_inputG = TextInput(hint_text='Destination IP address')
        self.dest_username_inputG = TextInput(hint_text='Destination Username')
        self.dest_password_inputG = TextInput(hint_text='Destination Password', password=True)

        self.sync_from_button = Button(text='Sync from Remote')
        self.sync_from_button.bind(on_press=self.sync_from_remote)

        self.host_directory = TextInput(hint_text='Host folder/file')

        left_layout.add_widget(self.host_input)
        left_layout.add_widget(self.dest_host_inputG)
        
        left_layout.add_widget(self.username_input)
        left_layout.add_widget(self.dest_username_inputG)

        left_layout.add_widget(directory_layout)
        left_layout.add_widget(self.host_directory)

        left_layout.add_widget(self.password_input)
        left_layout.add_widget(self.dest_password_inputG)

        right_layout.add_widget(self.sync_from_button)

        self.console_output = TextInput(readonly=True, multiline=True)
        self.console_output.size_hint = (1, 2)

        self.add_widget(left_layout)
        right_layout.add_widget(self.console_output)
        self.add_widget(right_layout)
        
    def _on_file_drop(self, window, file_path):
        self.directory_input.text = file_path

    def printc(self, message):
        current_text = self.console_output.text
        self.console_output.text = f"{current_text}\n{message}"
    
    def sync_from_remote(self, instance):
        host = self.host_input.text
        username = self.username_input.text
        password = self.password_input.text
        remote_directory = self.directory_input.text
        local_directory = self.host_directory.text

        try:
            transport = paramiko.Transport((host, 22))
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)

            sftp.get(remote_directory, local_directory)

            self.printc("File synchronization successful.")
        except Exception as e:
            self.printc(f"Error during synchronization: {e}")
        finally:
            if 'sftp' in locals():
                sftp.close()
            if 'transport' in locals():
                transport.close()

class MyAppGetter(App):
    def build(self):
        global getterInstance
        getterInstance = self
        return AppLayoutGetter()
    def on_start(self):
        self.root.printc("Welcome to KitchenSync.")
        self.root.printc(f"This machine's IP: {get_public_ip()}")
        self.root.printc(f"This machine's Username: {get_current_username()}")
        #port = get_ssh_port(pw)
        #if port == 22:
        #    self.root.printc(f"This machine's Port: default")
        #else: self.root.printc(f"This machine's Port: {port}")

        self.root.host_input.text = get_public_ip()
        self.root.username_input.text = get_current_username()

###################################################################################### Host app

class AppLayoutHost(BoxLayout):                              # fix this
    def __init__(self, **kwargs):
        super(AppLayoutHost, self).__init__(**kwargs)

        Window.bind(on_dropfile=self._on_file_drop)

        self.orientation = 'horizontal'

        left_layout = BoxLayout(orientation='vertical')
        right_layout = BoxLayout(orientation='vertical')

        self.host_input = TextInput(hint_text='IP address')
        self.username_input = TextInput(hint_text='Name')                   # this client
        self.password_input = TextInput(hint_text='Password', password=True)

        directory_layout = BoxLayout(orientation='horizontal') # this client

        self.host_directory = TextInput(hint_text='drag and a drop folder/file to show its directory')

        left_layout.add_widget(self.host_input)
        left_layout.add_widget(self.username_input)
        left_layout.add_widget(self.host_directory)

        self.console_output = TextInput(readonly=True, multiline=True)
        self.console_output.size_hint = (1, 2)

        self.add_widget(left_layout)
        right_layout.add_widget(self.console_output)
        self.add_widget(right_layout)
        
    def _on_file_drop(self, window, file_path):
        self.host_directory.text = file_path
    
    def printc(self, message):
        current_text = self.console_output.text
        self.console_output.text = f"{current_text}\n{message}"

class MyAppHost(App):
    def build(self):
        global hostInstance
        hostInstance = self
        return AppLayoutHost()
    def on_start(self):
        self.root.printc("Welcome to KitchenSync.")
        self.root.printc(f"This machine's IP: {get_public_ip()}")
        self.root.printc(f"This machine's Username: {get_current_username()}")

        self.root.printc("Input these on another client to sync your files.")

        self.root.host_input.text = get_public_ip()
        self.root.username_input.text = get_current_username()

###################################################################################### Runtime

if __name__ == '__main__':
    AppSelectorApp().run()
