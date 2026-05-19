import json
import matplotlib.pyplot as plt
import numpy as np

#パスを設定
tracking_path = "/mnt/datapool00/laliga_23/skillcorner_v2/tracking/1018887.json"

def analyze(target_id, start_frame, end_frame):
    #データ読み込み
    with open(tracking_path, 'r') as f:
        tracking_data = json.load(f)
    frames = tracking_data[start_frame:end_frame]

    positions = []
    timestamps = []

    for i, frame in enumerate(frames):
        for person in frame.get('data', []):
            if person.get('trackable_object') == target_id:
                x, y = person.get('x'), person.get('y')
                if x is not None and y is not None:
                    positions.append(np.array([x, y]))
                    timestamps.append(i*0.1) #１０Hzのデータなので、0.1をかけて秒に変換
    
    positions = np.array(positions)

    #速度計算
    dist = np.sqrt(np.sum(np.diff(positions, axis=0)**2, axis=1))#距離
    velocities = dist / 0.1 #距離÷時間

    #加速度計算
    accelerations = np.diff(velocities) / 0.1 #速度÷時間

    #グラフ作成
    #上下に2つグラフを配置
    fig, (ax1, ax2) = plt.subplots(2,1, figsize=(10,8), sharex=True)
    #速度プロット。2つの座標を要するため、1つデータをずらす
    ax1.plot(timestamps[1:], velocities, color="blue", label='Speed (m/s)')
    ax1.set_ylabel('Speed [m/s]')
    ax1.set_title(f'Player {target_id} Physics (Frame {start_frame}-{end_frame})')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    #加速度プロット。さらにもう1つの座標を要するため、もう1つデータをずらす
    ax2.plot(timestamps[2:], accelerations, color='red', label='Accelerasion {m/s^2}')
    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel('Acceleration [m/s^2]')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plt.savefig("player_physics.png")

if __name__ == "__main__":
    analyze(256, 10, 501)