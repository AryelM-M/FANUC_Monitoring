import pandas as pd
import matplotlib.pyplot as plt
import ast
import math
import time
import sys

def plot_real_time(csv_file):
    # Initialize an empty plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))
    fig.suptitle('Real-Time Machine Data Analysis')

    # Initialize empty lists to store data
    resultant_force = []
    resultant_speed = []

    while True:
        try:
            # Read CSV into a pandas DataFrame
            df = pd.read_csv(csv_file)

            # Convert 'timestamp' column to datetime type
            time_now = pd.to_datetime(df['timestamp'])
            # Process ext_force into resultant force
            force_list = df['ext_force'].apply(ast.literal_eval)
            resultant_force = []
            resultant_moment = []
            for force_vector in force_list:
                magnitude_f = math.sqrt(force_vector[0]**2 + force_vector[1]**2 + force_vector[2]**2)
                magnitude_m = math.sqrt(force_vector[3]**2 + force_vector[4]**2 + force_vector[5]**2)
                resultant_force.append(magnitude_f)
                resultant_moment.append(magnitude_m)

            # Process mch_pos into resultant speed
            pos_list = df['mch_pos'].apply(ast.literal_eval)
            resultant_speed = []
            for i in range(len(pos_list) - 1):
                magnitude_s = (pos_list[i+1][0] - pos_list[i][0])**2
                magnitude_s += (pos_list[i+1][1] - pos_list[i][1])**2
                magnitude_s += (pos_list[i+1][2] - pos_list[i][2])**2
                time_elapsed = df['milliseconds_passed'][i]
                if time_elapsed == 0:
                    resultant_speed.append(0)
                else:
                    magnitude_s = (math.sqrt(magnitude_s) / df['milliseconds_passed'][i]) * 1000  # Speed in mm/s
                    resultant_speed.append(magnitude_s)
            resultant_speed.append(0)

            # Plotting
            ax1.clear()
            ax1.plot(time_now, resultant_force, label='External Force (N)')
            ax1.plot(time_now, resultant_moment, label='External Moment (Nm)')
            ax1.set_title('External Force')
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Force (N)')
            ax1.legend()

            ax2.clear()
            ax2.plot(time_now, resultant_speed, label='Calculated Speed (mm/s)')
            ax2.plot(time_now, df['mch_spd'], label='Machine Speed (mm/s)')
            ax2.set_title('Speed Comparison')
            ax2.set_xlabel('Time')
            ax2.set_ylabel('Speed (mm/s)')
            ax2.legend()

            # Update the plot
            plt.tight_layout()
            plt.pause(0.1)  # Pause for a short time to update the plot (adjust as needed)

        except KeyboardInterrupt:
            print("Plotting terminated.")
            break
        except Exception as e:
            print(f"An error in monitoring occurred: {e}")
            time.sleep(1)  # Wait and retry if an error occurs

# Example usage
if len(sys.argv) > 1:
    csv_file = sys.argv[1]
else:
    csv_file = 'output.csv'
    
plot_real_time(csv_file)