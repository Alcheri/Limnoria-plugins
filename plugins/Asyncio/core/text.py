# -*- coding: utf-8 -*-

from __future__ import annotations

import re


def count_tokens(text: str | None) -> int:
    return len((text or "").split())


def is_likely_math(query: str | None) -> bool:
    math_pattern = (
        r"[\d\+\-\*/\^\=<>√∑∫π()]|"
        r"\b(solve|calculate|evaluate|simplify|factor|equation|system of|"
        r"legs|heads|probability|percent|ratio|algebra|geometry|integral|derivative)\b"
    )
    return bool(re.search(math_pattern, query or "", re.IGNORECASE))


def clean_output(text: str | None) -> str:
    if not text:
        return ""

    cleaned = text.replace("\\(", "").replace("\\)", "")
    cleaned = cleaned.replace("\\[", "").replace("\\]", "")
    cleaned = cleaned.replace("\\left", "").replace("\\right", "")
    cleaned = cleaned.replace("\\cdot", "⋅")

    cleaned = re.sub(r"\\text\{(.*?)\}", r"\1", cleaned)
    cleaned = cleaned.replace("\\", "")
    cleaned = re.sub(r"\n\s*\n+", "\n", cleaned)

    return cleaned.strip()


def split_irc_reply_lines(text: str | None, chunk_size: int = 350) -> list[str]:
    payload = (text or "").strip()
    if not payload:
        return []

    chunks: list[str] = []
    lines = payload.splitlines()
    for line in lines:
        line = (line or "").strip()
        if not line:
            continue

        while len(line) > chunk_size:
            chunks.append(line[:chunk_size])
            line = line[chunk_size:].lstrip()

        chunks.append(line)

    return chunks
