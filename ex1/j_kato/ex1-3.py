import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd


data_path = "/mnt/datapool00/laliga_23/skillcorner_v2/tracking/1018887.json"

player_team_path = "/mnt/datapool00/laliga_23/skillcorner_v2/match_test/1018887.json"

with open(data_path, "r") as f:
    data = json.load(f)

with open(player_team_path, "r") as f:
    team_data = json.load(f)

fig, ax = plt.subplots()

def draw_pitch(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")

    for spine in ax.spines.values():
        spine.set_visible(False)
    
    ax.plot([-52.5, 52.5], [-34, -34], color="black")
    ax.plot([-52.5, 52.5], [34, 34], color="black")
    ax.plot([-52.5, -52.5], [-34, 34], color="black")
    ax.plot([52.5, 52.5], [-34, 34], color="black")

    ax.plot([0, 0], [-34, 34], color="black")

    circle = plt.Circle((0, 0), 9.15, fill=False, color="black")
    ax.add_patch(circle)

    # 左
    ax.plot([-52.5, -36], [-20.16, -20.16], color="black")
    ax.plot([-52.5, -36], [20.16, 20.16], color="black")
    ax.plot([-36, -36], [-20.16, 20.16], color="black")

    # 右
    ax.plot([52.5, 36], [-20.16, -20.16], color="black")
    ax.plot([52.5, 36], [20.16, 20.16], color="black")
    ax.plot([36, 36], [-20.16, 20.16], color="black")

    ax.set_facecolor("#6CAB64")  






# trackable_objectとteam_idの対応辞書を作る
track_to_team = {}
for p in team_data["players"]:
    track_to_team[p["trackable_object"]] = p["team_id"]

home_id = team_data["home_team"]["id"]
away_id = team_data["away_team"]["id"]

home_color = team_data["home_team_kit"]["jersey_color"]
away_color = team_data["away_team_kit"]["jersey_color"]

def update(frame_idx):
    ax.clear()
    draw_pitch(ax)

    frame=data[frame_idx]

    if len(frame["data"])==0:
        return

    objects=frame["data"]

    players=[]
    ball=[]

    for obj in objects:
        if "z" in obj:
            ball.append(obj)
        else:
            players.append(obj)
            print(obj)

    bx=[b["x"] for b in ball] 
    by=[b["y"] for b in ball]

    trail_x = []
    trail_y = []

    for i in range(max(0, frame_idx-5), frame_idx+1):
        frame = data[i]

        if len(frame["data"]) == 0:
            continue

        for obj in frame["data"]:
            if "z" in obj:  
                trail_x.append(obj["x"])
                trail_y.append(obj["y"])
    
    px_home, py_home = [], []
    px_away, py_away = [], []


    for obj in players:
        tid = obj["trackable_object"]

        if tid in track_to_team:
            team_id = track_to_team[tid]

            if team_id == home_id:
                px_home.append(obj["x"])
                py_home.append(obj["y"])
            elif team_id == away_id:
                px_away.append(obj["x"])
                py_away.append(obj["y"])

    ax.scatter(px_home, py_home, c=home_color, label="Home")
    ax.scatter(px_away, py_away, c=away_color, label="Away")
    ax.scatter(trail_x, trail_y, c="white", alpha=0.3, s=30) 
    ax.scatter(bx, by,  c="white", edgecolors="black", s=100,label="Ball")

    ax.set_xlim(-60,60)
    ax.set_ylim(-40,40)

    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=3)

    ax.set_aspect('equal')

    ax.set_title(f"Frame {frame_idx}")

ani = FuncAnimation(fig, update, frames=200, interval=50)

ani.save("BallTrajectoryAnimation.gif", writer="pillow")