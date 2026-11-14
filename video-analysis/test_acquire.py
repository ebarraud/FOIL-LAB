"""Offline tests for yt-dlp caption acquisition and status semantics."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("acquire", HERE / "acquire.py")
acquire = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acquire)


def v(url="https://www.youtube.com/watch?v=7wOjU-wA6aQ", lang="fr"):
    return {"id": "test", "url": url, "publisher": "YouTube", "language": lang}


class AcquisitionTests(unittest.TestCase):
    def test_reject_index_page_without_network(self):
        item = v("https://gleiten.tv/foil/test/wingfoil/foil/")
        self.assertEqual(acquire.run_video(item, "probe")["reason"], "index_not_individual_video")

    def test_reject_external_host(self):
        self.assertEqual(acquire.run_video(v("https://not-a-video.example/watch?v=foo"), "probe")["status"], "skipped")

    def test_probe_never_claims_video_watched(self):
        outcome = acquire.run_video(v(), "probe", runner=lambda args: subprocess.CompletedProcess(args, 0, "Available subtitles\n", ""))
        self.assertEqual(outcome["status"], "probed")
        self.assertFalse(outcome["video_fully_watched"])
        self.assertFalse(outcome["transcript_analyzed"])

    def test_failure_is_not_availability(self):
        outcome = acquire.run_video(v(), "probe", runner=lambda args: subprocess.CompletedProcess(args, 1, "", "ERROR HTTP Error 403"))
        self.assertEqual(outcome["reason"], "access_denied")
        self.assertFalse(outcome["transcript_analyzed"])

    def test_fetch_without_captions_never_claims_analysis(self):
        outcome = acquire.run_video(v(), "fetch", runner=lambda args: subprocess.CompletedProcess(args, 0, "", ""))
        self.assertEqual(outcome["status"], "no_vtt")

    def test_cmd_never_requests_audio_video(self):
        args = acquire.command(v(), "fetch", Path("/tmp"), "fr")
        self.assertIn("--skip-download", args)
        self.assertIn("--write-auto-subs", args)
        self.assertIn("--write-subs", args)
        self.assertNotIn("--extract-audio", args)

    def test_prohibits_fetch_without_acknowledgement(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "manifest.json"
            path.write_text(json.dumps({"videos":[v()]}), encoding="utf-8")
            with self.assertRaises(SystemExit) as raised:
                acquire.main(["--manifest", str(path), "--mode", "fetch", "--output", str(Path(folder)/"out.json")])
            self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
