#!/usr/bin/env python3
"""Offline, user-authorized audio -> timecoded SRT -> technical evidence candidates.

Does NOT fetch media or captions from streaming websites.
Needs a local audio/video file that the operator is entitled to process.
Install optional dependencies locally: pip install faster-whisper
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path

MAX_BYTES = 800_000_000
SUFFIXES = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".mp4", ".webm", ".mov"}
LANGUAGES = {"fr", "de", "en"}

def fmt_srt(seconds: float) -> str:
    if seconds < 0:
        raise ValueError("timestamps must be nonnegative")
    milliseconds = int(round(seconds * 1000))
    hours, rem = divmod(milliseconds, 3600000)
    minutes, rem = divmod(rem, 60000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def render_srt(segments) -> tuple[str, int]:
    lines = []
    prior = -1.0
    count = 0
    for segment in segments:
        begin, end = float(segment.start), float(segment.end)
        phrase = " ".join(str(segment.text).split())
        if not phrase or end <= begin or begin < 0 or begin < prior:
            continue
        count += 1
        lines.append(f"{count}\n{fmt_srt(begin)} --> {fmt_srt(end)}\n{phrase}\n")
        prior = begin
    if not count:
        raise ValueError("No valid timestamped speech segments")
    return "\n".join(lines) + "\n", count

def transcribe(path: Path, *, language: str, model_size: str, device: str="cpu",
               compute_type: str="int8", engine=None) -> tuple[str,int]:
    if engine is None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as ex:
            raise RuntimeError("Install faster-whisper locally: pip install faster-whisper") from ex
        engine = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, _info = engine.transcribe(str(path), language=language,
                                         beam_size=5, vad_filter=True)
    return render_srt(segments)

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audio", required=True, type=Path)
    p.add_argument("--language", choices=sorted(LANGUAGES), required=True)
    p.add_argument("--video-id", required=True)
    p.add_argument("--video-url", required=True)
    p.add_argument("--video-title", required=True)
    p.add_argument("--publisher", required=True)
    p.add_argument("--model", default="small")
    p.add_argument("--device", default="cpu", choices=["cpu","cuda"])
    p.add_argument("--output-dir", type=Path, default=Path("video-analysis/local-results"))
    p.add_argument("--confirm-media-rights", action="store_true")
    args=p.parse_args(argv)
    if not args.confirm_media_rights:
        p.error("Confirm that you have lawful access and permission to transcribe this local media file")
    if args.audio.suffix.lower() not in SUFFIXES or not args.audio.is_file():
        p.error("Supply an existing local WAV/MP3/M4A/FLAC/MP4/WebM/etc media file")
    size=args.audio.stat().st_size
    if not 0<size<=MAX_BYTES:
        p.error("Empty or oversized media file")
    from urllib.parse import urlparse
    u=urlparse(args.video_url)
    if u.scheme!="https" or not u.hostname:
        p.error("A valid HTTPS source URL is required")
    import importlib.util
    spec=importlib.util.spec_from_file_location("foil_lab_analyze", Path(__file__).with_name("analyze.py"))
    analyzer=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analyzer)
    srt, segments=transcribe(args.audio,language=args.language,model_size=args.model,device=args.device)
    video={"id":args.video_id, "url":args.video_url,
           "title":args.video_title, "publisher":args.publisher}
    report=analyzer.extract(video,srt,args.language,args.audio.name)
    with args.audio.open("rb") as fh:
        audio_hash = hashlib.file_digest(fh,"sha256").hexdigest()
    report["transcription_provenance"]={
        "method":"local_faster_whisper_asr",
        "audio_filename":args.audio.name,
        "audio_sha256":audio_hash,
        "engine_model":args.model,
        "source_permission_confirmed":True,
        "asr_not_human_verified":True,
    }
    report["asr_segments"]=segments
    args.output_dir.mkdir(parents=True,exist_ok=True)
    stem="".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in args.video_id)[:90]
    srt_path=args.output_dir/(stem+".srt")
    report_path=args.output_dir/(stem+".candidates.json")
    srt_path.write_text(srt,encoding="utf-8")
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"video_id":args.video_id,"asr_segments":segments,
                      "keyword_candidates":len(report["candidates"]),
                      "srt_path":str(srt_path),
                      "candidate_path":str(report_path),
                      "video_fully_watched":False,
                      "performance_scores":None},ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
