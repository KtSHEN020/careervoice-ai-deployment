import argparse
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from voice_career_profile_extractor.audio_recorder import (
    record_microphone_to_wav,
)
from voice_career_profile_extractor.audio_transcriber import (
    transcribe_audio_file,
)
from voice_career_profile_extractor.exporters import (
    profile_to_json,
    save_profile_json,
)
from voice_career_profile_extractor.extractor import extract_career_profile
from voice_career_profile_extractor.llm_extractor import (
    SUPPORTED_OUTPUT_LANGUAGES,
    extract_career_profile_with_llm,
)
from voice_career_profile_extractor.models import CareerProfile
from voice_career_profile_extractor.transcript import load_transcript


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command line argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Extract a structured career profile from text or voice input."
    )

    subparsers = parser.add_subparsers(
        dest="input_mode",
        required=True,
    )

    file_parser = subparsers.add_parser(
        "file",
        help="Load career preferences from an existing transcript text file.",
    )
    file_parser.add_argument(
        "input_path",
        type=Path,
        help="Path to a text file containing career preferences.",
    )
    _add_shared_arguments(file_parser)

    text_parser = subparsers.add_parser(
        "text",
        help="Type career preferences directly into the terminal.",
    )
    _add_shared_arguments(text_parser)

    voice_parser = subparsers.add_parser(
        "voice",
        help="Record career preferences from the microphone.",
    )
    _add_shared_arguments(voice_parser)

    return parser


def _add_shared_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--extractor",
        choices=["rules", "llm"],
        default="rules",
        help=(
            "Profile extraction mode. "
            "Use 'rules' for offline extraction or 'llm' for OpenAI extraction. "
            "Defaults to 'rules'."
        ),
    )

    parser.add_argument(
        "--output-language",
        choices=SUPPORTED_OUTPUT_LANGUAGES,
        default="en",
        help=(
            "Language for AI-generated human-readable profile values. "
            "Supported values: en, zh-CN. Defaults to en."
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional path to save the extracted career profile as JSON.",
    )


def _load_input_text(args: argparse.Namespace) -> str:
    if args.input_mode == "file":
        return load_transcript(args.input_path)

    if args.input_mode == "text":
        return _read_typed_input()

    if args.input_mode == "voice":
        return _record_and_transcribe_voice()

    raise ValueError(f"Unsupported input mode: {args.input_mode}")


def _read_typed_input() -> str:
    text = input("Enter your career preferences:\n> ").strip()

    if not text:
        raise ValueError("Typed career profile input is empty.")

    return text


def _record_and_transcribe_voice() -> str:
    with TemporaryDirectory(prefix="career_profile_voice_") as temporary_directory:
        recording_path = Path(temporary_directory) / "recording.wav"

        print("Recording career preferences from microphone.", file=sys.stderr)
        record_microphone_to_wav(recording_path)

        print("Transcribing recorded audio...", file=sys.stderr)
        return transcribe_audio_file(recording_path)


def _extract_profile(
    text: str,
    extractor: str,
    output_language: str,
) -> CareerProfile:
    if extractor == "llm":
        return extract_career_profile_with_llm(
            text,
            output_language=output_language,
        )

    return extract_career_profile(text)


def _output_profile(
    profile: CareerProfile,
    output_path: Path | None,
) -> None:
    if output_path:
        saved_path = save_profile_json(profile, output_path)
        print(f"Saved career profile JSON to {saved_path}")
    else:
        print(profile_to_json(profile))


def main(argv: list[str] | None = None) -> int:
    """
    Run the command line interface.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    text = _load_input_text(args)
    profile = _extract_profile(
        text,
        args.extractor,
        args.output_language,
    )
    _output_profile(profile, args.output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
