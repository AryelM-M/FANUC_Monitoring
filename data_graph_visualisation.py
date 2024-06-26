import pandas as pd
import matplotlib.pyplot as plt
import ast
import math
import sys 

# Change to 1 if you want to compare machine data with loadcell data.
# You need to save the loadcell data in a csv file named 'ldcl_' + the name of the other csv file
USE_LOADCELL_DATA = 1
# Change the duration in seconds of a sample after a hit
SAMPLE_TIME = 60

def plot_data(csv_file):
    # Read CSV into a pandas DataFrame
    df = pd.read_csv(csv_file)
    
    # Read ldcl excel file into a pandas DataFrame
    # TODO ajust sampling to match the csv file
    if USE_LOADCELL_DATA == 1:
        ldcl = pd.read_csv("ldcl_" + csv_file)

    # Convert 'timestamp' column to datetime type
    time_now = pd.to_datetime(df['timestamp'])
    
    # Convert ext_force into a resultant force at TCP point
    force_list = df['ext_force'].apply(ast.literal_eval)
    resultant_force = []
    resultant_moment = []
    for force_vector in force_list:
        magnitude_f = math.sqrt(force_vector[0]**2 + force_vector[1]**2 + force_vector[2]**2)
        magnitude_m = math.sqrt(force_vector[3]**2 + force_vector[4]**2 + force_vector[5]**2)
        resultant_force.append(magnitude_f)
        resultant_moment.append(magnitude_m)

    # Convert mch_pos into a resultant speed at TCP point
    pos_list = df['mch_pos'].apply(ast.literal_eval)
    resultant_speed = []
    for i in range(len(pos_list)-1):
        magnitude_s = (pos_list[i+1][0] - pos_list[i][0])**2
        magnitude_s += (pos_list[i+1][1] - pos_list[i][1])**2
        magnitude_s += (pos_list[i+1][2] - pos_list[i][2])**2
        if df['milliseconds_passed'][i] == 0:
            resultant_speed.append(0)
        else:
            magnitude_s = (math.sqrt(magnitude_s) / df['milliseconds_passed'][i]) * 1000  # Speed in mm/s
            resultant_speed.append(magnitude_s)
    resultant_speed.append(0)


    # Ajust time range of robot to start at impact signal (Hit to start)
    i = 0
    j = 0
    max_time = 1000 * SAMPLE_TIME # Time in milliseconds the user wants to see
    time_elapsed = 0

    # Ajust time range of loadcell and robot to start at impact signal (Hit to start)
    while not resultant_force[i] > 10 :
        i = i + 1
    t_passed = i
    while time_elapsed < max_time :
        time_elapsed += df['milliseconds_passed'][t_passed]
        t_passed = t_passed + 1
    resultant_force = resultant_force[i:t_passed]
    time_now = time_now[i:t_passed]

 
    if USE_LOADCELL_DATA == 1:
        while ldcl['Newton'][j] < 10 :
            j = j + 1
        t_passed = j
        start_time = ldcl['Relative Time'][t_passed]

        while (ldcl['Relative Time'][t_passed] - ldcl['Relative Time'][j])*1000 < max_time:
            t_passed = t_passed + 1

        force_ldcl = ldcl['Newton'][j:t_passed]
        time_ldcl = ldcl['Relative Time'][j:t_passed]
        time_ldcl = [x - start_time for x in time_ldcl]

    # Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))

    ax1.plot(time_now, resultant_force, label='External Force (N)')
    #ax1.plot(time_now, resultant_moment, label='External Moment (Nm)')
    ax1.set_title('External Force of Fanuc Robot')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Force of robot (N)')
    ax1.legend()

    
    if USE_LOADCELL_DATA == 1:
        ax2.plot(time_ldcl, force_ldcl, label='External Force (N)')
    else : ax2.plot(time_now, df['mch_spd'], label='Machine Speed (mm/s)')
    ax2.set_title('External Force of Loadcell')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Force of loadcell (N)')
    ax2.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)

    # Event handler for closing the plot window
    def handle_close(event):
        print('Plotting terminated.')
        plt.close()
        raise KeyboardInterrupt  # Raise KeyboardInterrupt to exit the while loop

    fig.canvas.mpl_connect('close_event', handle_close)

    # Display plot
    plt.show()

# Example usage
if len(sys.argv) > 1:
    csv_file = sys.argv[1]
else:
    csv_file = 'output.csv'
    
plot_data(csv_file)
