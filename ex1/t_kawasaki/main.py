"""
ex1: SkillCornerトラッキングデータの可視化

本スクリプトは以下を実行する:
1. SkillCorner形式のトラッキングデータを読み込み
2. 1フレーム分の選手・ボール位置をピッチに描画（フクダ電子アリーナ風）
3. 指定選手の速度・加速度を計算し折れ線グラフとして保存
4. 全フレームをアニメーション動画(mp4)として保存（ボール軌跡付き）

使い方:
    uv run python main.py

入力:
    /mnt/datapool00/laliga_23/skillcorner_v2/match/{match_id}.json
    /mnt/datapool00/laliga_23/skillcorner_v2/tracking/{match_id}.json

出力:
    test_frame_fukuari.png
    player_{id}_speed_acceleration_{start}_{end}.png
    tracking_{match_id}_frames_{start}_{end}.mp4
"""

import json
from collections import deque
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle


# ============================================================
# 定数定義
# ============================================================
# SkillCornerデータが置いてあるディレクトリ
DATA_DIR = Path("/mnt/datapool00/laliga_23/skillcorner_v2")

# 課題で指定された試合ID
MATCH_ID = 1018887

# 課題で指定された対象選手のID
TARGET_PLAYER_ID = 246
# 描画用の色設定
COLOR_PITCH_BG = "#2d6a4f"      # ピッチの背景（緑）
COLOR_PITCH_LINE = "white"       # ピッチの白線
COLOR_HOME = "#1976d2"           # ホームチーム（青）
COLOR_AWAY = "#d32f2f"           # アウェイチーム（赤）
COLOR_BALL = "black"             # ボール
COLOR_TARGET = "yellow"          # 対象選手のハイライト

# ボールの trackable_object（match_data['ball']['trackable_object'] から取れるが固定値として持っておく）
# 後で動的に取るように書き換えてもOK

# ============================================================
# データ読み込み関数
# ============================================================
def load_match_data(match_id: int) -> dict:
    """
    試合のメタデータ（選手情報、ピッチサイズなど）を読み込む

    Args:
        match_id: 試合ID

    Returns:
        試合メタデータの辞書
    """
    match_path = DATA_DIR / "match" / f"{match_id}.json"
    with open(match_path) as f:
        return json.load(f)


def load_tracking_data(match_id: int) -> list:
    """
    トラッキングデータ（フレームごとの選手・ボール位置）を読み込む

    Args:
        match_id: 試合ID

    Returns:
        フレームごとの辞書のリスト
    """
    tracking_path = DATA_DIR / "tracking" / f"{match_id}.json"
    with open(tracking_path) as f:
        return json.load(f)


def find_player_by_id(match_data: dict, player_id: int) -> dict:
    """
    選手IDから選手情報を取得する

    Args:
        match_data: 試合メタデータ
        player_id: 探したい選手のID

    Returns:
        選手情報の辞書（見つからない場合はNone）
    """
    # match_data["players"] は選手のリスト
    # その中から id == player_id を満たすものを探す
    for player in match_data["players"]:
        if player["id"] == player_id:
            return player
    return None

def draw_fukuari_stadium(ax, pitch_length: float, pitch_width: float):
    """
    フクダ電子アリーナ風のスタジアムを描画する

    特徴:
    - 球技専用（陸上トラックなし）、ピッチとスタンドが近い
    - 角丸の屋根（座席の90%をカバー）
    - 灰色の客席に、黄色いジェフサポーターが点在
    - 屋根にJEFロゴ
    - アウェー側ゴール裏に大型ビジョン
    - 芝の縦縞（実際のスタジアム風）

    Args:
        ax: matplotlib Axes
        pitch_length: ピッチ縦の長さ (m)
        pitch_width: ピッチ横幅 (m)
    """


    half_length = pitch_length / 2
    half_width = pitch_width / 2

    # ===== レイヤー1: 屋根（角丸の四角） =====
    roof = FancyBboxPatch(
        (-half_length - 20, -half_width - 16),     # 左下の座標
        pitch_length + 40,                          # 幅
        pitch_width + 32,                           # 高さ
        boxstyle="round,pad=0,rounding_size=8",     # 角丸の半径=8
        facecolor="#d0d0d0",                        # 明るいグレー
        edgecolor="none",
        zorder=1,
    )
    ax.add_patch(roof)

    # ===== レイヤー2: 客席エリア（灰色） =====
    seat_base = Rectangle(
        (-half_length - 14, -half_width - 10),
        pitch_length + 28,
        pitch_width + 20,
        facecolor="#707070",                        # 落ち着いた濃いグレー
        edgecolor="none",
        zorder=2,
    )
    ax.add_patch(seat_base)

    # ===== レイヤー3: 観客（黄色いジェフサポーター） =====
    np.random.seed(42)
    n_dots = 1500  # 観客の数
    yellow_color = "#fdd835"  # ジェフカラー黄色

    # 上下のスタンド
    for y_range in [(-half_width - 10, -half_width - 0.5),
                    (half_width + 0.5, half_width + 10)]:
        xs = np.random.uniform(-half_length - 14, half_length + 14, n_dots // 2)
        ys = np.random.uniform(y_range[0], y_range[1], n_dots // 2)
        ax.scatter(xs, ys, s=2, c=yellow_color, alpha=0.85, zorder=4)

    # 左右のゴール裏
    for x_range in [(-half_length - 14, -half_length - 0.5),
                    (half_length + 0.5, half_length + 14)]:
        xs = np.random.uniform(x_range[0], x_range[1], n_dots // 2)
        ys = np.random.uniform(-half_width - 10, half_width + 10, n_dots // 2)
        ax.scatter(xs, ys, s=2, c=yellow_color, alpha=0.85, zorder=4)

    # ===== レイヤー4: 屋根のJEFロゴ =====
    # 屋根の上部中央あたりに大きく配置
    ax.text(
        0, half_width + 13,
        "JEF",
        color="#1b5e20",                            # ジェフのもう一つの色「緑」
        fontsize=22,
        ha="center", va="center",
        weight="bold",
        zorder=6,
        family="sans-serif",
    )
    # 装飾の星マーク（左右）
    ax.text(-12, half_width + 13, "★", color="#fdd835",
            fontsize=18, ha="center", va="center", zorder=6)
    ax.text(12, half_width + 13, "★", color="#fdd835",
            fontsize=18, ha="center", va="center", zorder=6)


    # ===== レイヤー5: ピッチの芝（縦縞） =====
    n_stripes = 10
    stripe_width = pitch_length / n_stripes
    for i in range(n_stripes):
        color = "#2e7d32" if i % 2 == 0 else "#388e3c"
        stripe = Rectangle(
            (-half_length + i * stripe_width, -half_width),
            stripe_width,
            pitch_width,
            facecolor=color,
            edgecolor="none",
            zorder=7,
        )
        ax.add_patch(stripe)

    # ===== レイヤー7: ピッチライン =====
    line_color = "white"
    line_width = 1.8
    line_z = 8

    # 外枠
    ax.plot(
        [-half_length, half_length, half_length, -half_length, -half_length],
        [-half_width, -half_width, half_width, half_width, -half_width],
        color=line_color, linewidth=line_width, zorder=line_z,
    )
    # センターライン
    ax.plot([0, 0], [-half_width, half_width],
            color=line_color, linewidth=line_width, zorder=line_z)
    # センターサークル
    ax.add_patch(Circle((0, 0), 9.15,
                        color=line_color, fill=False,
                        linewidth=line_width, zorder=line_z))
    ax.plot(0, 0, marker="o", color=line_color, markersize=4, zorder=line_z)

    # ペナルティエリア・ゴールエリア・ゴール
    for side in [-1, 1]:
        ax.add_patch(Rectangle(
            (side * half_length - side * 16.5, -20.16),
            side * 16.5, 40.32, fill=False,
            color=line_color, linewidth=line_width, zorder=line_z,
        ))
        ax.add_patch(Rectangle(
            (side * half_length - side * 5.5, -9.16),
            side * 5.5, 18.32, fill=False,
            color=line_color, linewidth=line_width, zorder=line_z,
        ))
        ax.plot(side * (half_length - 11), 0, marker="o",
                color=line_color, markersize=3, zorder=line_z)
        # ゴール枠
        ax.add_patch(Rectangle(
            (side * half_length, -3.66),
            side * 1.5, 7.32,
            facecolor="white", edgecolor="black",
            linewidth=1, zorder=line_z + 1,
        ))

    # コーナーフラッグ
    for x_side in [-1, 1]:
        for y_side in [-1, 1]:
            ax.plot(
                x_side * half_length, y_side * half_width,
                marker="^", color="#fdd835",
                markersize=7, markeredgecolor="black",
                markeredgewidth=0.4, zorder=line_z + 1,
            )

    # ===== 軸設定 =====
    ax.set_xlim(-half_length - 22, half_length + 22)
    ax.set_ylim(-half_width - 18, half_width + 18)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    # スタジアム名（下部）
    ax.text(
        0, -half_width - 14,
        "FUKUDA DENSHI ARENA  /  Capacity: 19,781",
        color="white",
        fontsize=9,
        weight="bold",
        ha="center",
        zorder=20,
    )

def draw_frame(ax, frame_data: dict, match_data: dict, target_trackable_object: int):
    """
    1フレーム分の選手とボールの位置をピッチ上に描画する

    Args:
        ax: matplotlibのAxes（draw_pitchで描いた上に重ねる）
        frame_data: 1フレーム分のトラッキングデータ
        match_data: 試合メタデータ（選手のチーム情報を引くために使う)
        target_trackable_object: ハイライトする選手のtrackable_object
    """
    # trackable_object -> 所属チームID の対応表を作る
    # （毎フレーム作るのは効率悪いので、後で外に出してもOK）
    home_team_id = match_data["home_team"]["id"]
    away_team_id = match_data["away_team"]["id"]
    ball_trackable_object = match_data["ball"]["trackable_object"]

    # 全選手のtrackable_object -> team_idの辞書を作る
    trackable_to_team = {}
    for player in match_data["players"]:
        trackable_to_team[player["trackable_object"]] = player["team_id"]

    # フレーム内の各オブジェクト（選手/ボール）を描画
    for obj in frame_data["data"]:
        x = obj["x"]
        y = obj["y"]
        trackable_object = obj["trackable_object"]

        # ボールかどうか判定
        if trackable_object == ball_trackable_object:
            # 選手やピッチライン(zorder=8-11)より前面に出すためzorder=12
            ax.scatter(x, y, color=COLOR_BALL, s=60, zorder=12)  
            continue

        # 選手の場合、所属チームで色を変える
        team_id = trackable_to_team.get(trackable_object)
        if team_id == home_team_id:
            color = COLOR_HOME
        elif team_id == away_team_id:
            color = COLOR_AWAY
        else:
            # 審判など、選手リストにない人物
            color = "gray"

        # 対象選手は黄色で大きめに描画
        if trackable_object == target_trackable_object:
            ax.scatter(x, y, color=color, edgecolor=COLOR_TARGET,
                       linewidth=2, s=200, zorder=11)  
        else:
            ax.scatter(x, y, color=color, s=100, zorder=10)  

# ============================================================
# 速度・加速度の計算
# ============================================================
def extract_player_positions(tracking_data: list, trackable_object: int,
                             frame_start: int, frame_end: int):
    """
    指定選手の(x, y)座標を、フレーム範囲内で抽出する

    SkillCornerのデータは、フレームによってその選手のデータが入って
    いないこともある(画面外などで)。
    その場合は np.nan を入れて、後で補間できるようにする。

    Args:
        tracking_data: トラッキングデータ全体
        trackable_object: 対象選手のtrackable_object
        frame_start: 開始フレーム
        frame_end: 終了フレーム（含む）

    Returns:
        xs, ys: 長さ (frame_end - frame_start + 1) の numpy 配列
    """
    n_frames = frame_end - frame_start + 1
    xs = np.full(n_frames, np.nan)  # 初期値はNaN
    ys = np.full(n_frames, np.nan)

    for i, frame_index in enumerate(range(frame_start, frame_end + 1)):
        frame = tracking_data[frame_index]
        # このフレームの選手データから、対象選手を探す
        for obj in frame["data"]:
            if obj["trackable_object"] == trackable_object:
                xs[i] = obj["x"]
                ys[i] = obj["y"]
                break  # 見つかったらこのフレームは終わり

    return xs, ys


def calculate_speed(xs: np.ndarray, ys: np.ndarray, dt: float = 0.1) -> np.ndarray:
    """
    位置の時系列から速度を計算する

    速度(t) = sqrt((x(t)-x(t-1))² + (y(t)-y(t-1))²) / dt

    Args:
        xs, ys: 位置座標の時系列 (numpy配列)
        dt: フレーム間の時間 (秒)。SkillCornerは10fpsなので0.1秒

    Returns:
        speeds: 速度の時系列（最初の要素は0、長さはxsと同じ）
    """
    # np.diff は隣接要素の差分を取る。長さが1減るのでprependで先頭を補う
    dx = np.diff(xs, prepend=xs[0])
    dy = np.diff(ys, prepend=ys[0])
    distances = np.sqrt(dx ** 2 + dy ** 2)
    speeds = distances / dt
    return speeds


def calculate_acceleration(speeds: np.ndarray, dt: float = 0.1) -> np.ndarray:
    """
    速度の時系列から加速度を計算する

    加速度(t) = (速度(t) - 速度(t-1)) / dt

    Args:
        speeds: 速度の時系列
        dt: フレーム間の時間 (秒)

    Returns:
        accelerations: 加速度の時系列（最初の要素は0、長さはspeedsと同じ）
    """
    accelerations = np.diff(speeds, prepend=speeds[0]) / dt
    return accelerations


def plot_speed_acceleration(speeds: np.ndarray, accelerations: np.ndarray,
                             frame_start: int, frame_end: int,
                             player_name: str, player_id: int,
                             trackable_object: int,
                             dt: float = 0.1,
                             save_path: str = "speed_acceleration.png"):
    """
    速度と加速度の折れ線グラフを2段で描画する

    Args:
        speeds: 速度の時系列
        accelerations: 加速度の時系列
        frame_start: 開始フレーム（タイトル表示用）
        frame_end: 終了フレーム
        player_name: 選手名（タイトル用）
        player_id: 選手ID（タイトル用）
        trackable_object: トラッキングオブジェクトID（タイトル用）
        dt: フレーム間時間
        save_path: 保存先ファイル名
    """
    # 時間軸（秒）を作る。frame_startを0秒とする
    time_axis = np.arange(len(speeds)) * dt

    # 2段のグラフを作る (sharex=Trueでx軸を共有)
    fig, (ax_speed, ax_accel) = plt.subplots(
        2, 1, figsize=(10, 6), sharex=True
    )

    # ===== 上段: 速度 =====
    ax_speed.plot(time_axis, speeds, color="#1976d2", linewidth=1.2)
    ax_speed.set_ylabel("Speed [m/s]", color="#1976d2")
    ax_speed.tick_params(axis="y", labelcolor="#1976d2")
    ax_speed.grid(True, alpha=0.3)

    # ===== 下段: 加速度 =====
    ax_accel.plot(time_axis, accelerations, color="#d32f2f", linewidth=1.0)
    ax_accel.set_ylabel("Acceleration [m/s²]", color="#d32f2f")
    ax_accel.set_xlabel("Time [s]")
    ax_accel.tick_params(axis="y", labelcolor="#d32f2f")
    ax_accel.grid(True, alpha=0.3)

    # 全体タイトル
    fig.suptitle(
        f"{player_name} (player_id={player_id}, trackable_object={trackable_object})\n"
        f"Frames {frame_start}-{frame_end}"
    )

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"{save_path} を保存しました")
    plt.close()

# ============================================================
# アニメーション関連
# ============================================================
def create_tracking_animation(
    tracking_data: list,
    match_data: dict,
    target_player: dict,
    frame_start: int,
    frame_end: int,
    ball_trail_length: int = 5,
    fps: int = 10,
    save_path: str = "tracking_animation.mp4",
):
    """
    トラッキングデータをアニメーション動画として作成する
    フクアリ仕様のスタジアム背景に、選手・ボール・ボールの軌跡を描画する

    Args:
        tracking_data: トラッキングデータ全体
        match_data: 試合メタデータ
        target_player: 対象選手の情報
        frame_start: 開始フレーム
        frame_end: 終了フレーム
        ball_trail_length: ボール軌跡を残すフレーム数（応用課題: 5）
        fps: 動画のフレームレート
        save_path: 保存先ファイル名
    """
    # ----- 事前計算: trackable_object -> team_id の対応表 -----
    home_team_id = match_data["home_team"]["id"]
    away_team_id = match_data["away_team"]["id"]
    ball_trackable_object = match_data["ball"]["trackable_object"]
    target_trackable_object = target_player["trackable_object"]

    trackable_to_team = {}
    for player in match_data["players"]:
        trackable_to_team[player["trackable_object"]] = player["team_id"]

    # ----- 図のセットアップ -----
    fig, ax = plt.subplots(figsize=(12, 8))
    draw_fukuari_stadium(ax, match_data["pitch_length"], match_data["pitch_width"])

    # ----- 動的に動く要素を初期化 -----
    # 選手・ボールのscatterオブジェクト（あとでset_offsetsで位置更新する）
    home_scatter = ax.scatter([], [], color=COLOR_HOME, s=100, zorder=10)
    away_scatter = ax.scatter([], [], color=COLOR_AWAY, s=100, zorder=10)
    other_scatter = ax.scatter([], [], color="gray", s=80, zorder=10)
    target_scatter = ax.scatter(
        [], [], color=COLOR_HOME, edgecolor=COLOR_TARGET,
        linewidth=2, s=200, zorder=11,
    )
    ball_scatter = ax.scatter([], [], color=COLOR_BALL, s=60, zorder=13)

    # ボール軌跡用のscatter（過去5フレーム分、薄い色で表示）
    trail_scatter = ax.scatter([], [], s=40, zorder=12)

    # フレーム情報を表示するテキスト
    info_text = ax.text(
        0, -match_data["pitch_width"] / 2 - 15,
        "", color="white", fontsize=11,
        ha="center", weight="bold", zorder=20,
    )

    # ボール軌跡を保持するdeque（先入れ先出しキュー、上限5）
    ball_trail = deque(maxlen=ball_trail_length)

    # ----- 1フレームを描画する関数（FuncAnimationが呼ぶ） -----
    def update(frame_index: int):
        # 対象チームの色を判定（対象選手の所属チーム）
        target_team_id = trackable_to_team.get(target_trackable_object)

        # 各カテゴリの座標を入れる入れ物
        home_positions = []
        away_positions = []
        other_positions = []
        target_position = []
        ball_position = []

        frame = tracking_data[frame_index]

        for obj in frame["data"]:
            x = obj["x"]
            y = obj["y"]
            trackable_object = obj["trackable_object"]

            # ボール
            if trackable_object == ball_trackable_object:
                ball_position.append([x, y])
                ball_trail.append([x, y])  # 軌跡に追加
                continue

            # 対象選手
            if trackable_object == target_trackable_object:
                target_position.append([x, y])
                continue

            # その他の選手
            team_id = trackable_to_team.get(trackable_object)
            if team_id == home_team_id:
                home_positions.append([x, y])
            elif team_id == away_team_id:
                away_positions.append([x, y])
            else:
                other_positions.append([x, y])

        # scatterの位置を更新（set_offsetsは(N, 2)の配列を受け取る）
        # 空のリストだと形状エラーになるので np.empty((0, 2)) を使う
        def _to_array(lst):
            return np.array(lst) if lst else np.empty((0, 2))

        home_scatter.set_offsets(_to_array(home_positions))
        away_scatter.set_offsets(_to_array(away_positions))
        other_scatter.set_offsets(_to_array(other_positions))
        target_scatter.set_offsets(_to_array(target_position))
        ball_scatter.set_offsets(_to_array(ball_position))

        # 対象選手の色を所属チームに合わせて更新
        if target_team_id == home_team_id:
            target_scatter.set_facecolor(COLOR_HOME)
        elif target_team_id == away_team_id:
            target_scatter.set_facecolor(COLOR_AWAY)

        # ----- ボール軌跡（過去5フレーム）の描画 -----
        # 古いものほど薄く、小さくする
        if len(ball_trail) > 0:
            trail_array = np.array(list(ball_trail))
            # alpha値を計算: 古い=0.1, 新しい=0.8 のように線形変化
            n_trail = len(trail_array)
            alphas = np.linspace(0.15, 0.7, n_trail)
            sizes = np.linspace(20, 50, n_trail)
            trail_scatter.set_offsets(trail_array)
            trail_scatter.set_sizes(sizes)
            # 色を白(ボール色をうっすら)に
            colors = np.array([[1, 1, 1, a] for a in alphas])  # RGBA
            trail_scatter.set_color(colors)

        # フレーム情報のテキスト更新
        info_text.set_text(
            f"Frame {frame_index}  |  {match_data['home_team']['name']} vs {match_data['away_team']['name']}"
        )

        # 返り値（blit=Trueを使う場合に必要だが、ここでは使わないので形式的に返す）
        return (home_scatter, away_scatter, other_scatter,
                target_scatter, ball_scatter, trail_scatter, info_text)

    # ----- アニメーション作成 -----
    print(f"アニメーション作成中... ({frame_end - frame_start + 1} フレーム)")
    anim = FuncAnimation(
        fig,
        update,
        frames=range(frame_start, frame_end + 1),
        interval=1000 / fps,  # ミリ秒
        blit=False,
    )

    # ----- 動画として保存 -----
    print(f"{save_path} を保存中... (時間がかかります)")
    writer = FFMpegWriter(fps=fps, bitrate=2000)
    anim.save(save_path, writer=writer)
    print(f"{save_path} を保存しました")
    plt.close()

# ============================================================
# メイン処理
# ============================================================
def main():
    # 試合メタデータを読み込む
    match_data = load_match_data(MATCH_ID)
    print(f"試合ID: {MATCH_ID}")
    print(f"ホーム: {match_data['home_team']['name']}")
    print(f"アウェイ: {match_data['away_team']['name']}")
    print(f"ピッチサイズ: {match_data['pitch_length']}m x {match_data['pitch_width']}m")
    print()

    # 対象選手の情報を取得
    target_player = find_player_by_id(match_data, TARGET_PLAYER_ID)
    if target_player is None:
        print(f"player_id={TARGET_PLAYER_ID} の選手が見つかりません")
        return

    # 選手情報を表示
    print(f"対象選手: {target_player['first_name']} {target_player['last_name']}")
    print(f"  player_id: {target_player['id']}")
    print(f"  trackable_object: {target_player['trackable_object']}")
    print(f"  背番号: {target_player['number']}")
    print(f"  team_id: {target_player['team_id']}")
    print()

    # トラッキングデータを読み込む
    tracking_data = load_tracking_data(MATCH_ID)
    print(f"総フレーム数: {len(tracking_data)}")

    # ----- まずは100フレーム目を可視化してみる -----
    test_frame_index = 100
    test_frame = tracking_data[test_frame_index]

    # 図のセットアップ
    fig, ax = plt.subplots(figsize=(12, 8))

    # フクアリ仕様のスタジアムを描画
    draw_fukuari_stadium(ax, match_data["pitch_length"], match_data["pitch_width"])

    # 選手とボールを描画
    draw_frame(ax, test_frame, match_data, target_player["trackable_object"])

    # タイトル
    ax.set_title(f"Frame {test_frame_index}: {match_data['home_team']['name']} vs {match_data['away_team']['name']}")

    # 保存
    plt.savefig("test_frame_fukuari.png", dpi=150, bbox_inches="tight")
    print(f"test_frame_fukuari.png を保存しました")
    plt.close()

    # ============================================================
    # 課題3: 速度・加速度の折れ線グラフを作成
    # ============================================================
    print("\n--- 速度・加速度グラフ作成 ---")

    # フレーム範囲（課題指定: 10〜500）
    FRAME_START = 10
    FRAME_END = 500

    # 対象選手の位置を抽出
    target_trackable = target_player["trackable_object"]
    xs, ys = extract_player_positions(
        tracking_data, target_trackable, FRAME_START, FRAME_END
    )

    # NaN（位置データなし）がいくつあるか確認
    nan_count = np.isnan(xs).sum()
    print(f"位置データなし(NaN)のフレーム数: {nan_count} / {len(xs)}")

    # 速度・加速度を計算
    speeds = calculate_speed(xs, ys)
    accelerations = calculate_acceleration(speeds)

    # グラフ作成
    player_full_name = f"{target_player['first_name']} {target_player['last_name']}"
    plot_speed_acceleration(
        speeds, accelerations,
        FRAME_START, FRAME_END,
        player_full_name,
        target_player["id"],
        target_player["trackable_object"],
        save_path=f"player_{target_player['id']}_speed_acceleration_{FRAME_START}_{FRAME_END}.png",
    )

    # ============================================================
    # 課題2（フル版）+ 応用課題: トラッキングアニメーション + ボール軌跡
    # ============================================================
    print("\n--- トラッキングアニメーション作成 ---")

    # 最初の100フレーム分（10秒）を動画にする
    # 全フレームだと60,739フレーム=約100分かかるので限定
    ANIM_FRAME_START = 0
    ANIM_FRAME_END = 100

    create_tracking_animation(
        tracking_data,
        match_data,
        target_player,
        ANIM_FRAME_START,
        ANIM_FRAME_END,
        ball_trail_length=5,
        fps=10,
        save_path=f"tracking_{MATCH_ID}_frames_{ANIM_FRAME_START}_{ANIM_FRAME_END}.mp4",
    )


if __name__ == "__main__":
    main()