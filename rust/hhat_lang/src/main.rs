#![allow(dead_code, unused)]

use std::collections::HashMap;
use peg;

mod ir;
mod parse;
mod passes;
mod backends;
mod runtime;
mod jit;
mod config;
mod toolchain;
mod semantics;
mod utils;

fn main() {
    let mut x: Vec<u32> = vec![0; 5];
    x[1] = 2;
    println!("{:?}", x);
    let y: [(&str, u32); 2] = [("a", 1), ("b", 2)];
    println!("valid {:?}", y);
    let z: HashMap<(String, u32), u32> = y.into_iter().map(|k| ((k.0.to_owned(), k.1.to_owned()), k.1.to_owned())).collect();
    println!("final {:?}", z);
    println!("get z[(\"b\", 2)] = {:?}", z.get(&(String::from("b"), 2)));
    println!("get z[(\"c\", 3)] = {:?}", z.get(&(String::from("c"), 3)));
    println!("{:?}", parse::parser::fn_program::start("[a b Ac x0]"));
    assert_eq!(parse::parser::fn_program::start("[a b Ac x0]"), Ok(vec!["a".to_owned(), "b".to_owned(), "Ac".to_owned(), "x0".to_owned()]));
}

