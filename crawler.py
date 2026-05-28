import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
from playwright.sync_api import sync_playwright


def crawl_novel(novel_id: str = "110383"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()

            def goto(url):
                page.goto(url, wait_until="domcontentloaded", timeout=15000)

            goto(f"https://book.sfacg.com/Novel/{novel_id}/")
            soup = BeautifulSoup(page.content(), "lxml")
            author = str.strip(soup.select_one("div.author-name").text).replace(
                "\xa0", " "
            )

            goto(f"https://book.sfacg.com/Novel/{novel_id}/MainIndex/")
            soup = BeautifulSoup(page.content(), "lxml")
            title = str.strip(soup.select_one("h1.story-title").text).replace(
                "\xa0", " "
            )

            cache_file = Path(f"{title}-{author}.json")

            outline = [
                (
                    str.strip(i.select_one(".catalog-title").text).replace("\xa0", " "),
                    [
                        (str.strip(j.text).replace("\xa0", " "), j["href"], [])
                        for j in i.select("div.catalog-list > ul > li > a")
                    ],
                )
                for i in soup.select("div.story-catalog")
            ]
            current_names = [
                cpt_name for _, catalog in outline for cpt_name, _, _ in catalog
            ]

            cached_names = []
            cached_contents = []
            if cache_file.exists():
                with cache_file.open("r", encoding="utf-8") as f:
                    cached_outline = json.load(f)
                cached_names = [
                    cpt_name for _, catalog in cached_outline for cpt_name, _ in catalog
                ]
                if cached_names == current_names:
                    return title, author, cached_outline
                cached_contents = [
                    cpt_content
                    for _, catalog in cached_outline
                    for _, cpt_content in catalog
                ]

            flat_outline = [cpt for _, catalog in outline for cpt in catalog]
            with tqdm(
                total=sum(
                    i >= len(cached_names) or cpt_name != cached_names[i]
                    for i, (cpt_name, _, _) in enumerate(flat_outline)
                ),
                desc=title,
            ) as pbar:
                chapter_index = 0
                for _, catalog in outline:
                    for cpt_name, cpt_url, cpt_content in catalog:
                        if (
                            chapter_index < len(cached_names)
                            and cpt_name == cached_names[chapter_index]
                        ):
                            cpt_content.extend(cached_contents[chapter_index])
                            chapter_index += 1
                            continue

                        goto(urljoin("https://book.sfacg.com/", cpt_url))
                        soup = BeautifulSoup(page.content(), "lxml")

                        cpt_content.clear()
                        cpt_content.extend(
                            str.strip(p.text).replace("\xa0", " ")
                            for p in soup.select("#ChapterBody > p")
                        )
                        chapter_index += 1
                        pbar.set_postfix_str(cpt_name)
                        pbar.update()

            outline = [
                [
                    catalog_name.replace(f"\u3010{title}\u3011", "").strip(),
                    [(cpt_name, cpt_content) for cpt_name, _, cpt_content in catalog],
                ]
                for catalog_name, catalog in outline
            ]

            return title, author, outline
        finally:
            browser.close()


if __name__ == "__main__":
    title, author, outline = crawl_novel()
    output_file = Path(f"{title}-{author}.json")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(
            outline,
            f,
            indent=4,
            ensure_ascii=False,
        )
