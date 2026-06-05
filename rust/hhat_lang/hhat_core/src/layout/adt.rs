//!
//! Composite algebraic data types for Cranelift framework forms.
//!

use crate::core::{ArenaIndexHolder, Arenable};
use crate::frontend::types::{TyEnum, TyStruct, TyVariants};
use crate::layout::base::{LayoutCache, TypeLayout};
use crate::SymbolId;

#[derive(Clone, Debug)]
pub struct StructLayout {
    pub size: u32,
    pub align: u32,
    pub members: Vec<MemberLayout>,
}

impl StructLayout {
    pub fn layout(ty: &TyStruct, layout_cache: &mut LayoutCache) -> Self {
        let mut struct_align: u32 = 1;
        let mut struct_size: u32 = 0;
        let mut struct_offset: u32 = 0;
        let mut prev_size: u32 = 0;
        let mut members: Vec<MemberLayout> = Vec::with_capacity(ty.members.len());
        for (s, t) in ty.iter() {
            let tmp_layout: TypeLayout = layout_cache.layout_of(t);
            let tmp_size: u32 = tmp_layout.size();
            let tmp_align: u32 = tmp_layout.align();

            if prev_size > 0 {
                struct_size += prev_size.abs_diff(tmp_size);  // add padding
            }
            prev_size = tmp_size;
            // Quantum members have no classical alignment.
            if tmp_align > 0 {
                struct_align = struct_align.checked_next_multiple_of(tmp_align).unwrap();
            }
            struct_offset += struct_align;
            members.push(MemberLayout {
                name: s.clone(),
                offset: struct_offset,
                layout: tmp_layout,
            })
        }

        Self {
            size: struct_size,
            align: struct_align,
            members,
        }
    }

    pub fn member_offset(&self, member_name: &SymbolId) -> Option<u32> {
        if let Some(_) = self.members.get(member_name.read() as usize) {
            Some(member_name.read())
        } else { None }
    }

    pub fn member(&self, member_name: &SymbolId) -> Option<&MemberLayout> {
        self.members.get(member_name.read() as usize)
    }

    pub fn get(&self, index: usize) -> Option<&MemberLayout> {
        self.members.get(index)
    }
}

impl Arenable for StructLayout {}


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

impl EnumLayout {
    pub fn layout(ty: &TyEnum, layout_cache: &mut LayoutCache) -> Self {
        let mut enum_size: u32 = 0;
        let mut enum_align: u32 = 1;
        let mut variants: Vec<VariantLayout> = Vec::with_capacity(ty.variants.len());
        let _ = ty.iter().map(|v| {
           match v {
               TyVariants::Named(sid, _) => {
                   variants.push(
                       VariantLayout {
                           name: sid.clone(),
                           payload: None,
                       }
                   );
               },
               TyVariants::Tagged(_sid, s) => {
                   let _ = s.iter().map(|(v_sid, ts)| {
                       let tmp_struct_layout = layout_cache.layout_of(ts);
                       let struct_layout: StructLayout = match tmp_struct_layout.clone() {
                           TypeLayout::Struct(sl, _) => {
                               sl
                           },
                           a => panic!("invalid variant entry layout ({:?}) for enums", a),
                       };
                       let tmp_struct_size = tmp_struct_layout.size();
                       let tmp_struct_align = tmp_struct_layout.align();

                       if tmp_struct_size > enum_size { enum_size = tmp_struct_size; }
                       if tmp_struct_align > enum_align { enum_align = tmp_struct_align; }
                       variants.push(
                           VariantLayout {
                               name: v_sid.clone(),
                               payload: Some(struct_layout)
                           }
                       )
                   }).collect::<Vec<()>>();
               },
           }
        }).collect::<Vec<()>>();

        Self {
            size: enum_size,
            align: enum_align,
            variants,
        }
    }

    pub fn variant_idx(&self, variant_name: &SymbolId) -> Option<u32> {
        if let Some(_) = self.variants.get(variant_name.read() as usize) {
            Some(variant_name.read())
        } else { None }
    }

    pub fn variant(&self, variant_name: &SymbolId) -> Option<&VariantLayout> {
        self.variants.get(variant_name.read() as usize)
    }

    pub fn get(&self, index: usize) -> Option<&VariantLayout> {
        self.variants.get(index)
    }
}

impl Arenable for EnumLayout {}


#[derive(Clone, Debug)]
pub struct VariantLayout {
    name: SymbolId,
    payload: Option<StructLayout>,
}


impl VariantLayout {
    pub fn name(&self) -> &SymbolId {
        &self.name
    }
}


#[derive(Clone, Debug)]
pub struct ArrayLayout {
    pub size: u32,
    pub align: u32,

}
