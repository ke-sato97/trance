# Local Transcriber

Docker上で `faster-whisper` を実行し、ローカル音声ファイルを日本語で文字起こしするCLIツールです。

OpenAI APIや外部の文字起こしAPIには音声を送信しません。音声ファイル、文字起こし結果、Whisperモデルは各PCのローカルディレクトリに保存します。

## 必要環境

- macOS
- Docker Desktop
- Docker Compose
- 初回モデル取得時のインターネット接続

PythonをホストPCへ直接インストールする必要はありません。

## 初回準備

```bash
docker compose build
```

## 使い方

音声ファイルを `inputs/` に配置します。

```text
inputs/meeting.mp3
```

文字起こしを実行します。

```bash
docker compose run --rm transcriber "meeting.mp3"
```

出力ファイルは `outputs/` に保存されます。

```text
outputs/meeting.txt
```

出力はタイムスタンプなし、話者分離なしの本文のみです。発話の区切りは空行で分けます。

```text
それでは本日の会議を始めます。よろしくお願いします。

よろしくお願いします。まず先週の進捗から共有します。

ありがとうございます。では画面の内容について確認していきます。
```

## オプション

モデルを指定できます。

```bash
docker compose run --rm transcriber "meeting.mp3" --model medium
```

固有名詞や人名の認識を補助するプロンプトを指定できます。

```bash
docker compose run --rm transcriber "meeting.mp3" \
  --prompt "これは複数人による日本語の会議です。"
```

## 対応形式

- `.mp3`
- `.wav`
- `.m4a`
- `.flac`

拡張子の大文字・小文字は区別しません。

## デバッグ

コンテナ内のbashに入る場合は、エントリーポイントを上書きします。

```bash
docker compose run --rm --entrypoint bash transcriber
```

コンテナ内では次のように実行できます。

```bash
python /app/transcribe.py "meeting.mp3"
```

## Git管理について

Gitで管理するのは、アプリケーションコード、Docker設定、README、空ディレクトリ維持用の `.gitkeep` です。

以下は `.gitignore` で除外します。

- `inputs/` 内の音声ファイル
- `outputs/` 内の文字起こし結果
- `models/` 内のWhisperモデルキャッシュ

別PCで使う場合は、リポジトリをcloneして `docker compose build` を実行してください。モデルはそのPCでの初回実行時に `models/` へダウンロードされ、2回目以降はキャッシュが使われます。

## 注意事項

- 初回実行時はモデルダウンロードが発生します。
- CPU実行のため、長時間音声は処理に時間がかかります。
- 同名の出力ファイルがある場合は上書きします。
- 入力音声は変更、削除、リネームしません。
- 初期版では話者分離を行いません。
- 文字起こし精度は音質、話し方、ノイズ、専門用語に影響されます。
