import json
import matplotlib.pyplot as plt
import numpy
import pandas as pd


data_path = "/mnt/datapool00/laliga_23/skillcorner_v2/tracking/1018887.json"
player_data_path = "/mnt/datapool00/laliga_23/skillcorner_v2/metadata/players.json"

with open(data_path, "r") as f:
    data = json.load(f)

with open(player_data_path, "r") as f:
    player_data = json.load(f)

for p in player_data:
    if p["id"]==246:
        target_track_id = p["trackable_object"]

px=[]
py=[]
times=[]

for frame_idx in range(500):
    frame=data[frame_idx]
    objects=frame["data"]


    for obj in objects:
        if obj["trackable_object"]==target_track_id:
            px.append(obj["x"])
            py.append(obj["y"])
            times.append(frame_idx)

speed=[]
for i in range(1,len(px)):
    dx=px[i]-px[i-1]
    dy=py[i]-py[i-1]

    distance=(dx**2+dy**2)**0.5
    v=distance/0.1


    speed.append(v)

acceleration=[]

for i in range(1,len(speed)):
    dv=speed[i]-speed[i-1]
    a=dv/0.1

    acceleration.append(a)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

time_speed = [t*0.1 for t in times[1:]]
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
