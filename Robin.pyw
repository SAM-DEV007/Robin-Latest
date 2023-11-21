import sounddevice as sd
import soundfile as sf

import datetime, random, time, json
import logging, subprocess, traceback
import os, sys, urllib
import librosa, wave, pyaudio
import pyttsx3, wolframalpha, vosk
import threading, queue

from requests_html import HTMLSession
from urllib import request
from contextlib import suppress
from PyQt6.QtWidgets import (
    QApplication, QFrame, QGraphicsDropShadowEffect, QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressBar, QPushButton, QScrollArea, QSizePolicy, QWidget
)
from PyQt6 import QtGui, uic, QtCore
from PyQt6.QtGui import QAction

#Functions
##Modules##
def speak(response="", additional=""):
    global response_val, additional_val, speak_txt

    response_val, additional_val = response, additional
    speak_txt = response_val + " " + additional_val
    response_val, additional_val = "", ""
    main_window._thread_speak.start()

def search_google(txt, ret=True):
    global main_window, additional_val

    cls = google_search_modules()
    res = cls.google_search(txt)

    for dictionary in res:
        response = (f"{dictionary['title']}:<br> <a href={dictionary['link']}>{dictionary['link']}</a>")
        additional_val = f"Here's what I found, showing the top search result"
        break

    if not response:
        response = ""

    main_window.robin.setOpenExternalLinks(True)
    if response == "":
        response = "Unable to understand!"
        additional_val = "Unable to understand"

    if ret is True:
        return response
    else:
        main_window.robin.setText(response)
        main_window.wait(2)
        speak(additional=additional_val)

def ai_wolfram(txt):
    global client

    try:
        response = client.query(txt)
        ans = next(response.results).text
        if ans != '(no data available)':
            return ans, None
        else:
            raise NameError
    except:
        text_ = search_google(txt)
        return text_, True

def random_gen(t):
    global response_val

    val = random.randint(0, len(t) - 1)
    response_val = t[val]
## ##

##Exception logging##
def time_format():
    global start, end

    if end is None:
        end = time.time()
    hrs, r = divmod(end-start, 3600)
    min , sec = divmod(r, 60)
    return f"{int(hrs):0>2}:{int(min):0>2}:{sec:05.2f}"

def check_sys():
    global new

    id = subprocess.check_output(['systeminfo'], stderr=subprocess.DEVNULL).decode('utf-8').split('\n')
    for item in id:
        new.append(str(item.split("\r")[:-1]))

def excepthook(exc_type, exc_value, exc_tb):
    global new, start, end, main_window, main_val

    #Setting up logger
    el_time = time_format()
    logger = logging.getLogger(__name__)
    file_name_time = datetime.datetime.now().strftime("%y-%m-%d %I-%M %p")
    location = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Logs\\", f"LOG {file_name_time}.log")
    handler = logging.FileHandler(filename=location)
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)

    #Formatting error
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    time = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")

    #Logging error
    logger.error(f"Time: {time} \nElapsed Time: {el_time} \n\nError message:\n {tb}")
    logger.error("-----------------    SYSTEM INFORMATION     -----------------")
    #Logging sys info
    for i in new:
        logger.error(i[2:-2])
    logger.error("-----------------    END     -----------------")

    if main_window and main_val is True:
        main_window.error_msg()

    exit()

def warn_logs(log_warn):
    global new

    #Setting up logger
    logger = logging.getLogger(__name__)
    file_name_time = datetime.datetime.now().strftime("%y-%m-%d %I-%M-%S %p")
    location = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Logs\\", f"LOG WARN {file_name_time}.log")
    handler = logging.FileHandler(filename=location)
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)

    #Formatting error
    time = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")

    #Logging error
    logger.error(f"Time: {time} \n\nWarning message:\n {log_warn}")
    logger.error("-----------------    SYSTEM INFORMATION     -----------------")
    #Logging sys info
    for i in new:
        logger.error(i[2:-2])
    logger.error("-----------------    END     -----------------")
## ##

#Responses
dictionary = {
    "hello_interaction": ("Hey", "Hello, human", "Hello, I am at your service", "Hi", "Greetings"),
    "asking_name_interaction": ("Hi, Robin here", "Hi, this is Robin", "I am Robin", "I am an AI Assistant named Robin",
                                "Hey, this is Robin"),
    "creator_interaction": ("I am created by Samyak", "My creator is Samyak", "Samyak is my owner and creator"),
    "how_are_you_interaction": ("I am fine!", "My systems are online and working perfectly fine!", "Me? Yeah, I'm fine!",
                                "I am great!"),
    "thank_you_interaction": ("Welcome!", "It's my duty", "My pleasure", "You're welcome"),
    "age_interaction": ("Well, I was created a long time ago and I don't even remember nor my creator",
                        "My creator doesn't know when I was created so I don't know")
}

commands = {
    "google": ("google search", "search google", "search"),
    "websites": ("open website", "search website"),
    "name": ("your name", "assistant name", "who are you"),
    "owner": ("owner", "creator", "created", "your god"),
    "well_being": ("how are you", "how's your day"),
    "gratitude": ("thanks", "thank you"),
    "hello": ("hello", "hey", "hi"),
    "my_name": ("my name",),
    "age": ("your age", "old are you", "you born"),
    "quit": ("quit", "shut down", "shutdown", "close", "exit", "goodbye", "bye", "goodnight", 
            "good bye", "good night")
}

mod = {
    commands["google"]: ( lambda: search_google(pass_txt, False), ),

    commands["name"]: ( lambda: random_gen(dictionary["asking_name_interaction"]), lambda: main_window.robin.setText(response_val), lambda: speak(response_val) ),
    commands["owner"]: ( lambda: random_gen(dictionary["creator_interaction"]), lambda: main_window.robin.setText(response_val), lambda: speak(response_val) ),
    commands["well_being"]: ( lambda: random_gen(dictionary["how_are_you_interaction"]), lambda: main_window.robin.setText(response_val), lambda: speak(response_val) ),
    commands["gratitude"]: ( lambda: random_gen(dictionary["thank_you_interaction"]), lambda: main_window.robin.setText(response_val), lambda: speak(response_val) ),
    commands["hello"]: ( lambda: random_gen(dictionary["hello_interaction"]), lambda: main_window.robin.setText(response_val), lambda: speak(response_val) ),
    commands["age"]: ( lambda: random_gen(dictionary["age_interaction"]), lambda: main_window.robin.setText(response_val), lambda: speak(response_val) ),

    commands["quit"]: ( lambda: exit(), )
}

'''
mod = {
    commands["my_name"]: (tuple("Your name is"), None),
    #Settings Window
    #Save Data Settings Window
}
'''

default_settings_dict = {
    "User_Name": "",
    "Voice": "Female"
}

files = {
    "resources": ("AI.png", "Audio Mute.png", "Audio Unmute.png", "Data_Save.jpg", "Enter.png", "EXIT.png",
                    "MIC Mute.png", "MIC Unmute.png", "MIC.png", "Settings.png"),
    "ui": ("Loading.ui", "Robin_Main.ui"),
    "directory": ("Logs", "Resources", "Settings", "UI", "Audio Model")
}

#API Keys
appId = ':)'

#Global Variables
lab_load, connect, start, end, main_window, model, model_success = None, None, None, None, None, None, None
main_val, ot, stop = False, False, False
fi, resource_file, gui_file, new, func_val = [], [], [], [], []
count = 0
desc, text_voice, command_lower, response_val, additional_val, pass_txt, speak_txt = "An unexpected error occured!", "", "", "", "", "", ""

#Config
q = queue.Queue()
client = wolframalpha.Client(appId)

replier = pyttsx3.init(driverName='sapi5')
voices = replier.getProperty('voices')
rate = replier.getProperty('rate')
replier.setProperty('rate', 135)
replier.setProperty('voice', voices[1].id) #0 -> Male, 1 -> Female ##temp

#Saving variables, default if none found,
'''
Also, set change the values while loading the save file

execute_save_changes()
    Change img and checked value of audio, which speaker variable
    Change username 
    Change voice and apply the changes
'''
speaker = True 
username = default_settings_dict["User_Name"]
voice = default_settings_dict["Voice"]

#Classes
class speak_module(QtCore.QObject):
    end = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.wf, self.stream = None, None

    # define callback
    def callback(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        return (data, pyaudio.paContinue)

    # stop stream
    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.wf.close()
        self.p.terminate()
        os.remove(f'temp_audio.wav')

    def pyaud(self):
        global speaker, main_window

        x,_ = librosa.load(f'./temp_audio.wav', sr=16000)
        sf.write(f'temp_audio.wav', x, 16000)

        self.wf = wave.open(f'temp_audio.wav', 'rb')

        # instantiate PyAudio
        self.p = pyaudio.PyAudio()

        # open stream using callback
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                        channels=self.wf.getnchannels(),
                        rate=self.wf.getframerate(),
                        output=True,
                        stream_callback=self.callback)

        # start the stream
        self.stream.start_stream()

        with suppress(OSError):
            while self.stream.is_active() and speaker is True:
                main_window.wait(2)
            else:
                self.stop()

    def speak(self):
        global replier, speaker, speak_txt

        main_window.wait(5)
        replier.save_to_file(speak_txt, "temp_audio.wav")
        replier.runAndWait()
        self.pyaud()

        speak_txt = ""
        self.end.emit()

class google_search_modules:
    def get_source(self, url):
        session = HTMLSession()
        response = session.get(url)
        return response

    def get_results(self, query):
        query = urllib.parse.quote_plus(query)
        response = self.get_source("https://www.google.com/search?q=" + query)
        return response
    
    def parse_results(self, response):
        css_identifier_result = ".tF2Cxc"
        css_identifier_title = "h3"
        css_identifier_link = ".yuRUbf a"

        results = response.html.find(css_identifier_result)
        output = []
        for result in results:
            item = {
                'title': result.find(css_identifier_title, first=True).text,
                'link': result.find(css_identifier_link, first=True).attrs['href'],
            }
            output.append(item)
        return output
    
    def google_search(self, query):
        response = self.get_results(query)
        return self.parse_results(response)

class text_voice(QtCore.QObject):
    update = QtCore.pyqtSignal()
    finish = QtCore.pyqtSignal()
    start = QtCore.pyqtSignal()
    err = QtCore.pyqtSignal()

    #Callback
    @staticmethod
    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    #Main Function
    def mic_input(self):
        global text_voice, command_lower

        try:
            self.samplerate = None
            self.device = None

            if self.samplerate is None:
                device_info = sd.query_devices(self.device, 'input')
                self.samplerate = int(device_info['default_samplerate'])

            with sd.RawInputStream(samplerate=self.samplerate, blocksize=16000, device=self.device, dtype='int16',
                                    channels=1, callback=self.callback):
                    rec = vosk.KaldiRecognizer(model, self.samplerate)
                    self.start.emit()
                    while True:
                        main_window.wait(2)
                        data = q.get()
                        if rec.AcceptWaveform(data):
                            dat = json.loads(rec.Result())
                            text_voice = dat["text"]
                            command_lower = text_voice.lower()
                            break
                        else:
                            partial_dat = json.loads(rec.PartialResult())
                            text_voice = partial_dat["partial"]
                            self.update.emit()
        except Exception:
            warn_logs(traceback.format_exc())
            self.err.emit()

        self.finish.emit()

class Loading(QMainWindow):
    #Signals
    model_signal = QtCore.pyqtSignal()
    check = QtCore.pyqtSignal()
    dependent = QtCore.pyqtSignal()
    res_load = QtCore.pyqtSignal()
    res = QtCore.pyqtSignal()
    err = QtCore.pyqtSignal()

    def __init__(self):
        global lab_load

        super(Loading, self).__init__()

        #Variables
        self.main_class = bg_process()
        self.depend = self.main_class.dependency()
        self.connect = self.main_class.check_internet()
        self.load = self.main_class.loading_lab()
        self.resource = self.main_class.resources()
        self.model = self.main_class.model_c()
        self.ui = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\UI\\", "Loading.ui")
        
        uic.loadUi(self.ui, self)

        #Widgets
        self.dropShadowFrame = self.findChild(QFrame, "dropShadowFrame")
        self.progress_bar = self.findChild(QProgressBar, "progressBar")
        lab_load = self.findChild(QLabel, "label_loading")
        self.desc = self.findChild(QLabel, "label_description")
        self.timer = QtCore.QTimer()
        self.shadow = QGraphicsDropShadowEffect()

        self._thread = QtCore.QThread()
        self._thread1 = QtCore.QThread()
        self._thread2 = QtCore.QThread()
        self._thread3 = QtCore.QThread()
        self._thread4 = QtCore.QThread()
        
        #Config
        self.setFixedSize(680, 400)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        self.dropShadowFrame.setGraphicsEffect(self.shadow)

        #Connections
        self.err.connect(self.msg_error)

        self.load.moveToThread(self._thread)
        self._thread.started.connect(self.load.load)
        self.load.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self.load.finished.connect(self.close)

        self.connect.moveToThread(self._thread1)
        self.check.connect(self._thread1.start)
        self._thread1.started.connect(self.connect.check)
        self.connect.finished.connect(self._thread1.quit)
        self._thread1.finished.connect(self._thread1.deleteLater)

        self.depend.moveToThread(self._thread2)
        self.dependent.connect(self._thread2.start)
        self._thread2.started.connect(self.depend.check_load)
        self.depend.finished.connect(self._thread2.quit)
        self._thread2.finished.connect(self._thread2.deleteLater)

        self.resource.moveToThread(self._thread3)
        self.res_load.connect(self._thread3.start)
        self._thread3.started.connect(self.resource.res_load)
        self.resource.finished.connect(self._thread3.quit)
        self._thread3.finished.connect(self._thread3.deleteLater)

        self.model.moveToThread(self._thread4)
        self.model_signal.connect(self._thread4.start)
        self._thread4.started.connect(self.model.check)
        self.model.finish.connect(self._thread4.quit)
        self._thread4.finished.connect(self._thread4.deleteLater)

        #Executions
        self._thread.start()

        #Progress Bar
        self.timer.timeout.connect(self.progress)
        self.timer.start(100)
    
    #Function
    def msg_error(self, ex=""):
        global desc, end

        end = time.time()
        QMessageBox.critical(self, "ERROR", desc)
        
        if ex == "":
            exit()
        else:
            raise Exception(ex)

    def main_win(self):
        global main_window, main_val

        main_window.show()
        main_val = True
        main_window.wait(3)
        main_window.msg()

    def progress(self):
        global count, connect, desc, fi, gui_file, resource_file, main_window, model, ot, model_success

        self.progress_bar.setValue(count)
        if ot is False:
            ot = True
            self.model_signal.emit()

        if count >= 100:
            self.desc.setText("STATUS: Launching the app!")
            self.load.var = True
            self.timer.stop()
            self.main_win()
        elif count < 10:
            self.desc.setText("STATUS: Checking Internet Connection!")
            self.check.emit()
            if connect is not None and connect:
                self.timer.start(25)
                count += 1
            elif connect is False:
                desc = "Please check your internet connection! Connection to server failed!"
                self.err.emit()
        elif count < 60:
            self.desc.setText("STATUS: Checking & Validating Directories!")
            self.dependent.emit()
            self.timer.start(500)
            count += 1
            if fi:
                self.load.force_close = True
                self.timer.stop()
                desc = "Some files are found missing or corrupt! \nTry re-installing the app! \n\nA crash report has been created for the developer to solve the issue, if it persist after re-installation."
                self.msg_error(f"\nThe following list of directories not found! \n {fi}")
            else:
                self.timer.start(25)
                count += 1
        elif count < 89:
            self.desc.setText("STATUS: Checking & Validating Resources!")
            self.res_load.emit()
            self.timer.start(500)
            count += 1
            if gui_file and resource_file:
                self.load.force_close = True
                self.timer.stop()
                desc = "Some files are found missing or corrupt! \nTry re-installing the app! \n\nA crash report has been created for the developer to solve the issue, if it persist after re-installation."
                self.msg_error(f"\nResources: \n {resource_file} \nUser Interface: \n {gui_file} \nNOT FOUND!")
            elif resource_file:
                self.load.force_close = True
                self.timer.stop()
                desc = "Some files are found missing or corrupt! \nTry re-installing the app! \n\nA crash report has been created for the developer to solve the issue, if it persist after re-installation."
                self.msg_error(f"\nThe following list of resource files not found! \n {resource_file}")
            elif gui_file:
                self.load.force_close = True
                self.timer.stop()
                desc = "Some files are found missing or corrupt! \nTry re-installing the app! \n\nA crash report has been created for the developer to solve the issue, if it persist after re-installation."
                self.msg_error(f"\nThe following list of user interface files not found! \n {gui_file}")
            else:
                self.timer.start(25)
                count += 1
        elif count < 100:
            self.load.remove = True
            self.desc.setText("STATUS: Setting up the app!")
            main_window = Main_Window_Class()
            if model_success is not None and model_success:
                self.timer.start(25)
                count += 1
            elif model_success is False:
                desc = "The audio model failed to initialize! Please try re-installing the app, if the issue persists!"
                self.err.emit()

class command(QtCore.QObject):
    end = QtCore.pyqtSignal()

    def command_execution(self, *args):
        global func_val, main_window, stop, pass_txt, additional_val, speak_txt

        func_val.clear()
        main_window.robin.setOpenExternalLinks(True)

        if stop is True:
            for argv in args:
                main_window.wait(2)
                argv()
        else:
            response, val = ai_wolfram(pass_txt)
            main_window.robin.setText(response)
            main_window.wait(2)
            if val is None:
                speak(response)
            else:
                speak(additional=additional_val)

        main_window.robin = None
        self.end.emit()

class bg_process:
    class model_c(QtCore.QObject):
        #Signals
        finish = QtCore.pyqtSignal()

        #Functions
        def check(self):
            global model_success, model

            try:
                model = vosk.Model(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))), "Audio Model"))
                model_success = True
            except:
                model_success = False

            self.finish.emit()

    class resources(QtCore.QObject):
        global files

        #Signals
        finished = QtCore.pyqtSignal()

        #Variables
        res_file = files["resources"]
        ui_file = files["ui"]

        #Functions
        def res_load(self):
            global resource_file, gui_file

            file_t = tuple([os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", file_name)) for file_name in self.res_file])
            for x in file_t:
                time.sleep(0.01)
                if x is False:
                    z = file_t.index(x)
                    resource_file.append(self.res_file[z])

            dir_t = tuple([os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\UI\\", dir_name)) for dir_name in self.ui_file])
            for n in dir_t:
                time.sleep(0.01)
                if n is False:
                    p = dir_t.index(n)
                    gui_file.append(self.ui_file[p])
            
            self.finished.emit()

    class dependency(QtCore.QObject):
        global files

        #Signals
        finished = QtCore.pyqtSignal()

        #Variables
        direc = files["directory"]

        #Functions
        def check_load(self):
            global fi

            dir_t = tuple([os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))), dir_name)) for dir_name in self.direc])
            for n in dir_t:
                time.sleep(0.01)
                if n is False:
                    p = dir_t.index(n)
                    fi.append(self.direc[p])
            
            self.finished.emit()

    class check_internet(QtCore.QObject):
        #Signals
        finished = QtCore.pyqtSignal()

        #Functions
        def check(self):
            global connect

            temp_connect = None
            t = tuple([self.internet() for _ in range(5)])
            for x in t:
                time.sleep(0.5)
                temp_connect = (False, True)[x]
            if temp_connect is False:
                for _ in range(50):
                    time.sleep(0.5)
                    if temp_connect is False and temp_connect is not None:
                        temp_connect = self.internet()
                    else:
                        break

            connect = temp_connect
            self.finished.emit()

        def internet(self, host='https://www.google.com'):
            try:
                request.urlopen(host)
                return True
            except:
                return False

    class loading_lab(QtCore.QObject):
        #Signals
        finished = QtCore.pyqtSignal()
        check = QtCore.pyqtSignal()

        def __init__(self):
            QtCore.QObject.__init__(self)

            #Variables
            self.var = False
            self.force_close = False
            self.txt = ("loading...", "loading.", "loading..")

        #Functions
        def load(self):
            global lab_load, count

            while True:
                if self.force_close is False:
                    if self.var is False:
                        for x in self.txt:
                            time.sleep(0.5)
                            lab_load.setText(x)
                    else:
                        self.finished.emit()
                        break
                else:
                    break

class Main_Window_Class(QMainWindow):
    def __init__(self):
        global text_voice, func_val, response_val

        super().__init__()
        
        uic.loadUi(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\UI\\", "Robin_Main.ui"), self)

        #Variables
        self.temp_label = None
        self.robin = None
        self.def_class = bg_process()
        self.internet_class = self.def_class.check_internet()
        self.commands = command()
        self.speak = speak_module()
        self.first, self.on = False, False

        self.text_voice = text_voice()

        self._thread = QtCore.QThread()
        self._thread_cmd = QtCore.QThread()
        self._thread_speak = QtCore.QThread()

        #Widgets Config
        self.setMouseTracking(True)
        self.setFixedSize(784, 594)

        #Widgets
        self.exit_btn = self.findChild(QPushButton, "pushButton_3")
        self.scroll_area = self.findChild(QScrollArea, "scrollArea")
        self.exit_btn_two = self.findChild(QAction, "actionQuit")
        self.mic = self.findChild(QPushButton, "MIC")
        self.enter = self.findChild(QPushButton, "pushButton")
        self.input = self.findChild(QLineEdit, "lineEdit")
        self.clear = self.findChild(QPushButton, "pushButton_4")
        self.settings = self.findChild(QAction, "actionSettings")
        self.data = self.findChild(QAction, "actionData")
        self.reset_data = self.findChild(QAction, "actionReset_Data_to_Defaults")
        self.about_data = self.findChild(QAction, "actionAbout_Data")
        self.shortcut = self.findChild(QAction, "Shortcut")
        self.about_ai = self.findChild(QAction, "actionAbout_AI")
        self.about_robin = self.findChild(QAction, "actionAbout_Robin")
        self.scroll_area = self.findChild(QScrollArea, "scrollArea")
        self.vbox = self.scroll_area.findChild(QWidget, "scrollAreaWidgetContents")
        self.audio = self.findChild(QPushButton, "Sound")
        
        #Connections
        self.text_voice.update.connect(lambda: self.add_label_client(text_voice, False))
        self.text_voice.start.connect(self.mic_icon)
        self.text_voice.finish.connect(lambda: self.mic.setChecked(False))
        self.text_voice.err.connect(lambda: self.error_msg(True, True))
        self.text_voice.finish.connect(self._thread.quit)

        self.text_voice.moveToThread(self._thread)
        self._thread.started.connect(self.text_voice.mic_input)
        self._thread.finished.connect(lambda: self.add_label_client(text_voice, True))
        self._thread.finished.connect(self.mic_icon)
        self._thread.finished.connect(self._thread.wait)

        self.commands.moveToThread(self._thread_cmd)
        self._thread_cmd.started.connect(lambda: self.commands.command_execution(*func_val))
        self.commands.end.connect(self._thread_cmd.quit)
        self._thread_cmd.finished.connect(self._thread_cmd.wait)

        self.speak.moveToThread(self._thread_speak)
        self._thread_speak.started.connect(self.speak.speak)
        self.speak.end.connect(self._thread_speak.quit)
        self._thread_speak.finished.connect(self._thread_speak.wait)

        self.exit_btn.clicked.connect(lambda: exit())
        self.exit_btn_two.triggered.connect(lambda: exit())
        self.mic.clicked.connect(lambda: (lambda: self._thread.start(), lambda: self.mic_cancel())[self._thread.isRunning()]())
        self.input.textChanged.connect(lambda: self.add_label_client(self.input.text(), False))
        self.enter.clicked.connect(lambda: self.add_label_client(self.input.text(), True))
        self.audio.clicked.connect(self.aud)

    #Static Methods/ Normal Functions
    @staticmethod
    def wait(time=10):
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(time*100, loop.quit)
        loop.exec()

    def handler(msg_type, msg_log_context, msg_string):
        pass
    QtCore.qInstallMessageHandler(handler)

    #Functions
    def mic_cancel(self):
        self._thread.quit()

        temp_thread = QtCore.QThread()
        self.moveToThread(temp_thread)

        self.mic_icon()

    def msg(self):
        if not self.first:
            self.first = True
            QMessageBox.about(self, "Confirmation", "Hi there, this is the Developer. The app is currently under-development so do expect bugs. Some bugs may cause the app to crash. I, apologize for it, in advance.\n\nHope you enjoy!")
        
    def scroll_down(self):
        bar = self.scroll_area.verticalScrollBar()
        bar.rangeChanged.connect(lambda _, y: bar.setValue(y))
    
    def aud(self):
        global speaker, replier

        mute = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", "Audio Mute")
        unmute = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", "Audio Unmute")

        (lambda: self.audio.setIcon(QtGui.QIcon(mute)), lambda: self.audio.setIcon(QtGui.QIcon(unmute)))[self.audio.isChecked()]()
        speaker = self.audio.isChecked()

    def add_label_client(self, text, loading):
        global speaker

        self.first = False
        if self.on is False:
            label_to_add = QLabel(self.scrollAreaWidgetContents)
        else:
            label_to_add = self.temp_label

        if text != "":
            if not self.first:
                self.first = True
                speaker = False

            self.on = True
            self.scroll_down()

            sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(label_to_add.sizePolicy().hasHeightForWidth())
            label_to_add.setSizePolicy(sizePolicy)

            label_to_add.setMinimumSize(QtCore.QSize(100, 30))
            label_to_add.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
            label_to_add.setStyleSheet("background-color: rgb(80, 80, 80);\n"
                                        "font: 87 8pt \"Arial Black\";\n"
                                        "border :3px solid black;\n"
                                        "border-top-left-radius :15px;\n"
                                        "border-top-right-radius : 15px;\n"
                                        "border-bottom-left-radius : 15px;\n"
                                        "border-bottom-right-radius : 15px;")
            label_to_add.setScaledContents(True)
            label_to_add.setWordWrap(True)
            label_to_add.adjustSize()
            label_to_add.setMaximumWidth(400)

            self.verticalLayout.addWidget(label_to_add, 0, QtCore.Qt.AlignmentFlag.AlignTop)
            self.temp_label = label_to_add

            with suppress(RuntimeError):
                label_to_add.setText(text)

            if loading:
                self.on = False
                self.temp_label = None
                self.input.clear()
                self.wait(1)
                self.robin_answer(text)
        else:
            if self.on is True:
                label_to_add.setText(text)
                self.wait(1)
                self.on = False
                label_to_add.deleteLater()

    def robin_answer(self, txt):
        global mod, func_val, stop, pass_txt, speaker

        pass_txt = txt
        if txt != "":
            speaker = self.audio.isChecked()
            self.first = False

            stop = False
            for val in mod:
                if stop is False:
                    for txt_arr in val:
                        if txt_arr in txt:
                            self.wait(1)
                            func_val = list(mod[val])
                            stop = True
                            break
                else:
                    break
            self._thread_cmd.start()

            self.scroll_down()

            label_to_add = QLabel(self.scrollAreaWidgetContents)
            self.robin = label_to_add

            sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(label_to_add.sizePolicy().hasHeightForWidth())
            label_to_add.setSizePolicy(sizePolicy)

            label_to_add.setMinimumSize(QtCore.QSize(100, 30))
            label_to_add.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
            label_to_add.setStyleSheet("background-color: rgb(177, 177, 177);\n"
                                        "font: 87 8pt \"Arial Black\";\n"
                                        "border :3px solid black;\n"
                                        "border-top-left-radius :15px;\n"
                                        "border-top-right-radius : 15px;\n"
                                        "border-bottom-left-radius : 15px;\n"
                                        "border-bottom-right-radius : 15px;")

            label_to_add.setScaledContents(True)
            label_to_add.setWordWrap(True)
            label_to_add.adjustSize()
            label_to_add.setMaximumWidth(400)

            self.verticalLayout.addWidget(label_to_add, 0, QtCore.Qt.AlignmentFlag.AlignTop)

            if self.internet_class.internet() is False:
                label_to_add.setText("No Internet connection! Please check your internet!")
                self.robin = None
                return

    def mic_icon(self):
        mute = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", "MIC Mute")
        unmute = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", "MIC Unmute")
        
        if self.mic.isChecked():
            self.mic.setStyleSheet(
                "border :3px solid ;"
                "border-top-color : red;"
                "border-left-color : green;"
                "border-right-color : blue;"
                "border-bottom-color : yellow;"
                "border-top-left-radius :15px;"
                "border-top-right-radius : 15px;"
                "border-bottom-left-radius : 15px;"
                "border-bottom-right-radius : 15px;"
            )
            self.mic.setIcon(QtGui.QIcon(unmute))
        else:
            self.mic.setStyleSheet(
                "border :3px solid black;"
                "border-top-left-radius :15px;"
                "border-top-right-radius : 15px;"
                "border-bottom-left-radius : 15px;"
                "border-bottom-right-radius : 15px;"
            )
            self.mic.setIcon(QtGui.QIcon(mute))

    def error_msg(self, package_prob=False, warn=False, custom_txt=desc):
        if package_prob is True:
            custom_txt = "We encountered an unexpected issue!. \n\nPlease Try Again Later!"

        if warn is False:
            QMessageBox.critical(self, "ERROR", custom_txt)
        else:
            QMessageBox.warning(self, "WARNING", custom_txt)

if __name__ == "__main__":
    start = time.time()
    threading.Thread(target=check_sys).start()
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    win = Loading()
    win.show()
    sys.exit(app.exec())
