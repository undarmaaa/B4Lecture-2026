import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# 保存先フォルダ（result）の作成
output_dir = 'result'
# folder（ディレクトリ）が存在しない場合は自動で作成する
os.makedirs(output_dir, exist_ok=True)

# パスの設定
result_path = '/home/y_kitagawa/B4Lecture-2026/ex02/y_kitagawa/117093_trimmed.txt'

# データの読み込み
cols = ['frame', 'id', 'x', 'y', 'w', 'h', 'conf', 'class', 'vis', 'none']
df = pd.read_csv(result_path, header=None, names=cols)

# 中心座標 (cx, cy) の計算
df['cx'] = df['x'] + df['w'] / 2
df['cy'] = df['y'] + df['h'] / 2

# 速度・加速度の計算
def calculate_kinematics(group):
    group = group.sort_values('frame')
    dt = group['frame'].diff()
    dcx = group['cx'].diff()
    dcy = group['cy'].diff()
    
    group['speed'] = np.sqrt(dcx**2 + dcy**2) / dt
    group['acceleration'] = group['speed'].diff() / dt
    return group

print("INFO: Calculating kinematics...")
df = df.groupby('id', group_keys=False).apply(calculate_kinematics)

# 異常値の多い4名 ＋ GK(13) の自動選別
valid_df = df.dropna(subset=['speed'])

# 13番を除外したデータから、速度の最大値が大きいトップ4のIDを自動抽出
anomaly_candidates = valid_df[valid_df['id'] != 13]
top4_ids = anomaly_candidates.sort_values(by='speed', ascending=False)['id'].unique()[:4]

# 13番（GK）と合体（5人のリストにする）
target_ids = [13] + list(top4_ids)

print(f"INFO: Target IDs for plotting: {target_ids}\n")

# --- 【グラフ1】軌跡の可視化 ---
plt.figure(figsize=(12, 8))

for tid in target_ids:
    player_data = df[df['id'] == tid]
    plt.plot(player_data['cx'], player_data['cy'], marker='o', markersize=2, label=f'ID: {tid}', alpha=0.7)

plt.title('Player Trajectories')
plt.xlabel('X coordinate (pixels)')
plt.ylabel('Y coordinate (pixels)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.5)
plt.gca().invert_yaxis() 
plt.tight_layout()

save_path_traj = os.path.join(output_dir, 'trajectory_result.png')
plt.savefig(save_path_traj)
print(f"SUCCESS: 軌跡グラフを保存 -> {os.path.abspath(save_path_traj)}")


# --- 【グラフ2】速度の可視化 ---
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()  # 2次元配列を1次元にしてループしやすくする

for i, tid in enumerate(target_ids):
    ax = axes[i]
    player_data = df[df['id'] == tid]
    
    # 赤色の線と点で1人ずつの速度を描画
    ax.plot(player_data['frame'], player_data['speed'], 
            color='firebrick', marker='o', markersize=2, linestyle='-', linewidth=1, alpha=0.8)
    
    ax.set_title(f'ID: {tid} Speed', fontsize=12)
    ax.set_xlabel('Frame', fontsize=10)
    ax.set_ylabel('Speed (pixels/frame)', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)

# 6個目の余った枠（右下）はデータがないので非表示にする
if len(target_ids) < len(axes):
    axes[-1].axis('off')

plt.tight_layout()

save_path_speed = os.path.join(output_dir, 'speed_subplots.png')
plt.savefig(save_path_speed, dpi=300)
print(f"SUCCESS: 速度サブプロットを保存 -> {os.path.abspath(save_path_speed)}")

