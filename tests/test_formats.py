import json
import unittest
from pathlib import Path

from ytconverter import formats as F

FIXTURES = json.loads((Path(__file__).parent / "fixtures" / "formats.json").read_text())
YT = FIXTURES["https://www.youtube.com/watch?v=aqz-KE-bpKQ"]
VK_1080 = FIXTURES["https://vk.ru/video-220754053_456242564"]
VK_WIDE = FIXTURES["https://vkvideo.ru/video-18403220_456239696"]
VK_HLS = FIXTURES["https://vk.com/video-140332_456239111"]


class QualityClassTest(unittest.TestCase):
    def test_common_sizes(self):
        cases = {
            (256, 144): 144, (426, 240): 240, (640, 360): 360, (854, 480): 480,
            (852, 480): 480, (1280, 720): 720, (1920, 1080): 1080,
            (2560, 1440): 1440, (3840, 2160): 2160,
        }
        for (w, h), expected in cases.items():
            self.assertEqual(F.quality_class(w, h), expected, (w, h))

    def test_non_16_9(self):
        self.assertEqual(F.quality_class(1920, 960), 1080)   # VK 2:1
        self.assertEqual(F.quality_class(1920, 800), 1080)   # cinema
        self.assertEqual(F.quality_class(1080, 1920), 1080)  # vertical clip
        self.assertEqual(F.quality_class(1440, 1080), 1080)  # 4:3
        self.assertEqual(F.quality_class(640, 480), 480)

    def test_partial_dimensions(self):
        self.assertEqual(F.quality_class(None, 1080), 1080)
        self.assertIsNone(F.quality_class(None, None))

    def test_labels(self):
        self.assertEqual(F.class_label(2160, 60), "4K60")
        self.assertEqual(F.class_label(1080, 50), "1080p50")
        self.assertEqual(F.class_label(720, 30), "720p")


class ChooseVideoTest(unittest.TestCase):
    def spec(self, fixture, quality="best", can_merge=True):
        choice = F.choose_video(fixture["formats"], quality, can_merge)
        return choice.format_spec if choice else None

    def test_youtube_prefers_h264_with_aac(self):
        self.assertEqual(self.spec(YT, "1080"), "299+140")
        self.assertEqual(self.spec(YT, "720"), "298+140")

    def test_youtube_best_takes_highest_resolution(self):
        choice = F.choose_video(YT["formats"], "best")
        self.assertEqual(choice.quality_class, 2160)
        self.assertEqual(choice.formats[1]["format_id"], "140")

    def test_vk_skips_legacy_progressive_file(self):
        # "url1080" reports height=1080 but is the low-bitrate legacy file.
        self.assertEqual(self.spec(VK_WIDE), "dash_sep-6+dash_sep-11")
        self.assertEqual(self.spec(VK_1080), "dash_sep-6+dash_sep-11")

    def test_vk_quality_cap(self):
        self.assertEqual(self.spec(VK_1080, "720"), "dash_sep-5+dash_sep-11")

    def test_vk_muxed_hls(self):
        self.assertEqual(self.spec(VK_HLS), "hls_ondemand-2442")

    def test_without_ffmpeg_only_muxed(self):
        self.assertIsNone(self.spec(YT, can_merge=False))
        spec = self.spec(VK_1080, can_merge=False)
        fmt = next(f for f in VK_1080["formats"] if f["format_id"] == spec)
        self.assertNotEqual(fmt.get("acodec"), "none")

    def test_target_below_available_takes_lowest(self):
        formats = [f for f in VK_HLS["formats"] if (f.get("height") or 0) >= 720 or f.get("vcodec") == "none"]
        choice = F.choose_video(formats, "144")
        self.assertEqual(choice.quality_class, 720)


class ChooseAudioTest(unittest.TestCase):
    def test_best_audio_track(self):
        self.assertEqual(F.choose_audio(YT["formats"]).format_spec, "140")
        self.assertEqual(F.choose_audio(VK_1080["formats"]).format_spec, "dash_sep-11")

    def test_muxed_only_fallback(self):
        muxed = [f for f in VK_HLS["formats"] if f.get("vcodec") != "none"]
        choice = F.choose_audio(muxed)
        self.assertIsNotNone(choice)
        self.assertNotEqual(choice.formats[0].get("acodec"), "none")


class FilenameTagTest(unittest.TestCase):
    def test_video_tag_uses_resolved_class(self):
        best = F.choose_video(VK_WIDE["formats"], "best")
        self.assertEqual(F.filename_tag("mp4", "best", best), "1080p50")
        capped = F.choose_video(YT["formats"], "720")
        self.assertEqual(F.filename_tag("mp4", "720", capped), "720p60")

    def test_audio_tag(self):
        self.assertEqual(F.filename_tag("mp3", "best", None), "")
        self.assertEqual(F.filename_tag("mp3", "128", None), "128k")


class LadderTest(unittest.TestCase):
    def test_video_ladder_matches_choices(self):
        ladder = F.video_ladder(VK_WIDE["formats"], VK_WIDE["duration"])
        values = [row["value"] for row in ladder]
        self.assertEqual(values, ["best", "1080", "720", "480", "360", "240", "144"])
        self.assertEqual(ladder[0]["label"], "1080p50")
        for row in ladder:
            self.assertTrue(row["size_estimate"], row)

    def test_playlist_ladder_hides_sizes(self):
        ladder = F.video_ladder(VK_WIDE["formats"], None, with_sizes=False)
        self.assertTrue(ladder)
        self.assertTrue(all(row["size_estimate"] is None for row in ladder))

    def test_audio_ladder_sizes(self):
        ladder = F.audio_ladder(100)
        self.assertEqual([r["value"] for r in ladder], ["best", "320", "256", "192", "128"])
        self.assertEqual(ladder[1]["size_estimate"], 4_000_000)


if __name__ == "__main__":
    unittest.main()
