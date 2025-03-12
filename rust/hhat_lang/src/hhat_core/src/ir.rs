// This file holds everything related to the intermediate representation (IR)
// part of H-hat.

use crate::data::CodeInstr;


/// Identifier to hold variable, types, function names
pub struct Identifier {
    pub name: String,
    // todo: implement the rest
}


/// Classical and quantum instructions data holder
pub struct Instructions<'a> {
    data: Vec<dyn CodeInstr<'a>>,
}

/// Intermediate representation (IR) version alpha, to be
/// evaluated by the interpreter (maybe JIT compiler?)
pub trait IRa {
}

