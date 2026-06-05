//! 
//! Layouts are mostly to be used to transform HIR types into MIR types and be ready to
//! be converted into Cranelift types.
//! 
//! Here you may find information regarding architecture (32 and 64 bits), primitives 
//! and algebraic data types, as well as base layout definitions for those types. 
//! 


pub mod arch;
pub mod primitives;
mod adt;
mod base;
pub mod quantum;
