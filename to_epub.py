from ebooklib import epub
import json
from typst_parser import typst2xml, typst2text, escape_xml_characters


def escape(s: str, typst2_) -> str:
    s = s.strip()
    return (
        typst2_(s)
        if str.startswith(s, "#[") and str.endswith(s, "]")
        else escape_xml_characters(s)
    )


def write_epub(title: str, author: str, data, cover_image_path: str = None):
    book = epub.EpubBook()

    book.set_identifier(f"{title}-{author}")
    book.set_title(title)
    book.set_language("zh")
    book.add_author(author)

    if cover_image_path:
        with open(cover_image_path, "rb") as img_file:
            cover_image = img_file.read()
        book.set_cover("cover.png", cover_image)

    style = r"""
    @charset "utf-8";
    p {
        text-align: justify;
        text-indent: 2em;
    }"""
    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style
    )
    book.add_item(nav_css)

    total_chapters = []
    toc = []
    for superchapter, chapters in data:
        super_sec = epub.Section(escape(superchapter, typst2text))
        local_chapters = []
        for cpt_name, cpt_body in chapters:
            chapter = epub.EpubHtml(
                title=escape(cpt_name, typst2text),
                file_name=f"chap_{len(total_chapters)}.xhtml",
                lang="zh",
            )
            chapter.add_link(href="style/nav.css", rel="stylesheet", type="text/css")
            chapter.content = (
                (
                    f"<h1>{escape(superchapter, typst2xml)}</h1>"
                    if superchapter is not None
                    else ""
                )
                + f"<h2>{escape(cpt_name, typst2xml)}</h2>"
                + "".join(f"<p>{escape(p, typst2xml)}</p>" for p in cpt_body)
            )
            superchapter = None
            book.add_item(chapter)
            local_chapters.append(chapter)
            total_chapters.append(chapter)
        toc.append([super_sec, local_chapters])

    book.toc = toc
    book.add_item(epub.EpubNcx())
    book.spine = total_chapters

    epub.write_epub(f"{title}-{author}.epub", book, {})


if __name__ == "__main__":
    title, author = "恐吓小说网", "幻影大厦"
    with open(f"{title}-{author}.json", "rb") as f:
        data = json.load(f)
    write_epub(title, author, data, cover_image_path="./cover.png")
