use crate::core::ArenaIndexHolder;
use std::fmt::Debug;
use std::slice::Iter;
use crate::SymbolId;
use strum::IntoEnumIterator;
use strum_macros::EnumIter;


/// Define all available types.
///
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum Ty {
    Primitive(TyPrimitive),
    Struct(TyStruct),
    Enum(TyEnum),
    Array(TyArray),
}

/// Define primitive types.
///
#[derive(Clone, Debug, PartialEq, Eq, Hash, EnumIter)]
pub enum TyPrimitive {
    // Classical
    Bool,
    U32,
    U64,
    I32,
    I64,
    F32,
    F64,
    C64,
    C128,
    String,
    // Quantum
    QBool,
    QU2,
    QU3,
    QU4,
    QU8,
}

/// Define struct type.
///
/// Ex:
/// ```text
/// type smt { m1:ty1, m2:ty2 }
/// type @smt { @m1:@ty1, @m2:@ty2, m3:ty3 }
/// ```
///
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct TyStruct {
    pub name: SymbolId,
    pub members: Vec<(SymbolId, Ty)>,
    locked: bool,
}

impl TyStruct {
    pub fn new(name: &SymbolId) -> Self {
        TyStruct {
            name: name.clone(),
            members: Vec::new(),
            locked: false,
        }
    }

    pub fn add_member(&mut self, name: &SymbolId, ty: Ty) {
        match self.locked {
            false => {
                if !self.name.is_quantum() && name.is_quantum() {
                    panic!(
                        "cannot add quantum member {:?} ({:?}) to a classical struct {:?}.",
                        name, ty, self.name
                    )
                } else {
                    self.members.push((name.clone(), ty))
                }
            },
            true => panic!(
                "cannot add more members ({:?}, {:?}) to struct; it's already locked in",
                name, ty
            ),
        }
    }

    pub fn done(&mut self) {
        self.locked = true
    }

    pub fn is_locked(&self) -> bool {
        self.locked
    }

    pub fn iter(&'_ self) -> Iter<'_, (SymbolId, Ty)> {
        self.members.iter()
    }
}

/// Define enum type.
///
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct TyEnum {
    pub name: SymbolId,
    pub variants: Vec<TyVariants>,
    locked: bool,
}

impl TyEnum {
    pub fn new(name: &SymbolId) -> Self {
        TyEnum {
            name: name.clone(),
            variants: Vec::new(),
            locked: false,
        }
    }

    pub fn add_variant(&mut self, name: &SymbolId, member: Option<TyStruct>) {
        match (self.locked, member) {
            (false, Some(x)) => {
                // tagged, struct
                self.variants.push(TyVariants::Tagged(name.clone(), x))
            }
            (false, None) => {
                // named, labeled value
                // warning:
                //     this will cause overflow for enums with more than 32 elements
                //
                // todo: rethink it, decide whether it's worth keeping
                //  it small to enable logical operations or not.
                let variant_value = 2u32.pow(self.variants.len() as u32);
                self.variants
                    .push(TyVariants::Named(name.clone(), variant_value))
            },
            (true, x) => panic!(
                "cannot add more variants ({:?}, {:?}) to enum; it's already locked in",
                name, x
            ),
        }
    }

    pub fn done(&mut self) {
        self.locked = true
    }

    pub fn is_locked(&self) -> bool {
        self.locked
    }

    pub fn iter(&'_ self) -> Iter<'_, TyVariants> {
        self.variants.iter()
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum TyVariants {
    Named(SymbolId, u32),
    Tagged(SymbolId, TyStruct),
}

impl TyVariants {
    pub fn name(&self) -> &SymbolId {
        match self {
            TyVariants::Named(a, _) => a,
            TyVariants::Tagged(a, _) => a,
        }
    }
}

impl TyPrimitive {
    pub fn is_quantum(&self) -> bool {
        matches!(
            self,
            TyPrimitive::QBool
                | TyPrimitive::QU2
                | TyPrimitive::QU3
                | TyPrimitive::QU4
                | TyPrimitive::QU8
        )
    }

    pub fn quantum_width(&self) -> Option<u32> {
        match self {
            TyPrimitive::QBool => Some(1),
            TyPrimitive::QU2 => Some(2),
            TyPrimitive::QU3 => Some(3),
            TyPrimitive::QU4 => Some(4),
            TyPrimitive::QU8 => Some(8),
            _ => None,
        }
    }
}

impl TyStruct {
    pub fn is_quantum(&self) -> bool {
        self.name.is_quantum()
    }
}

impl TyEnum {
    pub fn is_quantum(&self) -> bool {
        self.name.is_quantum()
    }
}

impl Ty {
    pub fn is_quantum(&self) -> bool {
        match self {
            Ty::Primitive(p) => p.is_quantum(),
            Ty::Struct(s) => s.is_quantum(),
            Ty::Enum(e) => e.is_quantum(),
            Ty::Array(a) => a.element.is_quantum(),
        }
    }
}

/// Define array type (static or dynamic/vector-like).
///
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct TyArray {
    pub element: Box<Ty>,
    pub kind: TyArrayKind,
}

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum TyArrayKind {
    /// Compile-time known length. Stored inline.
    Static(u32),
    /// Runtime length. Stored as a fat pointer (data, len, capacity).
    Dynamic,
}

impl TyArray {
    pub fn new_static(element: Ty, length: u32) -> Self {
        TyArray {
            element: Box::new(element),
            kind: TyArrayKind::Static(length),
        }
    }

    pub fn new_dynamic(element: Ty) -> Self {
        TyArray {
            element: Box::new(element),
            kind: TyArrayKind::Dynamic,
        }
    }
}
