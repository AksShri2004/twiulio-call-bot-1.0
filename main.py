import random
import time
from datetime import datetime, timedelta
from tkinter import *
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import threading
import json
import os
import sys


# Function to get the path of the executable or script directory
def get_resource_path(relative_path):
    # If it's in a PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # If running as a script or from source
        return os.path.join(os.path.abspath("."), relative_path)


# Function to load Twilio numbers from JSON file
def load_twilio_numbers():
    json_path = get_resource_path('twilio_numbers.json')
    if os.path.exists(json_path):
        with open(json_path, 'r') as file:
            data = json.load(file)
            return data['twilio_numbers']



# Function to save Twilio numbers to JSON file
def save_twilio_numbers():
    twilio_numbers = [
        entry_twilio1.get(),
        entry_twilio2.get(),
        entry_twilio3.get(),
        entry_twilio4.get(),
        entry_twilio5.get(),
        entry_twilio6.get(),
        entry_twilio7.get(),
        entry_twilio8.get(),
    ]

    data = {"twilio_numbers": twilio_numbers}

    json_path = get_resource_path('twilio_numbers.json')

    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

    update_status("Twilio numbers saved to twilio_numbers.json")


# Function to generate TwiML response for the call
def generate_twiml():
    response = VoiceResponse()
    response.pause(length=2)  # Wait for 2 seconds
    response.play(digits="2")  # Automatically press '2'
    response.pause(length=43)  # Stay connected for 43 seconds
    return str(response)


# Function to make the call using one of the Twilio numbers
def make_call(from_number, target_number, client):
    call = client.calls.create(
        to=target_number,
        from_=from_number,
        twiml=generate_twiml(),
        timeout=60
    )
    update_status(f"Call initiated from {from_number} to {target_number}. Call SID: {call.sid}")


# Function to schedule random calls within the hour
def schedule_hourly_calls(client, twilio_numbers, target_number, start_of_hour):
    total_calls_made = 0
    num_calls = random.randint(2, 3)  # Randomly select 2 or 3 calls per hour
    update_status(f"\nThis hour will make {num_calls} call(s).")

    # Calculate the total time left in the hour
    end_of_hour = start_of_hour + timedelta(hours=1)
    total_time_in_hour = (end_of_hour - datetime.now()).total_seconds()

    # Divide the hour into parts (4 parts for 3 calls, 3 parts for 2 calls)
    if num_calls == 3:
        divisions = 4
    else:
        divisions = 3

    part_duration = total_time_in_hour / divisions  # Duration of each part

    # Loop through and schedule the calls randomly within each part
    for i in range(num_calls):
        from_number = random.choice(twilio_numbers)  # Randomly choose one of the Twilio numbers

        # Calculate the random time within the current part
        random_delay_within_part = random.uniform(0, part_duration)

        # Wait for the random delay within this part before making the call
        update_status(
            f"Waiting for {int(random_delay_within_part // 60)} minutes and {int(random_delay_within_part % 60)} seconds before the next call.")
        time.sleep(random_delay_within_part)

        # Make the call
        make_call(from_number, target_number, client)
        total_calls_made += 1

        # Move to the next part and update the part duration
        now = datetime.now()
        total_time_in_hour = (end_of_hour - now).total_seconds()
        if i < num_calls - 1:
            part_duration = total_time_in_hour / (
                        divisions - (i + 1))  # Recalculate part duration for remaining divisions

    return total_calls_made


# Main loop to run for exactly 10 hours
def run_scheduler(twilio_numbers, target_number):
    total_calls_made = 0
    start_time = datetime.now()  # Start time of the script
    end_time = start_time + timedelta(hours=10)  # End time after 10 hours

    # Hardcoded Twilio credentials
    account_sid = "twilio sid"  # Your Twilio Account SID
    auth_token = "twilio auth token" # Your Twilio Auth Token
    client = Client(account_sid, auth_token)

    # Loop over each of the 10 hours
    for hour in range(10):
        now = datetime.now()
        start_of_hour = now

        # If the total runtime is about to exceed 10 hours, break the loop
        if now >= end_time:
            break

        # Make calls for this hour
        total_calls = schedule_hourly_calls(client, twilio_numbers, target_number, start_of_hour)
        total_calls_made += total_calls

        # Wait for the remaining time in the hour, if any, before starting the next hour
        now = datetime.now()
        remaining_time_in_hour = (start_of_hour + timedelta(hours=1) - now).total_seconds()
        if remaining_time_in_hour > 0:
            update_status(
                f"Waiting {int(remaining_time_in_hour // 60)} minutes and {int(remaining_time_in_hour % 60)} seconds until the next hour.")
            time.sleep(remaining_time_in_hour)  # Wait for the next hour

    update_status(f"\nTotal calls made in 10 hours: {total_calls_made}.")


# Function triggered by the "Run" button in the GUI
def run_process():
    # Get the values from the input fields (Twilio numbers and target number)
    twilio_numbers = [
        entry_twilio1.get(),
        entry_twilio2.get(),
        entry_twilio3.get(),
        entry_twilio4.get(),
        entry_twilio5.get(),
        entry_twilio6.get(),
        entry_twilio7.get(),
        entry_twilio8.get(),
    ]
    target_number = entry_target.get()

    # Save the Twilio numbers to JSON file when Run is clicked
    save_twilio_numbers()

    # Start the scheduler in a separate thread
    thread = threading.Thread(target=run_scheduler_thread, args=(twilio_numbers, target_number))
    thread.start()


# Function to update the status label in the GUI
def update_status(message):
    status_text.insert(END, message + "\n")
    status_text.see(END)  # Scroll to the end to show the latest status
    root.update()  # Update the GUI


# Function to run the scheduler in a separate thread
def run_scheduler_thread(twilio_numbers, target_number):
    # Clear the status before starting
    status_text.delete(1.0, END)
    run_scheduler(twilio_numbers, target_number)


# Create the GUI window using Tkinter
root = Tk()
root.title("Twilio Call Scheduler")

# Load Twilio numbers from JSON file
loaded_twilio_numbers = load_twilio_numbers()

# Use grid layout to place labels and text boxes side by side
Label(root, text="Twilio Number 1:").grid(row=0, column=0, padx=10, pady=5, sticky=E)
entry_twilio1 = Entry(root, width=40)
entry_twilio1.insert(0, loaded_twilio_numbers[0])  # Load saved number
entry_twilio1.grid(row=0, column=1)

Label(root, text="Twilio Number 2:").grid(row=1, column=0, padx=10, pady=5, sticky=E)
entry_twilio2 = Entry(root, width=40)
entry_twilio2.insert(0, loaded_twilio_numbers[1])  # Load saved number
entry_twilio2.grid(row=1, column=1)

Label(root, text="Twilio Number 3:").grid(row=2, column=0, padx=10, pady=5, sticky=E)
entry_twilio3 = Entry(root, width=40)
entry_twilio3.insert(0, loaded_twilio_numbers[2])  # Load saved number
entry_twilio3.grid(row=2, column=1)

Label(root, text="Twilio Number 4:").grid(row=3, column=0, padx=10, pady=5, sticky=E)
entry_twilio4 = Entry(root, width=40)
entry_twilio4.insert(0, loaded_twilio_numbers[3])  # Load saved number
entry_twilio4.grid(row=3, column=1)

Label(root, text="Twilio Number 5:").grid(row=4, column=0, padx=10, pady=5, sticky=E)
entry_twilio5 = Entry(root, width=40)
entry_twilio5.insert(0, loaded_twilio_numbers[4])  # Load saved number
entry_twilio5.grid(row=4, column=1)

Label(root, text="Twilio Number 6:").grid(row=5, column=0, padx=10, pady=5, sticky=E)
entry_twilio6 = Entry(root, width=40)
entry_twilio6.insert(0, loaded_twilio_numbers[5])  # Load saved number
entry_twilio6.grid(row=5, column=1)

Label(root, text="Twilio Number 7:").grid(row=6, column=0, padx=10, pady=5, sticky=E)
entry_twilio7 = Entry(root, width=40)
entry_twilio7.insert(0, loaded_twilio_numbers[6])  # Load saved number
entry_twilio7.grid(row=6, column=1)

Label(root, text="Twilio Number 8:").grid(row=7, column=0, padx=10, pady=5, sticky=E)
entry_twilio8 = Entry(root, width=40)
entry_twilio8.insert(0, loaded_twilio_numbers[7])  # Load saved number
entry_twilio8.grid(row=7, column=1)

# Label and entry field for the target phone number
Label(root, text="Target Number:").grid(row=8, column=0, padx=10, pady=5, sticky=E)
entry_target = Entry(root, width=40)
entry_target.grid(row=8, column=1)

# Run button to trigger the process
run_button = Button(root, text="Run", command=run_process)
run_button.grid(row=10, column=0, columnspan=2, pady=20)

# Save button to save the Twilio numbers to JSON
save_button = Button(root, text="Save Numbers", command=save_twilio_numbers)
save_button.grid(row=9, column=0, columnspan=2, pady=10)

# Status display in the GUI
Label(root, text="Status:").grid(row=11, column=0, padx=10, pady=5, sticky=E)
status_text = Text(root, height=10, width=60)
status_text.grid(row=11, column=1)

# Start the Tkinter event loop
root.mainloop()
