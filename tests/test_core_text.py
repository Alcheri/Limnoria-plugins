# -*- coding: utf-8 -*-

import unittest

from ..core.text import (
    clean_output,
    count_tokens,
    is_likely_math,
    split_irc_reply_lines,
)


class CoreTextTestCase(unittest.TestCase):
    def test_count_tokens(self):
        self.assertEqual(count_tokens("one two three"), 3)
        self.assertEqual(count_tokens(""), 0)
        self.assertEqual(count_tokens(None), 0)

    def test_is_likely_math(self):
        self.assertTrue(is_likely_math("calculate 3+4"))
        self.assertTrue(is_likely_math("Solve this equation"))
        self.assertFalse(is_likely_math("Tell me a story"))

    def test_clean_output(self):
        raw = r"\\(x\\) \\text{answer} \\cdot y"
        self.assertEqual(clean_output(raw), "x answer ⋅ y")

    def test_split_irc_reply_lines(self):
        chunks = split_irc_reply_lines("abcdef", chunk_size=3)
        self.assertEqual(chunks, ["abc", "def"])

        chunks = split_irc_reply_lines("a\n\n b ", chunk_size=10)
        self.assertEqual(chunks, ["a", "b"])

        self.assertEqual(split_irc_reply_lines("", chunk_size=10), [])
