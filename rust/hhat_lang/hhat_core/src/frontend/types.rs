use crate::SymbolId;

/// Define all available types.
///
#[derive(Clone, Debug)]
pub enum Ty {
    Primitive(TyPrimitive),
    Struct(TyStruct),
    Enum(TyEnum),
    Array(TyArray),
}

/// Define primitive types.
///
#[derive(Clone, Debug)]
pub enum TyPrimitive {
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
}

/// Define struct type.
///
#[derive(Clone, Debug)]
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
            false => self.members.push((name.clone(), ty)),
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
}

/// Define enum type.
///
#[derive(Clone, Debug)]
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
}

#[derive(Clone, Debug)]
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

/// Define array type (static or dynamic/vector-like).
///
#[derive(Clone, Debug)]
pub struct TyArray {
    pub element: Box<Ty>,
    pub kind: TyArrayKind,
}

#[derive(Clone, Debug)]
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