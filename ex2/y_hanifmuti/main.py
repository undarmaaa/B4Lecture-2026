import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_output_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # calculate bounding box center
    df["cx"] = df["x"] + df["w"] / 2
    df["cy"] = df["y"] + df["h"] / 2

    return df


def plot_player_trajectories(filtered_df, target_ids):
    plt.figure(figsize=(12, 7))

    for track_id in target_ids:
        player_data = filtered_df[filtered_df['track_id']
                                  == track_id].sort_values('frame')

        plt.plot(player_data['cx'], player_data['cy'],
                 label=f'Player ID {track_id}', alpha=0.5, linewidth=2)

        # Plot the scatter points with alpha based on frame progression
        norm_frame = (player_data['frame'] - player_data['frame'].min()) / \
            (player_data['frame'].max() - player_data['frame'].min() + 1)
        plt.scatter(player_data['cx'], player_data['cy'], label=f'Player ID {track_id}',
                    alpha=norm_frame.clip(0.1, 1.0), s=15)

        # Mark the starting position
        if not player_data.empty:
            plt.scatter(player_data['cx'].iloc[0], player_data['cy'].iloc[0],
                        color='black', marker='X', s=100, zorder=5)

    plt.scatter([], [], color='black', marker='X',
                s=100, label='Start Position', zorder=5)

    plt.gca().invert_yaxis()
    plt.title('Player Trajectories (First 20s)',
              fontsize=14, fontweight='bold')
    plt.xlabel('X Coordinate [Pixels]', fontsize=12)
    plt.ylabel('Y Coordinate [Pixels]', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='lower right')

    plt.tight_layout()
    plt.savefig('player_trajectories.png', dpi=300)


def smooth_speed(speed_series, window_size=5):
    return speed_series.rolling(window=window_size, min_periods=1, center=True).mean()


def plot_player_speed_acceleration(
    df,
    target_ids,
    smooth_window=5,
    output_filename='player_speed_acceleration.png'
):
    df = df.sort_values(by=['track_id', 'frame'])

    df['vx'] = df.groupby('track_id')['cx'].diff()
    df['vy'] = df.groupby('track_id')['cy'].diff()
    df['speed'] = np.sqrt(df['vx']**2 + df['vy']**2)
    if smooth_window > 1:
        df['speed'] = df.groupby('track_id')['speed'].transform(
            lambda x: smooth_speed(x, window_size=smooth_window))

    df['acceleration'] = df.groupby('track_id')['speed'].diff()

    cols_to_plot = min(3, len(target_ids))
    rows_to_plot = (len(target_ids) + cols_to_plot - 1) // cols_to_plot

    _, ax = plt.subplots(figsize=(12, 7), ncols=cols_to_plot,
                         nrows=rows_to_plot, sharex=True)

    # create up to 6 separate plots for each player
    for i, track_id in enumerate(target_ids):
        data = df[df['track_id'] == track_id]
        cols_index = i % cols_to_plot
        rows_index = i // cols_to_plot
        ax[rows_index, cols_index].plot(
            data['frame'], data['speed'], label='Speed', color='blue')
        ax[rows_index, cols_index].plot(
            data['frame'], data['acceleration'], label='Acceleration', color='orange')
        ax[rows_index, cols_index].set_title(
            f'Player ID {track_id}', fontsize=12, fontweight='bold')
        ax[rows_index, cols_index].set_xlabel('Frame', fontsize=10)
        ax[rows_index, cols_index].set_ylabel('Value', fontsize=10)
        ax[rows_index, cols_index].legend()
        ax[rows_index, cols_index].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)


def interpolate_missing_frames(df):
    df_cleaned = df.copy()
    ANOMALOUS_SPEED_THRESHOLD = 12
    df_cleaned['vx'] = df_cleaned.groupby('track_id')['cx'].diff()
    df_cleaned['vy'] = df_cleaned.groupby('track_id')['cy'].diff()
    df_cleaned['speed'] = np.sqrt(df_cleaned['vx']**2 + df_cleaned['vy']**2)
    bad_indices = df_cleaned[df_cleaned['speed']
                             > ANOMALOUS_SPEED_THRESHOLD].index

    df_cleaned.loc[bad_indices, ['cx', 'cy']] = np.nan
    df_cleaned['cx_interpolated'] = df_cleaned.groupby('track_id')['cx'].transform(
        lambda x: x.interpolate(method='linear'))
    df_cleaned['cy_interpolated'] = df_cleaned.groupby('track_id')['cy'].transform(
        lambda x: x.interpolate(method='linear'))

    df_cleaned['x_interpolated'] = df_cleaned['cx_interpolated'] - \
        (df_cleaned['w'] / 2)
    df_cleaned['y_interpolated'] = df_cleaned['cy_interpolated'] - \
        (df_cleaned['h'] / 2)

    output_cols = ['frame', 'track_id', 'x', 'y', 'w',
                   'h', 'score', 'class1', 'class2', 'class3']
    df_cleaned[output_cols].to_csv('Deep-EIoU-output_interpolated.txt',header=False, index=False)
    return df_cleaned

def main():
    output_data_filename = "Deep-EIoU-output.txt"
    output_data = load_output_data(output_data_filename)

    target_ids = output_data['track_id'].value_counts().nlargest(
        22).index.tolist()
    top_3 = target_ids[:3]
    bottom_3 = target_ids[-3:]
    target_ids = top_3 + bottom_3
    print(f"Selected Player IDs for Analysis: {target_ids}")
    # 課題1：選手軌跡の可視化
    filtered_df = output_data[output_data['track_id'].isin(target_ids)]
    plot_player_trajectories(filtered_df, target_ids)

    # 課題2：速度・加速度を用いた分析
    plot_player_speed_acceleration(filtered_df, target_ids, smooth_window=0,
                                   output_filename='player_speed_acceleration_no_smoothing.png')
    cleaned_df = interpolate_missing_frames(filtered_df)
    plot_player_speed_acceleration(cleaned_df, target_ids, smooth_window=5,
                                   output_filename='player_speed_acceleration_interpolated.png')

if __name__ == "__main__":
    main()
