import argparse
import sys
from pathlib import Path

from faster_whisper import WhisperModel


INPUT_DIR = Path("/data/inputs")
OUTPUT_DIR = Path("/data/outputs")
SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac"}
SUPPORTED_MODELS = {"tiny", "base", "small", "medium"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe a local audio file with faster-whisper."
    )
    parser.add_argument(
        "filename",
        help="Audio filename under inputs/. Do not pass an absolute path.",
    )
    parser.add_argument(
        "--model",
        default="small",
        choices=sorted(SUPPORTED_MODELS),
        help="Whisper model size. Default: small.",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Optional Japanese prompt to improve recognition of names and terms.",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    print(f"エラー: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_input(filename: str) -> Path:
    if Path(filename).is_absolute() or "/" in filename or "\\" in filename:
        fail("inputs内のファイル名だけを指定してください。")

    input_path = INPUT_DIR / filename

    if not input_path.exists():
        fail(f"入力ファイルが見つかりません: {input_path}")
    if not input_path.is_file():
        fail(f"入力ファイルではありません: {input_path}")
    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        extensions = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        fail(f"対応していない拡張子です。対応形式: {extensions}")
    if input_path.stat().st_size == 0:
        fail(f"入力ファイルが空です: {input_path}")

    return input_path


def format_segments(segments) -> str:
    paragraphs: list[str] = []

    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue

        print(f"認識しました: {text[:60]}")
        paragraphs.append(text)

    return "\n\n".join(paragraphs).strip() + "\n"


def write_output(output_path: Path, content: str) -> None:
    if not OUTPUT_DIR.exists():
        fail(f"出力ディレクトリが存在しません: {OUTPUT_DIR}")

    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")

    try:
        if output_path.exists():
            print(f"同名の出力ファイルを上書きします: {output_path}")

        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(output_path)
    except OSError as exc:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        fail(f"出力ファイルの保存に失敗しました: {exc}")


def main() -> int:
    args = parse_args()

    print("入力ファイルを確認しています...")
    input_path = validate_input(args.filename)
    output_path = OUTPUT_DIR / f"{input_path.stem}.txt"

    try:
        print(f"モデルを読み込んでいます: {args.model}")
        model = WhisperModel(args.model, device="cpu", compute_type="int8")

        print("文字起こしを開始します...")
        segments, _info = model.transcribe(
            str(input_path),
            language="ja",
            vad_filter=True,
            initial_prompt=args.prompt,
        )

        content = format_segments(segments)
        if not content.strip():
            fail("認識結果が空でした。")

        write_output(output_path, content)
    except SystemExit:
        raise
    except Exception as exc:
        fail(f"文字起こしに失敗しました: {exc}")

    print("文字起こしが完了しました。")
    print(f"保存しました: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
