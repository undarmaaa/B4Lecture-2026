import json
import matplotlib.pyplot as plt
import numpy
import pandas as pd

#トラッキングデータのデータパス
data_path = "/mnt/datapool00/laliga_23/skillcorner_v2/tracking/1018887.json"
#選手情報を含んだファイルのデータパス
player_data_path = "/mnt/datapool00/laliga_23/skillcorner_v2/metadata/players.json"

with open(data_path, "r") as f:
    data = json.load(f)

with open(player_data_path, "r") as f:
    player_data = json.load(f)

#player_id=246の選手に対応するtrackable_object を取得
for p in player_data:
    if p["id"]==246:
        target_track_id = p["trackable_object"]

px=[]
py=[]
times=[]

#0から500フレームのデータを取得する
for frame_idx in range(500):
    frame=data[frame_idx]
    objects=frame["data"]

    #現在のフレーム内の全オブジェクトあら対象選手の座標を取得する
    for obj in objects:
        if obj["trackable_object"]==target_track_id:
            px.append(obj["x"])
            py.append(obj["y"])
            times.append(frame_idx)

speed=[]
#隣接フレーム間の移動距離から速度を計算
for i in range(1,len(px)):
    #x方向・y方向の移動量
    dx=px[i]-px[i-1]
    dy=py[i]-py[i-1]

    #ユーグリッド距離を計算
    distance=(dx**2+dy**2)**0.5
    #速度を計算
    v=distance/0.1

    speed.append(v)

acceleration=[]
#隣接時刻の速度変化から加速度を計算
for i in range(1,len(speed)):
    #速度差を計算
    dv=speed[i]-speed[i-1]
    #加速度を計算
    a=dv/0.1

    acceleration.append(a)

# 縦2つのグラフを作成
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

#速度・加速度に対応する時間軸を作成
#速度は1フレーム差分なので times[1:]
time_speed = [t*0.1 for t in times[1:]]
#加速度は2フレーム差分なので times[2:]
time_acc = [t*0.1 for t in times[2:]]

ax1.plot(time_speed, speed)
ax1.set_title("Speed")
ax1.set_xlabel("time [s]")
ax1.set_ylabel("m/s")

ax2.plot(time_acc, acceleration)
ax2.set_title("Acceleration")
ax2.set_xlabel("time [s]")
ax2.set_ylabel("m/s^2")


plt.tight_layout()
plt.savefig("speed_acc.png")
