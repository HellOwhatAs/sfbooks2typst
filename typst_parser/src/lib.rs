use pyo3::prelude::*;
use lazy_static::lazy_static;
use std::collections::HashMap;

lazy_static! {
    static ref FuncCallRules: HashMap<String, (String, String)> = {
        maplit::hashmap! {
            "strike" => ("<del>", "</del>"),
            "highlight" => ("<mark>", "</mark>"),
            "overline" => ("<span style=\"text-decoration:overline;\">", "</span>"),
            "sub" => ("<sub>", "</sub>"),
            "super" => ("<sup>", "</sup>"),
            "underline" => ("<span style=\"text-decoration:underline;\">", "</span>"),
        }
        .into_iter()
        .map(|(k, (v1, v2))| (k.to_string(), (v1.to_string(), v2.to_string())))
        .collect::<HashMap<_, _>>()
    };
    static ref FuncCallTextRules: HashMap<String, (String, String)> = {
        maplit::hashmap! {
            "strike" => ("", ""),
            "highlight" => ("", ""),
            "overline" => ("", ""),
            "sub" => ("", ""),
            "super" => ("", ""),
            "underline" => ("", ""),
        }
        .into_iter()
        .map(|(k, (v1, v2))| (k.to_string(), (v1.to_string(), v2.to_string())))
        .collect::<HashMap<_, _>>()
    };
    static ref XmlEscapeDict: HashMap<char, &'static str> = {
        maplit::hashmap! {
            '&' => "&amp;",
            '<' => "&lt;",
            '>' => "&gt",
            '"' => "&quot;",
            '\'' => "&apos;",
            '\t' => "&emsp;",
            // '\n' => "<br>",
        }
    };
}

/// Escape xml characters.
#[pyfunction]
pub fn escape_xml_characters(s: &str) -> String {
    s.chars()
        .map(|c| {
            XmlEscapeDict
                .get(&c)
                .map(|s| s.to_string())
                .unwrap_or(c.to_string())
        })
        .reduce(|acc, e| acc + &e)
        .unwrap_or_else(|| String::new())
}

fn func(root: &typst_syntax::SyntaxNode, arr: &mut Vec<String>, rules: &HashMap<String, (String, String)>) {
    use typst_syntax::SyntaxKind::{FuncCall, Space, Str, Text};
    let s = root.text().to_string();
    match root.kind() {
        FuncCall => {
            let mut it = root.children();
            let func_name = it.next().unwrap();
            let func_args = it.next().unwrap();
            if let Some((pre, post)) = rules.get(func_name.text().as_str()) {
                arr.push(pre.to_string());
                func(func_args, arr, rules);
                arr.push(post.to_string());
            }
            return;
        }
        Text | Space => {
            arr.push(escape_xml_characters(&s));
        }
        Str => {
            arr.push(escape_xml_characters(
                &serde_json::from_str(&s).unwrap_or(s),
            ));
        }
        _ => {}
    }
    for child in root.children() {
        func(child, arr, rules);
    }
}

/// Convert typst code to xml code.
#[pyfunction]
pub fn typst2xml(src: String) -> PyResult<String> {
    let root: typst_syntax::SyntaxNode = typst_syntax::parse(&src);
    let mut arr = vec![];
    func(&root, &mut arr, &FuncCallRules);
    Ok(arr.join(""))
}

/// Convert typst code to text.
#[pyfunction]
pub fn typst2text(src: String) -> PyResult<String> {
    let root: typst_syntax::SyntaxNode = typst_syntax::parse(&src);
    let mut arr = vec![];
    func(&root, &mut arr, &FuncCallTextRules);
    Ok(arr.join(""))
}

/// A Python module implemented in Rust.
#[pymodule]
fn typst_parser(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(escape_xml_characters, m)?)?;
    m.add_function(wrap_pyfunction!(typst2xml, m)?)?;
    m.add_function(wrap_pyfunction!(typst2text, m)?)?;
    Ok(())
}
