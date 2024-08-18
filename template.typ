#let project(title: "", authors: (), logo: none, body) = {
  // Set the document's basic properties.
  set document(author: authors, title: title)
  set page(paper: "a5")
  set text(font: "Noto Serif CJK SC", lang: "zh")
  // set heading(numbering: "1.")
  show heading.where(level: 1): it => [
    #pagebreak(weak: true)
    #align(center, pad(y: 1.5em, it))
  ]
  show heading.where(level: 2): it => pad(y: 1.5em, it)
  show heading: it => {
    if it.level > 2 {
      parbreak()
      fake-italic(it.body)
    } else {
      it
    }
  }

  // Title page.
  // The page can contain a logo if you pass one with `logo: "logo.png"`.
  v(0.6fr)
  if logo != none {
    align(right, image(logo, width: 26%))
  }
  v(9.6fr)

  text(2em, weight: 700, title)

  // Author information.
  pad(
    top: 0.7em,
    right: 20%,
    grid(
      columns: (1fr,) * calc.min(3, authors.len()),
      gutter: 1em,
      ..authors.map(author => align(start, strong(author))),
    ),
  )

  v(2.4fr)
  pagebreak()


  // Table of contents.
  outline(depth: 2, indent: 1.5em)
  pagebreak()


  // Main body.
  set par(justify: true)

  set page(numbering: "1", number-align: center)
  counter(page).update(1)

  body
}