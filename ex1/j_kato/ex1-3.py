import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd

#トラッキングデータのデータパス
data_path = "/mnt/datapool00/laliga_23/skillcorner_v2/tracking/1018887.json"

#チーム情報を含んだファイルのデータパス
player_team_path = "/mnt/datapool00/laliga_23/skillcorner_v2/match_test/1018887.json"

with open(data_path, "r") as f:
    data = json.load(f)

with open(player_team_path, "r") as f:
    team_data = json.load(f)

#描画用のfigureとaxesを作成
fig, ax = plt.subplots()

#フィールドの縦・横の長さを取得
pitch_length = team_data["pitch_length"]
pitch_width = team_data["pitch_width"]

#サッカーフィールドをグラフ上に描画する関数
def draw_field(ax):
    #軸のメモリを削除する
    ax.set_xticks([])
    ax.set_yticks([])
    #軸のラベルを削除する
    ax.set_xlabel("")
    ax.set_ylabel("")

    #グラフの外枠を非表示にする
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    #サッカーフィールドの外枠を描画
    ax.plot([-pitch_length/2, pitch_length/2],[-pitch_width/2, -pitch_width/2],color="black")
    ax.plot([-pitch_length/2, pitch_length/2],[pitch_width/2, pitch_width/2],color="black")
    ax.plot([-pitch_length/2, -pitch_length/2],[-pitch_width/2, pitch_width/2],color="black")
    ax.plot([pitch_length/2, pitch_length/2],[-pitch_width/2, pitch_width/2],color="black")

    #サッカーフィールドのセンターラインを描画
    ax.plot([0, 0], [-pitch_width/2, pitch_width/2], color="black")

    #サッカーフィールドのセンターサークルを描画
    circle = plt.Circle((0, 0), 9.15, fill=False, color="black")
    ax.add_patch(circle)

    #サッカーフィールドの左ペナルティエリアを描画
    ax.plot([-52.5, -36], [-20.16, -20.16], color="black")
    ax.plot([-52.5, -36], [20.16, 20.16], color="black")
    ax.plot([-36, -36], [-20.16, 20.16], color="black")

    #サッカーフィールドの右ペナルティエリアを描画
    ax.plot([52.5, 36], [-20.16, -20.16], color="black")
    ax.plot([52.5, 36], [20.16, 20.16], color="black")
    ax.plot([36, 36], [-20.16, 20.16], color="black")

    #背景を芝生色に設定
    ax.set_facecolor("#6CAB64")  



# trackable_objectとteam_idの対応辞書を作る
track_to_team = {}
for p in team_data["players"]:
    track_to_team[p["trackable_object"]] = p["team_id"]

#ホームチームとアウェイチームのIDをそれぞれ取得する
home_id = team_data["home_team"]["id"]
away_id = team_data["away_team"]["id"]

#ホームチームとアウェイチームのユニフォームカラーをそれぞれ取得する
home_color = team_data["home_team_kit"]["jersey_color"]
away_color = team_data["away_team_kit"]["jersey_color"]

#アニメーションを更新する関数
def update(frame_idx):
    #前フレームを消去
    ax.clear()
    #フィールド描画
    draw_field(ax)

    #現在フレームの取得
    frame=data[frame_idx]

    #データが存在しない場合は終了する
    if len(frame["data"])==0:
        return

    objects=frame["data"]

    players=[]
    ball=[]

    #ボールと選手を分類する
    for obj in objects:
        if "z" in obj: #z座標が存在するものをボールとして扱う
            ball.append(obj)
        else:
            players.append(obj)
            print(obj)

    bx=[b["x"] for b in ball] 
    by=[b["y"] for b in ball]

    trail_x = []
    trail_y = []

    #5フレーム前までのボールの座標を取得する
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


    #選手ごとにチーム分類
    for obj in players:
        tid = obj["trackable_object"]

        if tid in track_to_team:
            #対応辞書から選手のチームIDを取得
            team_id = track_to_team[tid]

            if team_id == home_id:
                px_home.append(obj["x"])
                py_home.append(obj["y"])
            elif team_id == away_id:
                px_away.append(obj["x"])
                py_away.append(obj["y"])

    #ホーム/アウェイそれぞれのチームの選手を描画
    ax.scatter(px_home, py_home, c=home_color, label="Home")
    ax.scatter(px_away, py_away, c=away_color, label="Away")
    #5フレーム前までのボールの軌跡を描画
    ax.scatter(trail_x, trail_y, c="white", alpha=0.3, s=30) 
    #ボールを描画
    ax.scatter(bx, by,  c="white", edgecolors="black", s=100,label="Ball")

    #描画範囲を設定
    ax.set_xlim(-pitch_length/2 - 5, pitch_length/2 + 5) 
    ax.set_ylim(-pitch_width/2 - 5, pitch_width/2 + 5)

    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=3)

    ax.set_aspect('equal')

    ax.set_title(f"Frame {frame_idx}")

#アニメーションを作成
ani = FuncAnimation(fig, update, frames=200, interval=50)

#GIFでアニメーションを保存
ani.save("BallTrajectoryAnimation.gif", writer="pillow")