import requests
import json
import csv
import time
import threading
from datetime import datetime, timedelta
import sys
import traceback

last_fetch_time = None  # Variable to store the timestamp of the last fetch

def fetch_json(url):
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    return response.json()

def write_json_to_csv(json_data, output_filename, milliseconds_passed):
    if isinstance(json_data, dict):
        json_data = [json_data]

    keys = json_data[0].keys()
    with open(output_filename, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['timestamp', 'milliseconds_passed'] + list(keys))
        if file.tell() == 0:
            writer.writeheader()
        for item in json_data:
            item['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Format timestamp with milliseconds
            item['milliseconds_passed'] = milliseconds_passed
            writer.writerow(item)

def main(url, output_filename):
    global last_fetch_time
    try:
        json_data = fetch_json(url)
        current_time = datetime.now()
        
        if last_fetch_time is not None:
            milliseconds_passed = int((current_time - last_fetch_time).total_seconds() * 1000)
        else:
            milliseconds_passed = 0
        
        write_json_to_csv(json_data, output_filename, milliseconds_passed)
        last_fetch_time = current_time  # Update last_fetch_time to current time
        print(f"Data has been written to {output_filename}")
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()  # Print the full traceback for debugging

def repeat_every_interval(interval, url, output_filename):
    while True:
        main(url, output_filename)
        time.sleep(interval)

############### PARAMETERS TO MODIFY

# Get output filename from command line arguments
if len(sys.argv) > 1:
    output_filename = sys.argv[1]
else:
    output_filename = 'output.csv'

interval = 0.01  # Interval in seconds (0.05 seconds = 50 milliseconds)

url = 'http://192.168.137.100/KAREL/API_MOTION_LOG'

# Start the repeating function in a separate thread
thread = threading.Thread(target=repeat_every_interval, args=(interval, url, output_filename))
thread.daemon = True  # This makes the thread exit when the main program exits
thread.start()

# Keep the main program running to allow the thread to continue execution
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated.")
    thread.join()  # Ensure the thread completes gracefully
