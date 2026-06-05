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
mod subcompilers;

fn main() {

}

