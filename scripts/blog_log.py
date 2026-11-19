"""네이버 블로그 RSS에서 발행한 글 목록을 받아 blog/posts.md로 저장한다.

매일 아침 브랜딩 브리핑이 이 파일을 읽고, 이미 쓴 주제와 겹치지 않게 원고를 고른다.
"""
import email.utils
import pathlib
import urllib.request
import xml.etree.ElementTree as ET
from datetime import timezone, timedelta

FEED = "https://rss.blog.naver.com/qhtjd1216.xml"
OUT = pathlib.Path("blog/posts.md")
KST = timezone(timedelta(hours=9))


def main() -> None:
    req = urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0 (blog-log)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())

    rows = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip().split("?")[0]
        category = (item.findtext("category") or "").strip()
        pub = item.findtext("pubDate") or ""
        try:
            date = email.utils.parsedate_to_datetime(pub).astimezone(KST).strftime("%Y-%m-%d")
        except (TypeError, ValueError):
            date = ""
        if title:
            rows.append((date, category, title, link))

    rows.sort(key=lambda r: r[0], reverse=True)
    lines = [
        "# 블로그에 발행한 글",
        "",
        "네이버 블로그 RSS에서 매일 자동으로 받아 오는 목록입니다 (최신순).",
        "",
        "| 날짜 | 카테고리 | 제목 |",
        "|---|---|---|",
    ]
    for date, category, title, link in rows:
        title_cell = title.replace("|", "／")
        lines.append(f"| {date} | {category} | [{title_cell}]({link}) |")
    if not rows:
        lines.append("| - | - | 아직 발행한 글이 없습니다 |")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(rows)}개 글 기록")


if __name__ == "__main__":
    main()
