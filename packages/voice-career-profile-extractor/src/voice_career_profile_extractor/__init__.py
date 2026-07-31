"""Voice Career Profile Extractor.

A simple Python package for extracting structured career profile information
from text input or voice transcripts.
"""

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
    extract_career_profile_with_llm,
)
from voice_career_profile_extractor.models import CareerProfile
from voice_career_profile_extractor.transcript import (
    clean_transcript_text,
    load_transcript,
)

__version__ = "0.1.0"

__all__ = [
    "CareerProfile",
    "__version__",
    "clean_transcript_text",
    "extract_career_profile",
    "extract_career_profile_with_llm",
    "load_transcript",
    "profile_to_json",
    "record_microphone_to_wav",
    "save_profile_json",
    "transcribe_audio_file",
]
