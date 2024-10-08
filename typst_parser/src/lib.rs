use pyo3::prelude::*;
use lazy_static::lazy_static;
use std::collections::HashMap;

lazy_static! {
    static ref FuncCall_RULES: HashMap<String, (String, String)> = {
        let mut m = HashMap::new();
        m.insert(
            "strike".to_string(),
            ("<del>".to_string(), "</del>".to_string()),
        );
        m
    };
}

fn func(root: &typst_syntax::SyntaxNode, arr: &mut Vec<String>) {
    use typst_syntax::SyntaxKind::{FuncCall, Space, Text};
    let s = root.text().to_string();
    match root.kind() {
        FuncCall => {
            let mut it = root.children();
            let func_name = it.next().unwrap();
            let func_args = it.next().unwrap();
            if let Some((pre, post)) = FuncCall_RULES.get(func_name.text().as_str()) {
                arr.push(pre.to_string());
                func(func_args, arr);
                arr.push(post.to_string());
            }
            return;
        }
        Text | Space => {
            arr.push(s);
        }
        _ => {}
    }
    for child in root.children() {
        func(child, arr);
    }
}

/// Convert typst code to xml code.
#[pyfunction]
fn typst2xml(src: String) -> PyResult<String> {
    let root: typst_syntax::SyntaxNode = typst_syntax::parse(&src);
    let mut arr = vec![];
    func(&root, &mut arr);
    Ok(arr.join(""))
}

/// A Python module implemented in Rust.
#[pymodule]
fn typst_parser(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(typst2xml, m)?)?;
    Ok(())
}
