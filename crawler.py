from selenium.webdriver import Edge as Driver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager as DriverManager
import json

browser = Driver(service=Service(DriverManager().install()))

browser.get("https://book.sfacg.com/Novel/110383/")
author = browser.find_element(By.CSS_SELECTOR, "div.author-name").text
browser.find_element(By.CSS_SELECTOR, "#BasicOperation > a:nth-child(1)").click()
title = browser.find_element(By.CSS_SELECTOR, "h1.story-title").text

outline = [
    (
        i.find_element(By.CSS_SELECTOR, ".catalog-title").text,
        [
            (j.text, j.get_attribute("href"), [])
            for j in i.find_elements(By.CSS_SELECTOR, "div.catalog-list > ul > li > a")
        ],
    )
    for i in browser.find_elements(By.CSS_SELECTOR, "div.story-catalog")
]

for catalog_name, catalog in outline:
    for cpt_name, cpt_url, cpt_content in catalog:
        browser.get(cpt_url)
        cpt_content.clear()
        cpt_content.extend(
            p.text for p in browser.find_elements(By.CSS_SELECTOR, "#ChapterBody > p")
        )

browser.quit()
with open(f"{title}-{author}.json", "w", encoding="utf-8") as f:
    json.dump(
        [
            [
                catalog_name.replace(f"【{title}】", "").strip(),
                [(cpt_name, cpt_content) for cpt_name, _, cpt_content in catalog],
            ]
            for catalog_name, catalog in outline
        ],
        f,
        indent=4,
        ensure_ascii=False,
    )
