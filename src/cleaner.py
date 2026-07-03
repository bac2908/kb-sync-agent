import re

import html2text
from bs4 import BeautifulSoup


def clean_html(html: str) -> str:
    """
    Remove elements that are not useful for support knowledge retrieval.
    """
    soup = BeautifulSoup(html or "", "html.parser")

    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()

    for tag in soup.find_all(["span", "div"]):
        if not tag.get_text(strip=True) and not tag.find(["img", "a", "code", "pre"]):
            tag.decompose()

    return str(soup)


def html_to_markdown(html: str) -> str:
    """
    Convert cleaned HTML to Markdown while preserving links and images.
    """
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.body_width = 0
    converter.unicode_snob = True
    converter.protect_links = True
    markdown = converter.handle(html)

    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip()
