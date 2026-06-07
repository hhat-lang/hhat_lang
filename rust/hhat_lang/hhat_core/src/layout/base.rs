//!
//! Base layouts for types to be used for MIR.
//!

use strum::IntoEnumIterator;
use std::collections::HashMap;
use crate::core::Arenable;
use crate::frontend::types::{Ty, TyArrayKind, TyPrimitive};
use crate::layout::adt::{ArrayLayout, EnumLayout, StructLayout};
use crate::layout::arch::Arch;
use crate::layout::primitives::PrimitiveLayout;


#[derive(Clone, Debug)]
pub enum TypeLayout {
    Primitive(PrimitiveLayout, MemoryRegion),
    Struct(StructLayout, MemoryRegion),
    Enum(EnumLayout, MemoryRegion),
    Array(ArrayLayout, MemoryRegion),
}

impl TypeLayout {
    pub fn size(&self) -> u32 {
        match self {
            TypeLayout::Primitive(layout, _) => layout.size,
            TypeLayout::Struct(layout, _) => layout.size,
            TypeLayout::Enum(layout, _) => layout.size,
            TypeLayout::Array(layout, _) => layout.size,
        }
    }

    pub fn align(&self) -> u32 {
        match self {
            TypeLayout::Primitive(layout, _) => layout.align,
            TypeLayout::Struct(layout, _) => layout.align,
            TypeLayout::Enum(layout, _) => layout.align,
            TypeLayout::Array(layout, _) => layout.align,
        }
    }

    pub fn set_mem_region(&mut self, mem_region: MemoryRegion) {
        match self {
            TypeLayout::Primitive(_, mr)
            | TypeLayout::Struct(_, mr)
            | TypeLayout::Enum(_, mr)
            | TypeLayout::Array(_, mr) => *mr = mem_region
        }
    }
}

impl Arenable for TypeLayout {}


/// Where to store data: global scope, stack or heap.
///
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum MemoryRegion {
    GlobalScope,
    Stack,
    Heap,
}

impl MemoryRegion {
    pub fn default(ty: &Ty) -> Self {
        match ty {
            Ty::Array(a) if a.kind == TyArrayKind::Dynamic => MemoryRegion::Heap,
            _ => MemoryRegion::Stack,
        }
    }
}


pub struct LayoutCache {
    arch: Arch,
    cache: HashMap<Ty, TypeLayout>
}

impl LayoutCache {
    pub fn new(arch: Arch) -> Self {
        Self {
            arch,
            cache: HashMap::new(),
        }
    }

    pub fn initialize(&mut self, arch: Option<Arch>) {
        let _ = TyPrimitive::iter()
            .map(|v| {
                let _ = self.insert_layout(&Ty::Primitive(v), &arch);
            }).collect::<Vec<()>>();
    }

    pub fn has(&self, ty: &Ty) -> bool {
        self.cache.contains_key(ty)
    }

    pub fn insert_layout(&mut self, ty: &Ty, arch: &Option<Arch>) -> Option<TypeLayout> {
        match ty.clone() {
            Ty::Primitive(p) => self.cache.insert(
                ty.clone(),
                TypeLayout::Primitive(
                    PrimitiveLayout::layout(&p, arch.clone()),
                    MemoryRegion::default(&ty)
                )
            ),
            Ty::Struct(s) => {
                let _ = s.iter().map(|(_sid, t)| {
                    if !self.has(t) {
                        match t {
                            Ty::Primitive(_)
                            | Ty::Struct(_)
                            | Ty::Enum(_)
                            | Ty::Array(_) => self.insert_layout(&t, &arch),
                        };
                    }
                });
                let struct_layout = StructLayout::layout(&s, self);
                self.cache.insert(
                    ty.clone(),
                    TypeLayout::Struct(
                        struct_layout,
                        MemoryRegion::default(&ty),
                    )
                )
            },
            Ty::Enum(_e) => { todo!() },
            Ty::Array(_a) => { todo!() },
        }
    }

    pub fn layout_of(&mut self, ty: &Ty) -> TypeLayout {
        match self.cache.get(&ty) {
            Some(t) => t.clone(),
            None => panic!("layout of type {:?} not found.", ty),
        }
    }
}
