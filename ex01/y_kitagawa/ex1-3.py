import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.lines import Line2D


# 1. パスの設定
tracking_path = "/mnt/datapool00/laliga_23/skillcorner_v2/tracking/1018887.json"
matchData_path = "/mnt/datapool00/laliga_23/skillcorner_v2/match_test/1018887.json"

def load_data(tracking_path, matchData_path):
    with open(tracking_path, 'r') as f: #終わったら閉じる
        tracking_data = json.load(f) #中身を変換
    with open(matchData_path, 'r') as f:
        match_data = json.load(f)

    #辞書作成
    role_map = {}
    home_id = match_data.get('home_team', {}).get('id')
    away_id = match_data.get('away_team', {}).get('id')

    for player in match_data.get('players', []):
        p_id = player.get('trackable_object')
        t_id = player.get('team_id')
        
        if p_id is not None:
            role_map[p_id] = 'home' if t_id == home_id else 'away'

    ball = match_data.get('ball')
    if ball:
        b_id = ball.get('trackable_object')
        role_map[b_id] = 'ball'

    return tracking_data, role_map

def create_animation(tracking_data, role_map):
    STYLES = {
        'home': {'color':'red', 'size':60, 'z':3},
        'away': {'color':'blue', 'size': 60, 'z':3},
        'ball': {'color':'yellow', 'size': 30, 'z':5},
        'default': {'color':'gray', 'size':40, 'z':2}
    }

    frames = tracking_data[10:201]
    fig, ax = plt.subplots(figsize=(12,9))
    fig.patch.set_facecolor('#88B688')

#凡例作成 
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='UD Almería',
               markerfacecolor='red', markersize=10, ls=''),
        Line2D([0], [0], marker='o', color='w', label='Rayo Vallecano',
               markerfacecolor='blue', markersize=10, ls=''),
        Line2D([0], [0], marker='o', color='w', label='Ball',
               markerfacecolor='yellow', markeredgecolor='black', markersize=7, ls='')
    ]

    #凡例をピッチの外に配置
    # loc='lower center' で中央下に、bbox_to_anchor で位置を微調整します
    fig.legend(handles=legend_elements, loc='lower center', 
               bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False, fontsize=12)

    def draw_pitch():
        ax.set_facecolor("#88B688")
        line_cfg = {"color":"white", "fill":False, "lw":1}
        ax.add_patch(Rectangle((-52.5, -34), 105, 68, **line_cfg))
        ax.plot([0,0], [-34,34], color="white", lw=1, zorder=1)
        ax.add_patch(Circle((0,0), 9.15, **line_cfg))
        ax.scatter(0,0, color="white", s=15, zorder=1)

        for side in [-1, 1]:
            # コーナーアーク (4角)
            for y_sign in [-1, 1]:
                # theta1, theta2 で描く扇形を指定
                if side == -1 and y_sign == -1: t1, t2 = 0, 90
                elif side == -1 and y_sign == 1: t1, t2 = 270, 360
                elif side == 1 and y_sign == -1: t1, t2 = 90, 180
                else: t1, t2 = 180, 270
                ax.add_patch(Arc((side*52.5, y_sign*34), 2, 2, theta1=t1, theta2=t2, **line_cfg))

            # --- エリア関係 ---
            x_origin = -52.5 if side == -1 else 52.5
            
            # ペナルティエリア
            p_w, p_h = 16.5, 40.3
            x_p = x_origin if side == -1 else x_origin - p_w
            ax.add_patch(Rectangle((x_p, -20.15), p_w, p_h, **line_cfg))
            
            # ゴールエリア
            g_w, g_h = 5.5, 18.3
            x_g = x_origin if side == -1 else x_origin - g_w
            ax.add_patch(Rectangle((x_g, -9.15), g_w, g_h, **line_cfg))

            ax.add_patch(Rectangle((x_origin if side == -1 else x_origin, -3.66), side * 2, 7.32, **line_cfg))
            
            # ペナルティマーク (ゴールから11m)
            x_m = x_origin - (side*11)
            ax.scatter(x_m, 0, color="white", s=15, zorder=1)

            # ペナルティコアーク (Dの字の半円)
            # ペナルティマークを中心に、半径 9.15m。thetaで描画角度を指定。
            # 左側なら -53度〜53度、右側なら 127度〜233度
            angle = 180 if side == 1 else 0
            ax.add_patch(Arc((x_m, 0), 18.3, 18.3, angle=angle, theta1=-53, theta2=53, **line_cfg))

        ax.set_xlim(-58,58)
        ax.set_ylim(-45,40)
        ax.set_aspect('equal')
        ax.axis('off')

    def update(i):
        ax.clear()
        draw_pitch()
        frame_data = frames[i]

        ax.legend(handles=legend_elements, loc='upper center', 
                  bbox_to_anchor=(0.5, -0.02), ncol=3, frameon=False, fontsize=10)

        ts = frame_data.get('timestamp', '00:00:00.00')
        header_text = f"Frame: {i+10}   Timestamp: {ts}"
        ax.text(0, 36, header_text, fontsize=11, ha='center')

        ball_history = []
        current_ball_pos = None
        for person in frame_data.get('data', []):
            p_id = person.get('trackable_object')
            role = role_map.get(p_id, 'ball' if p_id is None else 'default')
            
            if role == 'ball':
                x, y = person.get('x'), person.get('y')
                if x is not None and y is not None:
                    current_ball_pos = (x, y)
                    ball_history.append(current_ball_pos)
        
        # 軌跡を最大5フレーム（現在の点を含めて6点分）に制限
        if len(ball_history) > 6:
            ball_history.pop(0)

        # ボールの軌跡を描画
        if len(ball_history) > 1:
            hx, hy = zip(*ball_history)
            # 黄色の半透明な線で軌跡を表示
            ax.plot(hx, hy, color="yellow", lw=2, alpha=0.6, zorder=4)

        # 全プレイヤーとボールの描画（既存のループ）
        for person in frame_data.get('data', []):
            p_id = person.get('trackable_object')
            x, y = person.get('x'), person.get('y')
            if x is not None and y is not None:
                role = role_map.get(p_id, 'ball' if p_id is None else 'default')
                style = STYLES.get(role, STYLES['default'])
                ax.scatter(x, y, color=style['color'], s=style['size'], 
                           zorder=style['z'], edgecolors="white", linewidth=0.8)

    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval = 100)
    ani.save("tracking_101887_5s.mp4", writer='ffmpeg')
    print("Animation saved as tracking_101887_5s.mp4")

if __name__ == "__main__":
    tracking, r_map = load_data(tracking_path, matchData_path)
    create_animation(tracking, r_map)