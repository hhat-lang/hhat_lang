//!
//! Quantum memory layout for quantum data.
//!
//! Kept fully apart from the classical layout (`base`, `adt`, `primitives`):
//! the classical side lays data out in bytes (size, alignment, memory region),
//! while here we only count qubits, derived straight from the frontend type
//! [`crate::frontend::types::Ty`] so the classical layout never carries quantum
//! information.
//!
//! Split by concern:
//!   - [`layout`]: the quantum layout definitions (primitive/struct/enum);
//!   - [`cache`]: the permanent store that lays each quantum type out once.
//!
//! The quantum instructions and the quantum program live in the
//! [`crate::program`] module, since `layout` is only for laying out types.
//!

pub mod layout;
pub mod cache;

pub use layout::{
    QuantumEnumLayout, QuantumLayout, QuantumMemberLayout, QuantumPrimitiveLayout,
    QuantumStructLayout,
};
pub use cache::QuantumLayoutCache;
