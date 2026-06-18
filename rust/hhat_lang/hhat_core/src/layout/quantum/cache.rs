//!
//! Caching of the quantum layouts.
//!
//! Laying out the quantum layout and storing it are different concerns: this
//! holds the permanent store so each quantum type is laid out once and reused
//! across every quantum variable in the program.
//!

use std::collections::HashMap;
use crate::frontend::types::Ty;
use crate::layout::quantum::layout::QuantumLayout;


/// Permanent store for quantum type layouts.
///
pub struct QuantumLayoutCache {
    cache: HashMap<Ty, QuantumLayout>,
}

#[allow(clippy::new_without_default)]
impl QuantumLayoutCache {
    pub fn new() -> Self {
        Self { cache: HashMap::new() }
    }

    pub fn has(&self, ty: &Ty) -> bool {
        self.cache.contains_key(ty)
    }

    /// Quantum layout for a type, building it on a miss and storing it.
    ///
    pub fn layout_of(&mut self, ty: &Ty) -> QuantumLayout {
        match self.cache.get(ty) {
            Some(q) => q.clone(),
            None => {
                let q = QuantumLayout::layout(ty);
                self.cache.insert(ty.clone(), q.clone());
                q
            }
        }
    }
}


#[cfg(test)]
mod tests {
    use crate::frontend::types::{Ty, TyPrimitive, TyStruct};
    use crate::layout::quantum::QuantumLayoutCache;
    use crate::SymbolId;

    /// Check the quantum layout cache stores layouts permanently and reuses them.
    ///
    #[test]
    fn check_quantum_layout_cache() {
        let bell_name = SymbolId(1, true);
        let mut bell_ty = TyStruct::new(&bell_name);
        bell_ty.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QBool));
        bell_ty.add_member(&SymbolId(3, true), Ty::Primitive(TyPrimitive::QBool));
        bell_ty.done();

        let mut qcache = QuantumLayoutCache::new();
        assert!(!qcache.has(&Ty::Struct(bell_ty.clone())));

        let first = qcache.layout_of(&Ty::Struct(bell_ty.clone()));
        assert_eq!(first.qubits(), 2);
        assert!(qcache.has(&Ty::Struct(bell_ty.clone())));

        // second lookup is served from the cache and matches
        let second = qcache.layout_of(&Ty::Struct(bell_ty));
        assert_eq!(second.qubits(), 2);
    }
}
