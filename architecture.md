# ポモドーロタイマーWebアプリ アーキテクチャ案

## 1. 概要

本アプリはFlask（Python）をバックエンド、HTML/CSS/JavaScriptをフロントエンドとしたシンプルなポモドーロタイマーWebアプリです。UIは添付のモック画像を参考に設計します。

---

## 2. ディレクトリ構成例

```
/プロジェクトルート/
├── app.py                # Flaskアプリ本体
├── timer_logic.py        # タイマー関連ロジック（テスト容易性のため分離）
├── tests/                # ユニットテスト用ディレクトリ
│   ├── test_timer_logic.py
│   └── test_app.py
├── templates/
│   └── index.html        # メイン画面
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── timer.js
│   │   └── timerLogic.js # JSロジック分離
│   └── img/
│       └── pomodoro.png
└── README.md
```

---

## 3. バックエンド（Flask）

- `/` ルートで `index.html` を返す
- 必要に応じてAPIエンドポイント（例: `/api/start`, `/api/stop`, `/api/status`）を用意
- タイマーや設定値の計算・管理ロジックは `timer_logic.py` に分離し、Flask本体から独立させる
- ユニットテスト容易化のため、ロジック部分は純粋なPython関数として実装
- DBや外部サービス利用時は依存性注入を意識

---

## 4. フロントエンド（HTML/CSS/JavaScript）

- `index.html` でUIを構築（モック画像を再現）
- `timer.js` でタイマーのUI制御、`timerLogic.js` でタイマーの計算・状態管理ロジックを分離
- `style.css` でデザイン調整
- 必要に応じてローカルストレージで状態保存
- ロジック部分は関数やクラスとして実装し、Jest等でテスト可能な構造に

---

## 5. テスト方針

- Python: `pytest`や`unittest`で`timer_logic.py`やAPIのユニットテストを実施
- JavaScript: `Jest`や`Vitest`で`timerLogic.js`のロジック部分のテストを実施
- CI/CDで自動テスト実行を推奨

---

## 6. 拡張性・保守性への配慮

- ロジックとUI/フレームワーク部分を分離し、テスト容易性・保守性を高める
- 必要に応じてAPIやDB連携、ユーザーごとの履歴管理なども拡張可能な構成

---

以上のアーキテクチャで、シンプルかつテストしやすいポモドーロタイマーWebアプリを実装します。