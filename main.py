import threading
from queue import Queue

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk, simpledialog
import os
from cryptography.fernet import Fernet

import shutil

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine_queue = Queue()


# Function to speak the given text
def speak(text):
    engine_queue.put(text)


# Function to process the engine queue and speak
def process_engine_queue():
    while True:
        text = engine_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()


# Start the engine processing thread
engine_thread = threading.Thread(target=process_engine_queue)
engine_thread.start()


# Function to recognize speech using SpeechRecognition
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language="en-US")
            print(f"You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand that.")
            return ""
        except sr.RequestError as e:
            print(f"Error connecting to Google Speech Recognition service: {e}")
            speak("Sorry, I couldn't connect to the speech recognition service.")
            return ""


# Function to recognize text input
def text_input():
    return input_entry.get().lower()


# Function to perform tasks based on the user's query
def perform_task(query):
    if "hello" in query:
        speak("Hello! How can I help you today?")

    elif "search for file" in query:
        file_name = search_file_query()
    elif "delete file" in query:
        file_name = search_file_query()
        if file_name:
            delete_file(file_name)
    elif "encrypt file" in query:
        file_name = search_file_query()
        if file_name:
            encrypt(file_name)
    elif "decrypt file" in query:
        file_name = search_file_query()
        if file_name:
            decrypt(file_name)
    elif "copy file" in query:
        file_name = search_file_query()
        dest = get_file()
        if file_name:
            copy_file(file_name, dest)
    elif "create file" in query:
        file_name = get_file()
        create_file(file_name)
    elif "exit" in query or "goodbye" in query:
        speak("Goodbye! Have a great day.")
        exit()
    else:
        speak("Sorry, I didn't understand that. Can you please repeat?")


# Function to switch between text and voice input
def switch_input_mode():
    global voice_input
    voice_input = not voice_input
    if voice_input:
        speak("Voice input mode activated. Please speak your command.")
    else:
        speak("Text input mode activated. Enter your command in the text box.")


# Function to get user input from the GUI
def get_user_input():
    if voice_input:
        return listen()
    else:
        return text_input()


def delete_file(file_name):
    os.remove(file_name)
    speak("file removed successfully")
    update_gui("file deleted")


def create_file(full_name):
    try:
        file = open(full_name, 'w')
        speak("file created successfully")
    except FileExistsError as e:
        speak(f'An error occurred: {e}')


def copy_file(file_name, dest):
    shutil.copy(file_name, dest)


def search_file_query():
    file_name = get_file()
    if file_name:
        file_found = search_for_file(file_name)
        update_gui("searching for file ...")
        if file_found:
            speak("File found.")
            update_gui(file_found)
            return file_found
        else:
            speak(f"Sorry, I couldn't find any file with the name {file_name}.")
            update_gui("file not found")
            return None


def search_for_file(file_name):
    for root, dirs, files in os.walk('c:\\'):  # Replace '/path/to/search' with the directory you want to search
        if file_name in files:
            return os.path.join(root, file_name)
    return None


def encrypt(filename):
    """
    Given a filename (str) and key (bytes), it encrypts the file and write it
    """
    # key generation
    keyf = Fernet.generate_key()

    # string the key in a file
    with open(filename + '.key', 'wb') as filekey:
        filekey.write(keyf)

    with open(filename + '.key', 'rb') as filekey:
        key = filekey.read()

    f = Fernet(key)
    with open(filename, "rb") as file:
        # read all file data
        file_data = file.read()
    # encrypt data
    encrypted_data = f.encrypt(file_data)
    # write the encrypted file
    with open(filename, "wb") as file:
        file.write(encrypted_data)


def decrypt(filename):
    """
    Given a filename (str) and key (bytes), it decrypts the file and write it
    """
    with open(filename + '.key', 'rb') as filekey:
        key = filekey.read()

    f = Fernet(key)
    with open(filename, "rb") as file:
        # read the encrypted data
        encrypted_data = file.read()
    # decrypt data
    decrypted_data = f.decrypt(encrypted_data)
    # write the original file
    with open(filename, "wb") as file:
        file.write(decrypted_data)


# Function to update the GUI with the assistant's response
def update_gui(response):
    output_label.config(text=response)


# Function to handle button click events
def button_click():
    query = get_user_input()
    if query:
        perform_task(query)


def get_file():
    file_name = simpledialog.askstring("File Input", "Enter path name:")
    return file_name


# Function to delay the execution of runAndWait
def delay_run_and_wait():
    engine.runAndWait()


# Main GUI setup
app = tk.Tk()
app.title("Voice Assistant")

# Voice input mode flag
voice_input = True

# Input entry
input_entry_var = tk.StringVar()  # Variable to store user input
input_entry = ttk.Entry(app, width=40, textvariable=input_entry_var)
input_entry.grid(row=0, column=0, padx=10, pady=10)

# Switch input mode button
switch_button = ttk.Button(app, text="Switch Input Mode", command=switch_input_mode)
switch_button.grid(row=0, column=1, padx=10, pady=10)

# Command execution button
execute_button = ttk.Button(app, text="Execute Command", command=button_click)
execute_button.grid(row=0, column=2, padx=10, pady=10)

# Output label
output_label = ttk.Label(app, text="Welcome! Enter your command.")
output_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Start the GUI main loop
app.mainloop()

# Cleanup: Stop the engine thread
engine_queue.put(None)  # Signal the engine thread to exit
engine_thread.join()  # Wait for the engine thread to finish
