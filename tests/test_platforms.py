import unittest

from ytconverter.platforms import detect_platform, extract_url


class ExtractUrlTest(unittest.TestCase):
    def test_plain_link(self):
        self.assertEqual(
            extract_url("https://vkvideo.ru/video-18403220_456239696"),
            "https://vkvideo.ru/video-18403220_456239696",
        )

    def test_link_inside_text(self):
        self.assertEqual(
            extract_url("смотри https://vk.com/video-140332_456239111 !"),
            "https://vk.com/video-140332_456239111",
        )

    def test_bare_host_gets_scheme(self):
        self.assertEqual(extract_url("youtu.be/aqz-KE-bpKQ"), "https://youtu.be/aqz-KE-bpKQ")
        self.assertEqual(
            extract_url("look: vkvideo.ru/video-1_2"), "https://vkvideo.ru/video-1_2"
        )

    def test_http_upgraded(self):
        self.assertEqual(extract_url("http://vk.com/clip1_2"), "https://vk.com/clip1_2")

    def test_trailing_punctuation(self):
        self.assertEqual(
            extract_url("(https://www.youtube.com/watch?v=abc)."),
            "https://www.youtube.com/watch?v=abc",
        )

    def test_nothing(self):
        self.assertEqual(extract_url(""), "")
        self.assertEqual(extract_url("just some words"), "")


class DetectPlatformTest(unittest.TestCase):
    def test_youtube(self):
        for url in (
            "https://www.youtube.com/watch?v=abc",
            "https://m.youtube.com/shorts/abc",
            "https://music.youtube.com/watch?v=abc",
            "https://youtu.be/abc",
            "https://www.youtube-nocookie.com/embed/abc",
        ):
            self.assertEqual(detect_platform(url), "youtube", url)

    def test_vk(self):
        for url in (
            "https://vk.com/video-1_2",
            "https://m.vk.com/video-1_2",
            "https://vk.ru/video-1_2",
            "https://vkvideo.ru/video-1_2",
            "https://vksport.vkvideo.ru/video-1_2",
            "https://vk.com/video_ext.php?oid=-1&id=2&hash=x",
            "https://vkvideo.ru/playlist/-1_2",
        ):
            self.assertEqual(detect_platform(url), "vk", url)

    def test_lookalikes_rejected(self):
        for url in (
            "https://notyoutube.com/watch?v=abc",
            "https://vk.com.evil.example/video-1_2",
            "https://example.com/?u=youtube.com",
            "not a url",
        ):
            self.assertIsNone(detect_platform(url), url)


if __name__ == "__main__":
    unittest.main()


class NormalizeUrlTest(unittest.TestCase):
    def test_vk_embed_rewritten(self):
        self.assertEqual(
            extract_url("https://vk.com/video_ext.php?oid=-18403220&id=456239696&hash=4e73"),
            "https://vk.com/video-18403220_456239696",
        )
        self.assertEqual(
            extract_url("vkvideo.ru/video_ext.php?oid=30014565&id=456240946&hash=7d7b&hd=2"),
            "https://vk.com/video30014565_456240946",
        )

    def test_other_links_untouched(self):
        self.assertEqual(
            extract_url("https://vk.com/video_ext.php?oid=abc&id=1"),
            "https://vk.com/video_ext.php?oid=abc&id=1",
        )
        self.assertEqual(
            extract_url("https://www.youtube.com/watch?v=abc&oid=1&id=2"),
            "https://www.youtube.com/watch?v=abc&oid=1&id=2",
        )
