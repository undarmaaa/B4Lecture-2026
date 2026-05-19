import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
from spaceeval.sports.soccer.obso.vis_obso import plot_pitch
from tqdm import tqdm


def load_tracking_data(skillcorner_match_id: int) -> pd.DataFrame:
    skillcorner_tracking_dir = data_path + "/tracking"
    tracking_df = pd.read_json(
        skillcorner_tracking_dir + f"/{skillcorner_match_id}.json")
    return tracking_df


def load_match_data(skillcorner_match_id: int) -> pd.DataFrame:
    skillcorner_match_dir = data_path + "/match"
    match_json = skillcorner_match_dir + f"/{skillcorner_match_id}.json"
    with open(match_json, "r") as f:
        match_data = json.load(f)
    return match_data


def prepare_trackable_frame_to_plot(frame_data: list[dict], players_lookup: dict, home_team_id: int, ball_id: int) -> tuple[list[tuple], list[tuple], list[tuple]]:
    home_players_coords = []
    away_players_coords = []
    ball_coords = []
    for trackable in frame_data:
        if trackable["trackable_object"] == ball_id:
            ball_coords.append((trackable["x"], trackable["y"]))
            continue

        trackable_metadata = players_lookup.get(
            trackable["trackable_object"], {})
        is_home_team = trackable_metadata.get("team_id") == home_team_id
        if is_home_team:
            home_players_coords.append((trackable["x"], trackable["y"]))
        else:
            away_players_coords.append((trackable["x"], trackable["y"]))

    return home_players_coords, away_players_coords, ball_coords


def prepare_ball_trail_coords(tracking_df: pd.DataFrame, frame_row: pd.Series, ball_id: int) -> list[tuple]:
    ball_trail_coords = []
    current_frame = frame_row["frame"]
    for i in range(max(0, current_frame - 5), current_frame):
        row = tracking_df[tracking_df["frame"] == i]
        if row.empty:
            continue
        frame_data = row.iloc[0]["data"]
        for trackable in frame_data:
            if trackable["trackable_object"] == ball_id:
                ball_trail_coords.append((trackable["x"], trackable["y"]))
                break
    return ball_trail_coords


def draw_animation(
        fname: str,
        tracking_df: pd.DataFrame,
        players_lookup: dict,
        home_team_id: int,
        ball_id: int,
        fps: int = 20
):
    FFMpegWriter = animation.writers['ffmpeg']
    metadata = {}
    writer = FFMpegWriter(fps=fps, metadata=metadata)
    fname = f"{fname}.mp4"
    field_dimen = (105.0, 68.0)
    fig, ax = plot_pitch(field_dimen=field_dimen)
    index = tracking_df.index

    with writer.saving(fig, fname, 100):
        for i in tqdm(index, desc="Generating animation"):
            row = tracking_df.loc[i]
            if not isinstance(row["data"], list) or len(row["data"]) == 0:
                frame_data = []
            else:
                frame_data = row["data"]

            home_players_coords, away_players_coords, ball_coords = prepare_trackable_frame_to_plot(
                frame_data, players_lookup, home_team_id, ball_id)
            ball_trail_coords = prepare_ball_trail_coords(
                tracking_df, row, ball_id)
            # create scatter plot size bigger for all

            figobjs = []
            if frame_data is not None and len(frame_data) > 0:
                figobjs.append(
                    ax.scatter(ball_coords[0][0], ball_coords[0][1],
                               label="Ball", c='yellow', alpha=0.7, s=100))
                figobjs.append(
                    ax.scatter([coord[0] for coord in home_players_coords],
                               [coord[1] for coord in home_players_coords],
                               label='Home', c='black', alpha=0.7, s=100))
                figobjs.append(
                    ax.scatter([coord[0] for coord in away_players_coords],
                               [coord[1] for coord in away_players_coords],
                               label='Away', c='red', alpha=0.7, s=100))
                if len(ball_trail_coords) > 0:
                    figobjs.append(
                        ax.scatter([coord[0] for coord in ball_trail_coords],
                                   [coord[1] for coord in ball_trail_coords],
                                   c='yellow', alpha=0.3, s=20))

            figobjs.append(fig.legend(loc='lower center', ncol=3))
            frame_number = int(row["frame"])
            timestring = f"Frame: {frame_number}"
            objs = ax.text(-2.5, field_dimen[1]/2.+1., timestring, fontsize=14)
            figobjs.append(objs)

            writer.grab_frame()
            for figobj in figobjs:
                figobj.remove()
    plt.clf()
    plt.close(fig)

def plot_player_speed_acceleration(tracking_df: pd.DataFrame, player_id: int, player_df: pd.DataFrame):
    trackable_object = player_df[player_df["id"] == player_id]
    first_name = trackable_object["first_name"].values[0]
    last_name = trackable_object["last_name"].values[0]
    player_name = f"{first_name} {last_name}".strip()
    trackable_object = trackable_object["trackable_object"].values[0]
    player_data = tracking_df[tracking_df["data"].apply(lambda x: any(
        trackable["trackable_object"] == trackable_object for trackable in x))]
    player_data = player_data[player_data["frame"].isin(range(10, 500))]

    player_data["x"] = player_data["data"].apply(lambda x: next(
        (trackable["x"] for trackable in x if trackable["trackable_object"] == trackable_object), None))
    player_data["y"] = player_data["data"].apply(lambda x: next(
        (trackable["y"] for trackable in x if trackable["trackable_object"] == trackable_object), None))

    player_data["x"] = pd.to_numeric(player_data["x"], errors="coerce")
    player_data["y"] = pd.to_numeric(player_data["y"], errors="coerce")
    player_data = player_data.dropna(subset=["x", "y"]).reset_index(drop=True)

    fps = 10 # Assuming 10 frames per second
    player_data["velocity"] = ((player_data["x"].diff()**2 + player_data["y"].diff()**2)**0.5) * fps
    player_data["acceleration"] = player_data["velocity"].diff() * fps

    # Use time in seconds for plotting
    time_data = player_data["frame"] / fps

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    ax1.set_ylabel('Speed [m/s]', color='tab:blue')
    ax1.plot(time_data, player_data["velocity"], color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel('Acceleration [m/s²]', color='tab:red')
    ax2.plot(time_data, player_data["acceleration"], color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    graph_title = f'{player_name} (player_id={player_id}, trackable_object={trackable_object})\nFrame 10-500'
    plt.text(s=graph_title,
             x=0.5, y=0.95, transform=fig.transFigure, fontsize=16, ha='center')
    plt.savefig(f'player_{player_id}_speed_acceleration_10_500.png')
    plt.clf()
    plt.close(fig)


if __name__ == "__main__":
    data_path = "/mnt/datapool00/laliga_23/skillcorner_v2"
    skillcorner_match_id = 1018887

    tracking_df = load_tracking_data(skillcorner_match_id)
    match_data_json = load_match_data(skillcorner_match_id)
    players_json = match_data_json.get("players", [])
    ball_json = match_data_json.get("ball", {})
    ball_id = ball_json.get("trackable_object", -1)

    players_lookup = {player["trackable_object"]: player for player in players_json}
    home_team_id = -1
    away_team_id = -1
    for trackable_object, player in players_lookup.items():
        team_id = player.get("team_id")
        if home_team_id == -1 and team_id is not None:
            home_team_id = team_id
        elif team_id != home_team_id and away_team_id == -1 and team_id is not None:
            away_team_id = team_id
        else:
            break

    # draw animation for first 500 frames
    tracking_df = tracking_df[tracking_df["frame"].isin(range(500))]
    draw_animation(f"match_{skillcorner_match_id}_tracking", tracking_df,
                   players_lookup, home_team_id, ball_id, fps=10)

    # plot speed and acceleration for player 246
    player_df = pd.DataFrame(players_json)
    plot_player_speed_acceleration(tracking_df, 246, player_df)
