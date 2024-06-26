import subprocess
import os
import glob
import signal
import time
import easygui as eg


# Path to the Python executable in the virtual environment
python_executable = os.path.join('.venv', 'Scripts', 'python.exe')

# Paths to your scripts
script1 = 'data_log_CSV_FANUC.py'
script2 = 'data_live_monitoring_FANUC.py'
script3 = 'data_graph_visualisation.py'

# Function to run a script
def run_script(script, *args):
    return subprocess.Popen([python_executable, script] + list(args))

# Function to terminate processes
def terminate_processes(*processes):
    for process in processes:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

# Function to handle the user's choice
def handle_choice(choice, processes):
    
    if choice == 'Visualize present data':
        output_filename = eg.enterbox("Enter the name of the CSV file to monitor :", "File Name Input")
        if not output_filename.endswith('.csv'):
            output_filename += '.csv' 

        print("Visualizing present data...")
        process3 = run_script(script3, output_filename)
        processes.append(process3)
        print("Started data visualization script.")

    elif choice == 'Monitor new data':
        print("Monitoring new data...")
        # Prompt user for output CSV file name
        output_filename = eg.enterbox("Enter the name of the output CSV file:", "File Name Input")
        if not output_filename.endswith('.csv'):
            output_filename += '.csv'        
        process1 = run_script(script1, output_filename)
        process2 = run_script(script2, output_filename)
        processes.extend([process1, process2])
        print("Both programs started.")

    elif choice == 'Clear CSV files':
         # Remove current .csv files to input new data into testing
        for file_path in glob.glob('*.csv'):
            try:
                os.remove(file_path)
                print(f"Removed file: {file_path}")
            except Exception as e:
                print(f"Error removing file {file_path}: {e}")
            print("CSV files erased.")

    elif choice == 'Terminate running processes':
        terminate_processes(*processes)
        processes.clear()
        print("Processes terminated.")

    elif choice == 'Exit':
        terminate_processes(*processes)
        processes.clear()
        print("Exiting...")

# Show the selection dialog
processes = []
while True:
    choices = ['Visualize present data', 'Monitor new data', 'Clear CSV files', 'Terminate running processes', 'Exit']
    choice = eg.buttonbox("\n\n\n                           What would you like to do ?", choices=choices, title="Data monitoring")

    # Handle the user's choice
    if choice:
        handle_choice(choice, processes)
        if choice == 'Exit':
            break
    else:
        print("No choice made.")
        break
