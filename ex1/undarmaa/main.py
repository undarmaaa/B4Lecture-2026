import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

DATA_PATH = "/mnt/datapool00/laliga_23/skillcorner_v2"
MATCH_ID = 1018887
PLAYER_ID = 246
FPS = 10
START_FRAME = 10
END_FRAME = 200


def load_json(path):
    """Load a JSON file."""
    with open(path, "r") as file:
        return json.load(file)


def get_trackable_object(match_data, player_id):
    """Get trackable_object ID from player ID."""
    for player in match_data["players"]:
        if player["id"] == player_id:
            return player["trackable_object"], player["short_name"]

    raise ValueError(f"Player ID {player_id} was not found.")


def extract_player_positions(tracking_data, trackable_object):
    """Extract frame, x, y positions of one player."""
    positions = []

    for frame_data in tracking_data:
        frame = frame_data["frame"]

        for obj in frame_data["data"]:
            if obj["trackable_object"] == trackable_object:
                positions.append([frame, obj["x"], obj["y"]])
                break

    return np.array(positions)


def calculate_speed_acceleration(positions):
    """Calculate speed and acceleration from x-y coordinates."""
    frames = positions[:, 0]
    x = positions[:, 1]
    y = positions[:, 2]

    dx = np.diff(x)
    dy = np.diff(y)
    dt = 1 / FPS

    distance = np.sqrt(dx**2 + dy**2)
    speed = distance / dt

    acceleration = np.diff(speed) / dt

    speed_frames = frames[1:]
    acceleration_frames = frames[2:]

    return speed_frames, speed, acceleration_frames, acceleration


def plot_speed_acceleration(
    speed_frames,
    speed,
    acceleration_frames,
    acceleration,
    player_name,
    output_path,
):
    """Plot speed and acceleration from frame 10 to frame 500."""
    speed_mask = (speed_frames >= START_FRAME) & (speed_frames <= END_FRAME)
    acceleration_mask = (acceleration_frames >= START_FRAME) & (
        acceleration_frames <= END_FRAME
    )

    plt.figure(figsize=(12, 6))

    plt.plot(
        speed_frames[speed_mask],
        speed[speed_mask],
        label="Speed",
    )
    plt.plot(
        acceleration_frames[acceleration_mask],
        acceleration[acceleration_mask],
        label="Acceleration",
    )

    plt.xlabel("Frame")
    plt.ylabel("Value")
    plt.title(f"Speed and Acceleration of {player_name} (Player ID: {PLAYER_ID})")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def draw_pitch(ax, pitch_length, pitch_width):
    """Draw a simple soccer pitch."""
    x_min = -pitch_length / 2
    x_max = pitch_length / 2
    y_min = -pitch_width / 2
    y_max = pitch_width / 2

    ax.plot([x_min, x_max, x_max, x_min, x_min], [y_min, y_min, y_max, y_max, y_min])
    ax.axvline(0)
    ax.add_patch(plt.Circle((0, 0), 9.15, fill=False))

    # Left penalty area
    ax.plot(
        [-52.5, -36.0],
        [-20.16, -20.16],
        color="black",
    )
    ax.plot(
        [-36.0, -36.0],
        [-20.16, 20.16],
        color="black",
    )
    ax.plot(
        [-36.0, -52.5],
        [20.16, 20.16],
        color="black",
    )

    # Right penalty area
    ax.plot(
        [52.5, 36.0],
        [-20.16, -20.16],
        color="black",
    )
    ax.plot(
        [36.0, 36.0],
        [-20.16, 20.16],
        color="black",
    )
    ax.plot(
        [36.0, 52.5],
        [20.16, 20.16],
        color="black",
    )

    # Left goal area
    ax.plot(
        [-52.5, -47.0],
        [-9.16, -9.16],
        color="black",
    )
    ax.plot(
        [-47.0, -47.0],
        [-9.16, 9.16],
        color="black",
    )
    ax.plot(
        [-47.0, -52.5],
        [9.16, 9.16],
        color="black",
    )

    # Right goal area
    ax.plot(
        [52.5, 47.0],
        [-9.16, -9.16],
        color="black",
    )
    ax.plot(
        [47.0, 47.0],
        [-9.16, 9.16],
        color="black",
    )
    ax.plot(
        [47.0, 52.5],
        [9.16, 9.16],
        color="black",
    )

    ax.set_xlim(x_min - 5, x_max + 5)
    ax.set_ylim(y_min - 5, y_max + 5)
    ax.set_aspect("equal")
    ax.set_xlabel("X position [m]")
    ax.set_ylabel("Y position [m]")
    ax.grid(True)


def build_trackable_team_map(match_data):
    """Create mapping from trackable_object to team_id."""
    trackable_team_map = {}

    for player in match_data["players"]:
        trackable_team_map[player["trackable_object"]] = player["team_id"]

    return trackable_team_map


def plot_tracking_frame(tracking_data, match_data, frame_number, output_path):
    """Plot all players and the ball in one frame."""
    pitch_length = match_data["pitch_length"]
    pitch_width = match_data["pitch_width"]

    home_team_id = match_data["home_team"]["id"]
    away_team_id = match_data["away_team"]["id"]
    home_team_name = match_data["home_team"]["short_name"]
    away_team_name = match_data["away_team"]["short_name"]

    ball_trackable_object = match_data["ball"]["trackable_object"]
    target_trackable_object, target_player_name = get_trackable_object(
        match_data,
        PLAYER_ID,
    )

    trackable_team_map = build_trackable_team_map(match_data)

    target_frame = None
    for frame_data in tracking_data:
        if frame_data["frame"] == frame_number:
            target_frame = frame_data
            break

    if target_frame is None:
        raise ValueError(f"Frame {frame_number} was not found.")

    fig, ax = plt.subplots(figsize=(12, 8))
    draw_pitch(ax, pitch_length, pitch_width)

    home_x, home_y = [], []
    away_x, away_y = [], []
    unknown_x, unknown_y = [], []
    ball_x, ball_y = [], []
    target_x, target_y = [], []

    for obj in target_frame["data"]:
        x = obj["x"]
        y = obj["y"]
        trackable_object = obj["trackable_object"]

        if trackable_object == ball_trackable_object:
            ball_x.append(x)
            ball_y.append(y)
        elif trackable_object == target_trackable_object:
            target_x.append(x)
            target_y.append(y)
        else:
            team_id = trackable_team_map.get(trackable_object)

            if team_id == home_team_id:
                home_x.append(x)
                home_y.append(y)
            elif team_id == away_team_id:
                away_x.append(x)
                away_y.append(y)
            else:
                unknown_x.append(x)
                unknown_y.append(y)

    ax.scatter(home_x, home_y, s=70, label=f"Home: {home_team_name}")
    ax.scatter(away_x, away_y, s=70, label=f"Away: {away_team_name}")
    ax.scatter(unknown_x, unknown_y, s=50, label="Unknown")
    ax.scatter(ball_x, ball_y, s=120, marker="o", label="Ball")
    ax.scatter(
        target_x,
        target_y,
        s=180,
        marker="*",
        label=f"Target player: {target_player_name} (ID: {PLAYER_ID})",
    )

    ax.set_title(f"Tracking Data Visualization at Frame {frame_number}")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def create_tracking_animation(
    tracking_data,
    match_data,
    start_frame,
    end_frame,
    output_path,
):
    """Create tracking animation with a 5-frame ball trajectory."""
    pitch_length = match_data["pitch_length"]
    pitch_width = match_data["pitch_width"]

    home_team_id = match_data["home_team"]["id"]
    away_team_id = match_data["away_team"]["id"]
    ball_trackable_object = match_data["ball"]["trackable_object"]
    target_trackable_object, target_player_name = get_trackable_object(
        match_data,
        PLAYER_ID,
    )
    trackable_team_map = build_trackable_team_map(match_data)

    frame_map = {
        frame_data["frame"]: frame_data
        for frame_data in tracking_data
        if start_frame <= frame_data["frame"] <= end_frame
    }
    frames = sorted(frame_map.keys())

    fig, ax = plt.subplots(figsize=(12, 8))
    draw_pitch(ax, pitch_length, pitch_width)

    home_scatter = ax.scatter([], [], s=70, label="Home")
    away_scatter = ax.scatter([], [], s=70, label="Away")
    ball_scatter = ax.scatter([], [], s=120, label="Ball")
    target_scatter = ax.scatter([], [], s=180, marker="*", label="Target player")
    (ball_trail_line,) = ax.plot(
        [],
        [],
        marker="o",
        color="green",
        linewidth=2,
        label="Ball trail",
    )

    title = ax.set_title("")
    ax.legend(loc="upper right")

    def update(frame_number):
        frame_data = frame_map[frame_number]

        home_xy = []
        away_xy = []
        ball_xy = []
        target_xy = []

        for obj in frame_data["data"]:
            x = obj["x"]
            y = obj["y"]
            trackable_object = obj["trackable_object"]

            if trackable_object == ball_trackable_object:
                ball_xy.append([x, y])
            elif trackable_object == target_trackable_object:
                target_xy.append([x, y])
            else:
                team_id = trackable_team_map.get(trackable_object)

                if team_id == home_team_id:
                    home_xy.append([x, y])
                elif team_id == away_team_id:
                    away_xy.append([x, y])

        home_scatter.set_offsets(np.array(home_xy) if home_xy else np.empty((0, 2)))
        away_scatter.set_offsets(np.array(away_xy) if away_xy else np.empty((0, 2)))
        ball_scatter.set_offsets(np.array(ball_xy) if ball_xy else np.empty((0, 2)))
        target_scatter.set_offsets(
            np.array(target_xy) if target_xy else np.empty((0, 2))
        )

        trail_xy = []
        for past_frame in range(frame_number - 4, frame_number + 1):
            if past_frame not in frame_map:
                continue

            for obj in frame_map[past_frame]["data"]:
                if obj["trackable_object"] == ball_trackable_object:
                    trail_xy.append([obj["x"], obj["y"]])
                    break

        if trail_xy:
            trail_xy = np.array(trail_xy)
            ball_trail_line.set_data(trail_xy[:, 0], trail_xy[:, 1])
        else:
            ball_trail_line.set_data([], [])

        title.set_text(
            f"Tracking Animation: Frame {frame_number} "
            f"(Target: {target_player_name}, ID: {PLAYER_ID})"
        )

        return (
            home_scatter,
            away_scatter,
            ball_scatter,
            target_scatter,
            ball_trail_line,
            title,
        )

    animation = FuncAnimation(
        fig,
        update,
        frames=frames,
        interval=100,
        blit=False,
    )

    animation.save(output_path, fps=10)
    plt.close()


def main():
    tracking_path = f"{DATA_PATH}/tracking/{MATCH_ID}.json"
    match_path = f"{DATA_PATH}/match/{MATCH_ID}.json"

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    tracking_data = load_json(tracking_path)
    match_data = load_json(match_path)

    pitch_output_path = f"{output_dir}/pitch_frame_10.png"
    plot_tracking_frame(
        tracking_data,
        match_data,
        START_FRAME,
        pitch_output_path,
    )
    print(f"Saved pitch visualization to {pitch_output_path}")

    animation_output_path = f"{output_dir}/tracking_animation_10_500.mp4"
    create_tracking_animation(
        tracking_data,
        match_data,
        START_FRAME,
        END_FRAME,
        animation_output_path,
    )
    print(f"Saved animation to {animation_output_path}")

    trackable_object, player_name = get_trackable_object(match_data, PLAYER_ID)

    print(f"Player ID: {PLAYER_ID}")
    print(f"Player name: {player_name}")
    print(f"Trackable object: {trackable_object}")

    positions = extract_player_positions(tracking_data, trackable_object)

    print("Extracted position shape:", positions.shape)
    print("First 5 rows:")
    print(positions[:5])

    speed_frames, speed, acceleration_frames, acceleration = (
        calculate_speed_acceleration(positions)
    )

    output_path = f"{output_dir}/player_246_speed_acceleration_10_500.png"

    plot_speed_acceleration(
        speed_frames,
        speed,
        acceleration_frames,
        acceleration,
        player_name,
        output_path,
    )

    print(f"Saved graph to {output_path}")


if __name__ == "__main__":
    main()
