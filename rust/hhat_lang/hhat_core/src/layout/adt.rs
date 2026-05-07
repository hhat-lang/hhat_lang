//!
//! Composite algebraic data types for Cranelift framework forms.
//!

use crate::frontend::types::TyStruct;
use crate::layout::base::TypeLayout;
use crate::SymbolId;

#[derive(Clone, Debug)]
pub struct StructLayout {
    pub size: u32,
    pub align: u32,
    pub members: Vec<MemberLayout>,
}

impl StructLayout {
    pub fn get_layout(ty: &TyStruct) -> Self { todo!() }
}

/// Layout for struct members.
///
#[derive(Clone, Debug)]
pub struct MemberLayout {
    pub name: SymbolId,
    pub offset: u32,
    pub layout: TypeLayout,
}



#[derive(Clone, Debug)]
pub struct EnumLayout {
    pub size: u32,
    pub align: u32,
    pub variants: Vec<VariantLayout>,
}


#[derive(Clone, Debug)]
pub struct VariantLayout {

}


#[derive(Clone, Debug)]
pub struct ArrayLayout {
    pub size: u32,
    pub align: u32,

}