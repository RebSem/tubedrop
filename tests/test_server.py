import unittest

from ytconverter.web import server as S


class ThrottleHeuristicTest(unittest.TestCase):
    def test_only_progressive_360_is_throttled(self):
        fmts = [{"format_id": "18", "vcodec": "avc1", "acodec": "mp4a", "width": 640, "height": 360}]
        self.assertTrue(S._looks_throttled(fmts, S._Logger()))

    def test_old_low_res_upload_is_not_throttled(self):
        fmts = [
            {"format_id": "133", "vcodec": "avc1", "acodec": "none", "width": 320, "height": 240},
            {"format_id": "140", "vcodec": "none", "acodec": "mp4a"},
        ]
        self.assertFalse(S._looks_throttled(fmts, S._Logger()))

    def test_hd_available_is_not_throttled(self):
        fmts = [{"format_id": "299", "vcodec": "avc1", "acodec": "none", "width": 1920, "height": 1080}]
        self.assertFalse(S._looks_throttled(fmts, S._Logger()))


class JobCleanupTest(unittest.TestCase):
    def test_cleanup_skips_finished_items_and_unknown_files(self):
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            def touch(name):
                path = os.path.join(d, name)
                open(path, "w").close()
                return path

            done = touch("001 - A [a] 720p.mp4")
            done_sub = touch("001 - A [a] 720p.ru.srt")
            part = touch("002 - B [b] 720p.f298.mp4.part")
            thumb = touch("002 - B [b] 720p.jpg")
            unrelated = touch("my notes.txt")

            job = S.Job({})
            job.track("a", done.replace(".mp4", ".f298.mp4"), done_sub)
            job.files.append(done)
            job.items["a"]["done"] = True
            job.track("b", part.replace(".part", ""), thumb)
            S._cleanup_partial(job)

            self.assertTrue(os.path.exists(done))
            self.assertTrue(os.path.exists(done_sub))
            self.assertTrue(os.path.exists(unrelated))
            self.assertFalse(os.path.exists(part))
            self.assertFalse(os.path.exists(thumb))


class LiveFilterTest(unittest.TestCase):
    def test_live_entries_are_skipped(self):
        job = S.Job({})
        f = S._make_live_filter(job)
        self.assertIsNotNone(f({"live_status": "is_live", "title": "radio"}))
        self.assertIsNone(f({"live_status": "was_live"}))
        self.assertEqual(len(job.live_skipped), 1)


if __name__ == "__main__":
    unittest.main()


class PlaylistSummaryTest(unittest.TestCase):
    def test_channel_tabs_are_flattened_and_only_one_video_extracted(self):
        calls = []
        tabs = {
            "https://yt/@c/videos": {"entries": [
                {"_type": "url", "ie_key": "Youtube", "url": "https://yt/watch?v=1"},
                {"_type": "url", "ie_key": "Youtube", "url": "https://yt/watch?v=2"},
            ]},
            "https://yt/@c/shorts": {"entries": [
                {"_type": "url", "ie_key": "Youtube", "url": "https://yt/shorts/3"},
            ]},
        }

        def fake_extract(url, **extra):
            calls.append((url, extra.get("extract_flat")))
            if url in tabs:
                return tabs[url], [], S._Logger()
            return {"id": url, "formats": [{"format_id": "18"}]}, [], S._Logger()

        info = {"_type": "playlist", "entries": [
            {"_type": "url", "ie_key": "YoutubeTab", "url": "https://yt/@c/videos"},
            {"_type": "url", "ie_key": "YoutubeTab", "url": "https://yt/@c/shorts"},
        ]}
        original = S._extract
        S._extract = fake_extract
        try:
            count, first, _notices, _logger = S._playlist_summary(info)
        finally:
            S._extract = original

        self.assertEqual(count, 3)
        self.assertEqual(first["id"], "https://yt/watch?v=1")
        video_calls = [c for c in calls if "watch" in c[0] or "shorts/" in c[0]]
        self.assertEqual(len(video_calls), 1)
        self.assertTrue(all(flat == "in_playlist" for _, flat in calls))
