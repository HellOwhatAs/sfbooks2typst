import json
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm


def crawl_novel(novel_id: str = "110383"):
    headers = {"User-Agent": UserAgent(platforms=["desktop"]).edge}
    response = requests.get(
        f"https://book.sfacg.com/Novel/{novel_id}/", headers=headers
    )
    soup = BeautifulSoup(response.content, "lxml")
    author = str.strip(soup.select_one("div.author-name").text).replace("\xa0", " ")

    response = requests.get(
        f"https://book.sfacg.com/Novel/{novel_id}/MainIndex/", headers=headers
    )
    soup = BeautifulSoup(response.content, "lxml")
    title = str.strip(soup.select_one("h1.story-title").text).replace("\xa0", " ")

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

    pbar = tqdm(total=sum(len(i) for _, i in outline), desc=title)
    for _, catalog in outline:
        for cpt_name, cpt_url, cpt_content in catalog:
            response = requests.get(
                urljoin("https://book.sfacg.com/", cpt_url), headers=headers
            )
            soup = BeautifulSoup(response.content, "lxml")
            cpt_content.clear()
            cpt_content.extend(
                str.strip(p.text).replace("\xa0", " ")
                for p in soup.select("#ChapterBody > p")
            )
            pbar.set_postfix_str(cpt_name)
            pbar.update()

    outline = [
        [
            str.replace(catalog_name, f"【{title}】", "").strip(),
            [(cpt_name, cpt_content) for cpt_name, _, cpt_content in catalog],
        ]
        for catalog_name, catalog in outline
    ]

    return title, author, outline


if __name__ == "__main__":
    title, author, outline = crawl_novel()
    with open(f"{title}-{author}.json", "w", encoding="utf-8") as f:
        json.dump(
            outline,
            f,
            indent=4,
            ensure_ascii=False,
        )
