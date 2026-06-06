#![allow(dead_code, unused)]

use peg;
use std::collections::HashMap;

mod backends;
mod config;
mod ir;
mod jit;
mod parse;
mod passes;
mod runtime;
mod semantics;
mod subcompilers;
mod toolchain;
mod utils;

fn main() {}
