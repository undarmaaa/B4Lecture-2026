import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation # pltで描画した図をパラパラ漫画みたいに動かすやつ
from mplsoccer import Pitch
import pandas as pd
import numpy as np


# ==========================================
# 定数（各データのパス）
# ==========================================
TRACKING_PATH = "/mnt/datapool00/laliga_23/skillcorner_v2/tracking/1018887.json"
META_PATH = "/mnt/datapool00/laliga_23/skillcorner_v2/match_test/1018887.json"

# ==========================================
# 関数定義
# ==========================================

def load_data(tracking_path, meta_path):
    """
    指定されたパスからトラッキングデータとメタデータを読み込む。
    
    Parameters:
        tracking_path (str): トラッキングデータ(JSON)のファイルパス
        meta_path (str): メタデータ(JSON)のファイルパス
        
    Returns:
        tuple: (トラッキングデータのリスト, メタデータの辞書)
    """
    # データの読み込み
    # with ... as f: はファイルを f という名前で開き、このブロックの処理が終わったら自動的にファイルを閉じるという意味
    with open(tracking_path, 'r') as f:
        data = json.load(f)
    """
    フレームごとの選手IDとその座標がある
    [
      {
        "frame": 1,
        "timestamp": "00:00:00.00",
        "data": [
          {"trackable_object": 246, "x": -10.5, "y": 5.2},
          {"trackable_object": 555, "x": -12.0, "y": 6.0}
        ]
      },
      {
        "frame": 2, ...
      }
    ]
    """

    with open(meta_path, 'r') as f:
        meta = json.load(f)
    """
    対戦チームと選手の所属チームの情報が辞書として保存されてる
    {
      "home_team": {"id": 101, "name": "Team A"},
      "away_team": {"id": 102, "name": "Team B"},
      "players": [
        {"trackable_object": 246, "team_id": 101, "name": "Player X"},
        {"trackable_object": 300, "team_id": 102, "name": "Player Y"}
      ],
      "ball": {"trackable_object": 555}
    }
    """
    return data, meta


def create_player_team_map(meta):
    """
    メタデータから、選手IDをキー、所属チーム(home/away/ball)を値とする辞書を作成する。
    
    Parameters:
        meta (dict): メタデータの辞書
        
    Returns:
        tuple: (選手IDと所属チームの対応辞書, ホームチーム名, アウェイチーム名)
    """
    # チーム名と選手IDの対応辞書作成
    home_name = meta['home_team']['name']
    away_name = meta['away_team']['name']
    player_team_map = {}

    # 選手
    for p in meta.get('players', []):
        p_id = p['trackable_object']
        if p['team_id'] == meta['home_team']['id']:
            player_team_map[p_id] = 'home'
        elif p['team_id'] == meta['away_team']['id']:
            player_team_map[p_id] = 'away'
    """
    例
    p = {"trackable_object": 246, "team_id": 101, "name": "Player A"}
    p_id = p['trackable_object'] # 246
    p['team_id'] == meta['home_team']['id'] # 101 == 101 -> True
    player_team_map[246] = 'home'
    """

    # ボール
    if 'ball' in meta:
        player_team_map[meta['ball']['trackable_object']] = 'ball'

    return player_team_map, home_name, away_name


def create_tracking_animation(data, player_team_map, home_name, away_name, output_filename, num_frames):
    """
    トラッキングデータを可視化し、アニメーション動画として保存する。
    
    Parameters:
        data (list): トラッキングデータのリスト
        player_team_map (dict): 選手IDと所属チームの対応辞書
        home_name (str): ホームチーム名
        away_name (str): アウェイチーム名
        output_filename (str): 保存する動画のファイル名
        num_frames (int): 描画するフレーム数
    """
    # アニメーションの描画設定
    pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68, 
                  pitch_color='forestgreen', line_color='white')
    
    fig, ax = pitch.draw(figsize=(10, 7)) # ピッチを描画して fig と ax を取得

    # 毎フレーム呼び出される更新関数（この関数の中にネストしておくことで、引数なしで変数を参照できます）
    def update(frame_idx):
        # 前のフレームの描画を一度消去する
        ax.cla()
        
        # 毎フレームピッチを再描画
        pitch.draw(ax=ax) 
        ax.set_title(f"Frame: {frame_idx}")

        # 指定フレームのデータを取得
        frame_data = data[frame_idx]
        
        # 選手とボールのプロット
        for obj in frame_data['data']:
            p_id = obj['trackable_object']
            team = player_team_map.get(p_id)
            
            # チームごとに色分けしてプロット
            if team == 'home':
                ax.scatter(obj['x'], obj['y'], c='red', edgecolors='white', label=home_name, zorder=10)
            elif team == 'away':
                ax.scatter(obj['x'], obj['y'], c='black', edgecolors='white', label=away_name, zorder=10)
            elif team == 'ball':
                ax.scatter(obj['x'], obj['y'], c='yellow', edgecolors='black', label='Ball', zorder=10)

        # 凡例の描画（データがある場合のみ）
        handles, labels = ax.get_legend_handles_labels() # get_legend_handles_labels() は現在のグラフに描画されている要素から凡例のハンドルとラベルを取得する関数
        if handles:
            by_label = dict(zip(labels, handles)) # 凡例の重複を防ぐために辞書に変換
            # 凡例を枠外下部(bbox_to_anchor)に配置
            ax.legend(by_label.values(), by_label.keys(), loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)

    # FuncAnimationは指定した関数(update)をフレームごとに呼び出してアニメーションを作成する関数
    # interval=100 は 100ミリ秒(0.1秒)間隔 = 10fps でフレームを更新するという意味
    ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=100)

    # mp4として保存
    ani.save(output_filename, writer='ffmpeg', fps=10)


def calculate_and_plot_metrics(data, target_id, output_filename):
    """
    特定の選手の速度と加速度を計算し、時系列グラフとして保存する。
    
    Parameters:
        data (list): トラッキングデータのリスト
        target_id (int): 対象となる選手のID
        output_filename (str): 保存するグラフのファイル名
    """
    
    frames = [] # フレーム番号のリスト
    x_coords = [] # x座標のリスト
    y_coords = [] # y座標のリスト
    
    # 全フレームをループして、ターゲット選手の座標を抽出
    for frame_info in data:
        frame_idx = frame_info['frame']
        found = False # ターゲット選手がこのフレームにいるかどうかを示すフラグ
        for obj in frame_info['data']:
            if obj['trackable_object'] == target_id:
                frames.append(frame_idx)
                x_coords.append(obj['x'])
                y_coords.append(obj['y'])
                found = True
                break
        
        # 選手がカメラ外にいてデータがないフレームは欠損値(NaN)として扱う
        if not found:
            frames.append(frame_idx)
            x_coords.append(np.nan)
            y_coords.append(np.nan)
            
    # pandasのデータフレーム(表形式)に変換
    df = pd.DataFrame({'frame': frames, 'x': x_coords, 'y': y_coords})
    
    # 速度と加速度の計算
    # 1フレーム間の時間差 (dt) は 0.1秒
    dt = 0.1
    df['time'] = df['frame'] * dt
    
    # .diff() で１フレーム前との差分を計算して、dx と dy を求める
    df['dx'] = df['x'].diff()
    df['dy'] = df['y'].diff()
    
    # dist = √(dx^2 + dy^2)
    df['dist'] = np.sqrt(df['dx']**2 + df['dy']**2)
    
    # 速度 (m/s) = 距離 / 0.1秒
    df['speed'] = df['dist'] / dt
    
    # 加速度 (m/s^2) = 速度の変化量 / 0.1秒
    df['acceleration'] = df['speed'].diff() / dt
    
    # グラフの描画
    # 上下に2つのグラフを並べる (2行1列)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # グラフのタイトルと軸ラベルの設定
    fig.suptitle(f"trackable_object: {target_id}", fontsize=14)
    ax1.set_title("Frames 10-500", fontsize=12)
    
    # 上段: 速度グラフ
    ax1.plot(df['time'], df['speed'], color='blue', label='Speed (m/s)')
    ax1.set_ylabel('Speed [m/s]')
    ax1.set_ylim(0, 5.2)
    # ax1.legend()
    ax1.grid(True)
    
    # 下段: 加速度グラフ
    ax2.plot(df['time'], df['acceleration'], color='red', label='Acceleration (m/s^2)')
    ax2.set_ylabel('Acceleration [m/s^2]')
    ax2.set_ylim(-7.5, 6.0)
    ax2.set_xlabel('Time [s]')
    ax1.set_xlim(1, 50)
    ax2.set_xlim(1, 50)

    #ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_filename)


# ==========================================
# メイン処理
# ==========================================
def main():
    # 1. データの読み込み
    data, meta = load_data(TRACKING_PATH, META_PATH)
    
    # 2. チームと選手の対応表を作成
    player_team_map, home_name, away_name = create_player_team_map(meta)
    
    # 3. アニメーションの作成
    num_frames = min(200, len(data)) # 描画するフレーム数を200に制限
    create_tracking_animation(
        data=data, 
        player_team_map=player_team_map, 
        home_name=home_name, 
        away_name=away_name, 
        output_filename="tracking_1018887.mp4",
        num_frames=num_frames
    )
    
    # 4. 速度・加速度の計算とグラフ化
    trackable_object = 256 # player_id = 246 が trackable_object = 256 らしい
    calculate_and_plot_metrics(
        data=data, 
        target_id=trackable_object, 
        output_filename="player_246_metrics.png"
    )

if __name__ == "__main__":
    main()