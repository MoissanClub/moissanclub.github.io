#!/usr/bin/env python3
"""Check the generated static site using only Python's standard library."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.canonical = None
        self.has_heading = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h1":
            self.has_heading = True
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        key = "href" if tag in ("a", "link") else "src" if tag in ("img", "script") else None
        if key and attrs.get(key):
            self.links.append(attrs[key])


def target_exists(directory, url):
    candidate = directory / unquote(urlsplit(url).path).lstrip("/")
    return candidate.is_file() or (candidate / "index.html").is_file()


def check_site(directory, base_url):
    directory = directory.resolve()
    errors = []
    for relative in ("index.html", "projects/index.html", "newsletter/index.html", "newsletter/index.xml", "404.html", "sitemap.xml", "robots.txt"):
        if not (directory / relative).is_file():
            errors.append(f"Missing generated file: {relative}")

    pages = sorted(directory.rglob("*.html"))
    for path in pages:
        relative = path.relative_to(directory)
        route = "/" + relative.as_posix()
        if route.endswith("index.html"):
            route = route[:-10]
        html = path.read_text(encoding="utf-8")
        page = Page()
        page.feed(html)
        if not page.canonical or not page.canonical.startswith(base_url):
            errors.append(f"{relative}: missing canonical URL or wrong domain")
        # Hugo's alias pages intentionally have no heading.
        is_alias = 'http-equiv="refresh"' in html.lower() or "http-equiv=refresh" in html.lower()
        if not page.has_heading and not is_alias:
            errors.append(f"{relative}: missing h1")
        for link in page.links:
            # Full URLs may belong to separate deployments on the same domain.
            source = urlsplit(link)
            if source.scheme or source.netloc:
                continue
            target = urlsplit(urljoin(base_url.rstrip("/") + route, link))
            if not target_exists(directory, target.geturl()):
                errors.append(f"{relative}: broken local link {link}")

    feed = directory / "newsletter/index.xml"
    if feed.is_file():
        channel = ET.parse(feed).getroot().find("channel")
        if channel is None or channel.findtext("link") != base_url + "newsletter/":
            errors.append("Newsletter RSS has the wrong channel URL")
        else:
            for item in channel.findall("item"):
                link = item.findtext("link", "")
                if not link.startswith(base_url) or not target_exists(directory, link):
                    errors.append(f"Newsletter RSS contains an invalid or broken item URL: {link}")

    if errors:
        raise SystemExit("Site checks failed:\n- " + "\n- ".join(errors))
    print(f"Site checks passed: {len(pages)} HTML pages, relative assets and links, canonical domain, and newsletter RSS.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", default="public", type=Path)
    parser.add_argument("--base-url", default="https://moissan.org/")
    args = parser.parse_args()
    check_site(args.directory, args.base_url.rstrip("/") + "/")
