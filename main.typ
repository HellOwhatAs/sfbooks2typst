#import "template.typ": *

#let title = "恐吓小说网";
#let author = "幻影大厦";

#show: project.with(title: title, authors: (author,), abstract: "世上有三种人最惹不起，第一种是无欲无求的人，第二种是不怕死的人，第三种则是“恐吓小说网”的「作者」。 成为“恐吓小说网”的作者后，绪方周围越来越多地出现了怪异事件。")

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