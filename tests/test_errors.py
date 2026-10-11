import unittest

from ytconverter.errors import clean, explain


class ExplainTest(unittest.TestCase):
    def check(self, raw, code, needs_browser=None):
        result = explain(raw)
        self.assertEqual(result["code"], code, result)
        if needs_browser is not None:
            self.assertEqual(result["needs_browser"], needs_browser)
        return result

    def test_bot_check(self):
        self.check(
            "ERROR: [youtube] abc: Sign in to confirm you’re not a bot. Use --cookies-from-browser "
            "or --cookies for the authentication.",
            "bot_check", True,
        )

    def test_vk_registered_users(self):
        self.check(
            "ERROR: [vk] -1_2: Video -1_2 is only available for registered users, use --username "
            "and --password options to provide account credentials.",
            "login_required", True,
        )

    def test_extractor_bug(self):
        self.check(
            "ERROR: [vk:uservideos] @x: Unable to extract cursor data; please report this issue on "
            " https://github.com/yt-dlp/yt-dlp/issues?q= , filling out the appropriate issue template.",
            "extractor_broken", False,
        )

    def test_age_is_not_bot_check(self):
        self.check("ERROR: [youtube] x: Sign in to confirm your age. This video may be "
                   "inappropriate for some users.", "age_restricted", True)

    def test_youtube_unavailable_wording(self):
        self.check("ERROR: [youtube] aaaaaaaaaaa: This video is unavailable", "removed")

    def test_live(self):
        self.check("This is a live event — it can be downloaded after it finishes.", "live")

    def test_misc(self):
        self.check("ERROR: unable to download video data: HTTP Error 403: Forbidden", "forbidden")
        self.check("ERROR: [youtube] x: Video unavailable", "removed")
        self.check("[Errno 28] No space left on device", "no_space")
        self.check("Postprocessing: ffprobe and ffmpeg not found. Please install", "ffmpeg_missing")
        self.check("HTTP Error 429: Too Many Requests", "rate_limited")
        self.check("something odd", "unknown")

    def test_clean(self):
        self.assertEqual(
            clean("\x1b[0;31mERROR:\x1b[0m [youtube] abc: Video unavailable"),
            "Video unavailable",
        )


if __name__ == "__main__":
    unittest.main()
