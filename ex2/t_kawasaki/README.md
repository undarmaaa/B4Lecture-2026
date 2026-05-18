# ex2: Deep-EIoU トラッキング結果の分析

## 概要

SoccerTrack Challenge 2025 の動画 `117093.mp4` に対して [Deep-EIoU](https://github.com/hsiangwei0903/Deep-EIoU) で選手追跡を行い、その結果を可視化・分析した。

## 課題

1. **課題1**: Deep-EIoU の出力を用いて、選手の軌跡を可視化する
2. **課題2**: 速度または加速度を計算し、トラッキング結果の特徴や異常な動きを分析する

## ファイル構成

```
t_kawasaki/
├── README.md                ← このファイル
├── ex2_task.ipynb           ← 分析ノートブック（メイン成果物）
├── tracking_result.txt      ← Deep-EIoU の出力（MOTChallenge形式）
├── pyproject.toml           ← Python パッケージ管理
├── uv.lock
├── .python-version
└── .gitignore
```

`Deep-EIoU/` フォルダ（モデル本体、重みファイル、動画など）は容量が大きいためリポジトリには含めていない。再現したい場合は下記の手順を参照。

## 実行手順

### ノートブックを開いて結果を見るだけの場合

VSCode などで `ex2_task.ipynb` を開けば、既に実行済みの結果（グラフ、表）が見られる。

### コードを再実行する場合

```bash
# Python 3.8 環境を作成
uv venv --python 3.8

# 依存ライブラリインストール
uv sync

# ノートブックを開いて実行
# (VSCode で ex2_task.ipynb を開く)
```

トラッキング結果テキスト (`tracking_result.txt`) は既に同梱しているので、Deep-EIoU を実行しなくてもノートブックは動く。

### Deep-EIoU を最初から再現する場合

```bash
# 1. Deep-EIoU を clone
git clone https://github.com/hsiangwei0903/Deep-EIoU.git

# 2. モデル重みを Google Drive からダウンロード
cd Deep-EIoU/Deep-EIoU
uv run gdown --fuzzy 'https://drive.google.com/file/d/1834kh10-X0Tu743fgmN7jXPVDKgq4ZqR/view?usp=drive_link' --output checkpoints/best_ckpt.pth.tar
uv run gdown --fuzzy 'https://drive.google.com/file/d/14zzlm1nI9Ws_Il9RYNChwPC7Fsul7xwl/view?usp=drive_link' --output checkpoints/sports_model.pth.tar-60

# 3. 動画をダウンロード
uv run gdown --fuzzy 'https://drive.google.com/file/d/1bC1C5lOM-2AKX2Jmk-9Yk7klzYIh0uEF/view?usp=drive_link'

# 4. 先頭20秒を切り出し
ffmpeg -i 117093.mp4 -ss 00:00:00 -t 00:00:20 -c copy 117093_trimmed.mp4

# 5. Deep-EIoU のコード修正（np.float が新しい NumPy で使えないため）
grep -rln "np\.float[^0-9_]" --include="*.py" | xargs sed -i 's/np\.float\([^0-9_]\)/float\1/g'

# 6. torchreid を追加インストール
cd ../../  # t_kawasaki/ に戻る
uv add "torchreid @ git+https://github.com/KaiyangZhou/deep-person-reid.git" --no-build-isolation

# 7. Deep-EIoU 実行
cd Deep-EIoU/Deep-EIoU
uv run python tools/demo.py --path 117093_trimmed.mp4 --save_result True
```

## 実行環境

- OS: Ubuntu 24.04
- GPU: NVIDIA RTX A6000
- Python: 3.8.20
- PyTorch: 1.13.0+cu116
- CUDA: 11.6

## 主な発見

### 課題1: 選手軌跡の可視化

- 完全追跡された選手は約 15 人、ほぼ完全な追跡が約 6 人で、合計約 21 人の選手を安定して追跡できている
- ID スイッチが自動検出で **46件** 見つかった
- ID スイッチは特に **フレーム 270 付近に集中** している（最大8件）

### 課題2: 速度・加速度の分析

- 通常の検出は速度 5 px/frame 以下に収まっている
- しきい値 30 px/frame を超える異常値が **78件** 存在
- 異常値の多くは **画面端で部分的にしか映っていない物体の不安定な検出**が原因
- 速度の異常スパイクは IDスイッチや断続的な検出を別の角度から検出する手段になる

## 補足

- Deep-EIoU の出力する画像座標系（ピクセル単位）の速度であり、ピッチ上の実速度ではない
- カメラが動けば静止している選手も移動して見えるため、解釈には注意が必要
- 課題3（パラメータ変更による評価値比較）は時間の都合で実施していない