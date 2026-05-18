import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def calculate_kinematics(group):
    group = group.sort_values('frame')
    dt = group['frame'].diff()
    dcx = group['cx'].diff()
    dcy = group['cy'].diff()
    
    group['speed'] = np.sqrt(dcx**2 + dcy**2) / dt
    group['acceleration'] = group['speed'].diff() / dt
    return group

def plot_trajectories(df, target_ids, output_dir):
    plt.figure(figsize=(12, 8))

    for tid in target_ids:
        player_data = df[df['id'] == tid]
        plt.plot(player_data['cx'], player_data['cy'], 
                 marker='o', markersize=2, label=f'ID: {tid}', alpha=0.7)

    plt.title('Player Trajectories')
    plt.xlabel('X coordinate (pixels)')
    plt.ylabel('Y coordinate (pixels)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.gca().invert_yaxis() 
    plt.tight_layout()

    # Save processed trajectory graph
    save_path_traj = os.path.join(output_dir, 'trajectory_result.png')
    plt.savefig(save_path_traj)
    print(f"SUCCESS: Save the trajectory graph -> {os.path.abspath(save_path_traj)}")

def plot_speed(df, target_ids, output_dir):
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, tid in enumerate(target_ids):
        ax = axes[i]
        player_data = df[df['id'] == tid]
    
        ax.plot(player_data['frame'], player_data['speed'], color='firebrick', marker='o', markersize=2, linestyle='-', linewidth=1, alpha=0.8)
        ax.set_title(f'ID: {tid} Speed', fontsize=12)
        ax.set_xlabel('Frame', fontsize=10)
        ax.set_ylabel('Speed (pixels/frame)', fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.5)

    if len(target_ids) < len(axes):
        axes[-1].axis('off')

    plt.tight_layout()

    save_path_speed = os.path.join(output_dir, 'speed_subplots.png')
    plt.savefig(save_path_speed, dpi=300)
    print(f"SUCCESS: Save the speed subplots -> {os.path.abspath(save_path_speed)}")

# Create the output folder
output_dir = 'result'
os.makedirs(output_dir, exist_ok=True)

# Path to the trimmed result file
result_path = '/home/y_kitagawa/B4Lecture-2026/ex02/y_kitagawa/117093_trimmed.txt'

# Load the data
cols = ['frame', 'id', 'x', 'y', 'w', 'h', 'conf', 'class', 'vis', 'none']
df = pd.read_csv(result_path, header=None, names=cols)

# Calculate center coordinates
df['cx'] = df['x'] + df['w'] / 2
df['cy'] = df['y'] + df['h'] / 2

print("INFO: Calculating kinematics...")
df = df.groupby('id', group_keys=False).apply(calculate_kinematics)

valid_df = df.dropna(subset=['speed'])

# Automatically extract the top 4 IDs with the highest maximum speed, excluding ID 13
anomaly_candidates = valid_df[valid_df['id'] != 13]
top4_ids = anomaly_candidates.sort_values(by='speed', ascending=False)['id'].unique()[:4]

target_ids = [13] + list(top4_ids)

print(f"INFO: Target IDs for plotting: {target_ids}\n")

plot_trajectories(df, target_ids, output_dir)
plot_speed(df, target_ids, output_dir)