import typst

if __name__ == "__main__":
    title, author = "恐吓小说网", "幻影大厦"
    typst.compile("main.typ", output=f"{title}-{author}.pdf")
