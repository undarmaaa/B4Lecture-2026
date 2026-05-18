# Exercise 3: TrackID3x3 を用いた簡単なアブレーションスタディ

## 目的

本課題では，`B4Lecture-2026/ex3/5.2.3_Track-ID-3x3.ipynb` を用いて，
人物検出器と追跡器の組み合わせを変更し，トラッキング性能がどのように変化するかを確認します。

特に，以下の3つの評価指標を比較します。

- TI-HOTA
- TI-DetA
- TI-AssA

最終的に，複数の検出器・追跡器の組み合わせを試し，結果を表にまとめてください。

---

## 実験内容

ノートブック内の以下のセルを変更して，検出器と追跡器の組み合わせを変えて実験してください。

```python
model = YOLO("yolo11x.pt")

results = model.track(
    source=video_path,
    tracker="bytetrack.yaml",
    device="0",
    classes=[0],
    save=True,
    save_txt=True,
    save_conf=True,
    verbose=False
)
```

---

## 変更する箇所

### 1. 検出器

以下のように，YOLOモデルを変更して実験してください。

```python
model = YOLO("yolo11n.pt")  # Nano
model = YOLO("yolo11s.pt")  # Small
model = YOLO("yolo11m.pt")  # Medium
model = YOLO("yolo11l.pt")  # Large
model = YOLO("yolo11x.pt")  # Extra-Large
```

すべてを試す必要はありませんが，少なくとも2種類以上の検出器を比較してください。

### 2. 追跡器

以下のように，`tracker` を変更して実験してください。

```python
tracker="bytetrack.yaml"
tracker="botsort.yaml"
```

環境に設定ファイルがある場合は，その他の追跡器を試しても構いません。

---

## 最低実験数

少なくとも以下の4条件を比較してください。

| Detector | Tracker |
|---|---|
| YOLO11n | ByteTrack |
| YOLO11n | BoT-SORT |
| YOLO11x | ByteTrack |
| YOLO11x | BoT-SORT |

計算時間に余裕がある場合は，YOLO11s，YOLO11m，YOLO11l も追加してください。

---

## 実験条件

公平に比較するため，以下の条件は固定してください。

- 使用する動画
- 評価対象のフレーム範囲
- `classes=[0]`
- confidence threshold や IoU threshold を変更する場合は，全条件で同じ値にする
- 評価スクリプト
- 評価指標

基本的には，検出器と追跡器以外の設定を変更しなければ大丈夫です。

---

## 評価指標

本課題では，以下の3つの指標を用いて結果を比較します。

- **TI-HOTA**: 検出性能と対応付け性能を総合的に評価する指標
- **TI-DetA**: 主に検出性能を評価する指標
- **TI-AssA**: 主に対応付けやID維持の性能を評価する指標

3つとも値が高いほど良い結果であることを表します。
TI-DetA が低い場合は，人物検出がうまくできていない可能性があります。  
TI-AssA が低い場合は，同じ人物のIDを維持することが難しかった可能性があります。

---

## 結果のまとめ方

各組み合わせについて，TI-HOTA，TI-DetA，TI-AssA を表にまとめてください。
ただし，TI-HOTA，TI-DetA，TI-AssA の表示スケールは表の中で統一してください。
各指標で最も良い値を **太字** にしてください。

例:

| Detector | Tracker | TI-HOTA↑ | TI-DetA↑ | TI-AssA↑ |
|---|---|---:|---:|---:|
| YOLO11n | ByteTrack | 0.XXX | 0.XXX | 0.XXX |
| YOLO11n | BoT-SORT | 0.XXX | 0.XXX | 0.XXX |
| YOLO11x | ByteTrack | **0.XXX** | 0.XXX | **0.XXX** |
| YOLO11x | BoT-SORT | 0.XXX | **0.XXX** | 0.XXX |

値はパーセント表示でも構いません。

例:

| Detector | Tracker | TI-HOTA (%) ↑ | TI-DetA (%) ↑ | TI-AssA (%) ↑ |
|---|---|---:|---:|---:|
| YOLO11n | ByteTrack | 52.3 | 61.0 | 45.2 |
| YOLO11x | BoT-SORT | **58.7** | **64.8** | **53.1** |

時間があれば https://texclip.marutank.net/ で作成して画像にしてみましょう（生成AIに手伝ってもらうと良いと思います）。

---

## 考察

表を作成したうえで，以下の点について簡単に考察してください。

1. どの検出器・追跡器の組み合わせが最も良かったか
2. 検出器を大きく・小さくすると性能は改善・悪化したか
3. 追跡器を変更するといずれかの指標に変化はあったか
4. 検出性能とID維持性能のどちらが課題になっていそうか

考察は長くなくて構いません。数行程度でまとめてください。評価指標の値だけでなく、可視化結果も使って考察するのも良いでしょう。

---

## 提出物

以下を提出してください。

1. 結果をまとめた表
2. 簡単な考察
3. ミニマップ付き動画（TI-HOTAが一番悪かったものと一番良かったもの）

---

## 注意点

- Colabでの実行を推奨。ランタイムをGPUに設定すること。
