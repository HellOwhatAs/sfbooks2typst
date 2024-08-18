#import "template.typ": *

#let title = "恐吓小说网";
#let author = "幻影大厦";

#show: project.with(title: title, authors: (author,))

#let parse-input(src) = if src.starts-with("#[") and src.ends-with("]") {
  eval(src, mode: "markup")
} else { src }

#let data = json(title + "-" + author +".json")
#for (catalog_name, catalog) in data {
  heading(parse-input(catalog_name), level: 1);
  for (cpt_name, cpt_content) in catalog {
    heading(parse-input(cpt_name), level: 2);
    for p in cpt_content {
      par(parse-input(p))
    }
  }
}