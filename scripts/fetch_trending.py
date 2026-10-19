"""GitHub 주간 트렌딩 페이지를 받아 JSON과 마크다운으로 저장합니다.

GitHub Actions에서 매주 실행됩니다. 직접 실행하려면:
    pip install requests beautifulsoup4
    python scripts/fetch_trending.py
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://github.com/trending?since=weekly"
KST = timezone(timedelta(hours=9))
ROOT = Path(__file__).resolve().parent.parent


def to_int(text):
    digits = re.sub(r"[^0-9]", "", text or "")
    return int(digits) if digits else None


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    repos = []
    for rank, row in enumerate(soup.select("article.Box-row"), start=1):
        link = row.select_one("h2 a")
        if not link:
            continue
        full_name = re.sub(r"\s+", "", link.get("href", "")).strip("/")

        desc_el = row.select_one("p")
        lang_el = row.select_one('[itemprop="programmingLanguage"]')
        stars_el = row.select_one('a[href$="/stargazers"]')
        forks_el = row.select_one('a[href$="/forks"]')

        week_stars = None
        for span in row.select("span"):
            text = span.get_text(" ", strip=True)
            if "stars this week" in text:
                week_stars = to_int(text)
                break

        repos.append({
            "rank": rank,
            "repo": full_name,
            "url": f"https://github.com/{full_name}",
            "description": desc_el.get_text(" ", strip=True) if desc_el else "",
            "language": lang_el.get_text(strip=True) if lang_el else "",
            "stars_total": to_int(stars_el.get_text()) if stars_el else None,
            "forks_total": to_int(forks_el.get_text()) if forks_el else None,
            "stars_this_week": week_stars,
        })
    return repos


def fmt(n):
    return f"{n:,}" if isinstance(n, int) else "-"


def to_markdown(date_str, fetched_at, repos):
    lines = [
        f"# GitHub 주간 트렌딩 ({date_str})",
        "",
        f"수집 시각: {fetched_at} · 출처: {URL}",
        "",
        "| # | 저장소 | 언어 | 이번 주 스타 | 전체 스타 | 설명 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in repos:
        desc = r["description"].replace("|", "\\|")
        lines.append(
            f"| {r['rank']} | [{r['repo']}]({r['url']}) | {r['language'] or '-'} | "
            f"{fmt(r['stars_this_week'])} | {fmt(r['stars_total'])} | {desc} |"
        )
    return "\n".join(lines) + "\n"


def main():
    resp = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0 (github-trending-log)", "Accept-Language": "en-US"},
        timeout=30,
    )
    resp.raise_for_status()
    repos = parse(resp.text)
    if len(repos) < 5:
        # 페이지 구조가 바뀌었을 가능성이 큽니다. 빈 기록을 남기지 않고 실패로 끝냅니다.
        print(f"저장소를 {len(repos)}개만 찾았습니다. 페이지 구조가 바뀌었는지 확인하세요.", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d")
    record = {
        "date": date_str,
        "fetched_at": now.isoformat(timespec="seconds"),
        "source": URL,
        "repos": repos,
    }

    data_dir = ROOT / "data"
    weekly_dir = ROOT / "weekly"
    data_dir.mkdir(exist_ok=True)
    weekly_dir.mkdir(exist_ok=True)

    text = json.dumps(record, ensure_ascii=False, indent=2)
    (data_dir / f"{date_str}.json").write_text(text, encoding="utf-8")
    (data_dir / "latest.json").write_text(text, encoding="utf-8")
    (weekly_dir / f"{date_str}.md").write_text(
        to_markdown(date_str, record["fetched_at"], repos), encoding="utf-8"
    )
    print(f"{len(repos)}개 저장소 저장 완료: {date_str}")


if __name__ == "__main__":
    main()
