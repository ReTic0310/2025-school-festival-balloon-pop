# HEART BALLOON POP 🎈🔫

USBカメラとハンドジェスチャーで遊ぶ、8ビットレトロスタイルのバルーンシューティングゲーム！

## 概要

MediaPipe Handsを使用したリアルタイムの銃ジェスチャー認識により、手で銃のポーズを作って風船を撃ち落とすゲームです。30秒間でできるだけ多くの風船を割って、ハイスコアを目指しましょう！

## 特徴

- 🎮 **ハンドジェスチャー認識**: 銃のポーズで照準を合わせて発射
- 🎯 **照準システム**: 銃を横に向けると照準が表示される
- 📷 **USBカメラ自動検出**: シリアル番号による自動デバイス認識（ポート変更に対応）
- 🎨 **8ビットレトロ風**: 320x180の仮想解像度を1920x1080にスケール
- ⏱️ **タイムチケット報酬システム**: スコアに応じて報酬を獲得
- 📸 **リザルト保存機能**: ゲーム結果のスクリーンショット保存
- 📹 **リアルタイムカメラプレビュー**: 画面右上にカメラ映像を表示

## システム要件

- Python 3.11 (MediaPipe互換性のため)
- USBカメラ (UVC対応推奨)
- Raspberry Pi または Linux システム
- ディスプレイ: 1920x1080 (フルスクリーン)

## インストール

### 1. 依存ライブラリのインストール

```bash
# pyenvがインストールされていない場合
curl https://pyenv.run | bash

# Python 3.11のビルドに必要なパッケージ
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev curl \
  libncursesw5-dev xz-utils tk-dev libxml2-dev \
  libxmlsec1-dev libffi-dev liblzma-dev

# カメラ情報取得のためのツール
sudo apt-get install -y v4l-utils
```

### 2. Python 3.11のインストール

```bash
pyenv install 3.11.14
```

### 3. 仮想環境の作成

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 4. Pythonパッケージのインストール

```bash
./venv/bin/pip install --upgrade pip
./venv/bin/pip install pygame opencv-python numpy mediapipe
```

## 使い方

### ゲームの起動

```bash
./main.py
```

または

```bash
./venv/bin/python3 main.py
```

### 操作方法

#### ゲーム開始前 (READYステート)
- **SPACE**: ゲーム開始

#### ゲーム中 (RUNステート)
- **銃ジェスチャー**:
  1. **照準モード**: 人差し指を伸ばして他の指を曲げ、手を横に向ける
     - 照準（黄色の円）が表示される
  2. **発射モード**: 照準を合わせたら、手を90度上に向ける
     - 照準位置で風船を撃ち抜く！
- **M**: マニュアル発射 (テスト用)
- **ESC / Q**: ゲーム終了

#### リザルト画面 (RESULTステート)
- **R**: リスタート
- **S**: スクリーンショット保存
- **Q**: 終了

### タイムチケット報酬

| 撃ち落とした風船数 | 獲得時間 |
|------------------|---------|
| 50個以上          | 120分   |
| 40〜49個          | 90分    |
| 30〜39個          | 60分    |
| 20〜29個          | 30分    |
| 10〜19個          | 15分    |
| 9個以下           | 0分     |

## プロジェクト構造

```
heart_balloon_pop/
├── main.py                 # メインエントリーポイント
├── camera_config.json      # カメラ設定ファイル
├── src/
│   ├── camera_manager.py   # カメラ管理モジュール
│   ├── heart_detector.py   # 銃ジェスチャー検出
│   └── game.py            # ゲームコアロジック
├── assets/                 # アセットディレクトリ (将来の拡張用)
├── results/               # リザルト画像保存先
└── venv/                  # Python仮想環境
```

## カメラ設定

初回起動時、USBカメラの情報が自動的に `camera_config.json` に記録されます。

```json
{
  "registered_cameras": [
    {
      "model": "C505 HD Webcam",
      "serial": "962EAD20",
      "preferred_resolution": [1280, 720],
      "preferred_fps": 30,
      "last_seen_device": "/dev/video0"
    }
  ]
}
```

次回以降は、カメラがどのポート（/dev/video0、/dev/video1など）に接続されていても、シリアル番号で自動的に認識されます。

## トラブルシューティング

### カメラが認識されない

```bash
# カメラデバイスの確認
v4l2-ctl --list-devices

# カメラの詳細情報
v4l2-ctl -d /dev/video0 --all
```

### Pygameの画面が表示されない

Raspberry Piの場合、X11またはWaylandディスプレイサーバーが実行されていることを確認してください。

```bash
echo $DISPLAY
# 出力例: :0 または :1
```

### MediaPipeのインポートエラー

Python 3.11を使用していることを確認してください：

```bash
./venv/bin/python3 --version
# Python 3.11.14 であることを確認
```

## 開発者情報

### コーディング規約

- ログとコードコメントは英語
- 中間メッセージやドキュメントは日本語
- importは常にトップレベルに配置
- シンプルで読みやすいコードを心がける

## ライセンス

このプロジェクトは教育・研究目的で作成されています。

## 謝辞

- **Pygame**: ゲームエンジン
- **MediaPipe**: ハンドトラッキング
- **OpenCV**: カメラ入力
