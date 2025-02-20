from crawler import crawl_novel
from to_epub import write_epub

title, author, outline = crawl_novel("191310")
write_epub(title, author, outline, cover_image_path="./cover.png")
