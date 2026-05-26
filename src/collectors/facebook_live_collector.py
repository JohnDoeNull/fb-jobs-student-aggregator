from __future__ import annotations

import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import quote_plus

import yaml
from playwright.sync_api import sync_playwright

from src.models import JobPost


class FacebookLiveCollector:
    """Collector thật dùng Playwright + cookies.

    Yêu cầu:
    - File cookies Netscape/JSON export từ browser tại data/secrets/facebook_cookies.json
    - Group URL phải truy cập được bởi tài khoản đó.
    """

    def __init__(self, config_path: str, cookies_path: str = "data/secrets/facebook_cookies.json"):
        self.config_path = Path(config_path)
        self.cookies_path = Path(cookies_path)
        self.config = yaml.safe_load(self.config_path.read_text(encoding="utf-8"))

    @staticmethod
    def _extract_job_posts(text: str) -> list[str]:
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        job_like = []
        kw = re.compile(r"(tuyển|hiring|intern|part[- ]?time|full[- ]?time|developer|engineer|thực tập)", re.I)
        for ln in lines:
            if len(ln) < 20:
                continue
            if kw.search(ln):
                job_like.append(ln)
        # giữ unique theo thứ tự
        seen = set()
        out = []
        for x in job_like:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    @staticmethod
    def _make_id(group: str, text: str) -> str:
        raw = f"{group}|{text}".encode("utf-8", errors="ignore")
        return hashlib.sha1(raw).hexdigest()[:16]

    def collect(self) -> List[JobPost]:
        groups = self.config.get("groups", [])
        crawl_cfg = self.config.get("crawl", {})
        max_posts = int(crawl_cfg.get("max_posts_per_group", 20))
        headless = bool(crawl_cfg.get("headless", True))
        scroll_rounds = int(crawl_cfg.get("scroll_rounds", 5))

        if not self.cookies_path.exists():
            raise FileNotFoundError(
                f"Missing cookies file: {self.cookies_path}. Export Facebook cookies JSON and place it there."
            )

        cookies = json.loads(self.cookies_path.read_text(encoding="utf-8"))
        all_jobs: list[JobPost] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context()
            context.add_cookies(cookies)
            page = context.new_page()

            for g in groups:
                name = g.get("name", "")
                url = g.get("url", "")
                seed_tags = g.get("tags", [])
                if not url:
                    # fallback: tìm group theo tên khi chưa có URL cụ thể
                    q = quote_plus(name)
                    url = f"https://www.facebook.com/search/groups/?q={q}"

                page.goto(url, wait_until="domcontentloaded", timeout=90_000)
                page.wait_for_timeout(3000)

                for _ in range(scroll_rounds):
                    page.mouse.wheel(0, 6000)
                    page.wait_for_timeout(1500)

                text = page.inner_text("body")
                candidates = self._extract_job_posts(text)[:max_posts]

                for c in candidates:
                    jid = self._make_id(name, c)
                    title = c[:120]
                    all_jobs.append(
                        JobPost(
                            id=jid,
                            source_group=name,
                            source_url=url,
                            title=title,
                            description=c,
                            location="",
                            salary=None,
                            posted_at=datetime.utcnow().date().isoformat(),
                            tags=seed_tags,
                        )
                    )

            browser.close()

        # dedup
        uniq = {}
        for j in all_jobs:
            uniq[j.id] = j
        return list(uniq.values())
