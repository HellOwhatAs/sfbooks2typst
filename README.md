# sfbooks2typst

## Getting Started
1. Install [Rust](https://www.rust-lang.org/), [uv](https://github.com/astral-sh/uv), and [typst](https://typst.app/).

2. ```bash
   git clone https://github.com/HellOwhatAs/sfbooks2typst.git
   cd sfbooks2typst
   
   # output <title>-<author>.json
   uv run crawler.py

   # output <title>-<author>.epub
   uv run to_epub.py

   # compile to main.pdf
   typst c main.typ
   ```