from ebooklib import epub
import json

def escape_xml_characters(input_string):
    escape_dict = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&apos;'
    }
    return ''.join(escape_dict.get(char, char) for char in input_string)

with open("./恐吓小说网-幻影大厦.json", "rb") as f:
    data = json.load(f)

book = epub.EpubBook()

book.set_identifier("sfacg_110383")
book.set_title("恐吓小说网")
book.set_language("zh")
book.add_author("幻影大厦")

style = r'''
@charset "utf-8";
p {
    text-align: justify;
    text-indent: 2em;
}'''
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
book.add_item(nav_css)

total_chapters = []
toc = []
for superchapter, chapters in data:
    super_sec = epub.Section(superchapter)
    local_chapters = []
    for cpt_name, cpt_body in chapters:
        chapter = epub.EpubHtml(
            title=cpt_name, file_name=f"chap_{len(total_chapters)}.xhtml", lang="zh"
        )
        chapter.add_link(href='style/nav.css', rel='stylesheet', type='text/css')
        chapter.content = (
            (f"<h1>{superchapter}</h1>" if superchapter is not None else "")
            + f"<h2>{cpt_name}</h2>"
            + "".join(f'<p>{escape_xml_characters(p)}</p>' for p in cpt_body)
        )
        superchapter = None
        book.add_item(chapter)
        local_chapters.append(chapter)
        total_chapters.append(chapter)
    toc.append([super_sec, local_chapters])

book.toc = tuple(toc)
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
book.spine = ["nav", *total_chapters]

epub.write_epub("恐吓小说网-幻影大厦.epub", book, {})