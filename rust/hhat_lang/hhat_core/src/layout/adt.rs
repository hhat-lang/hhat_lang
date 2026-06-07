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
        let mut members: Vec<MemberLayout> = Vec::with_capacity(
            ty.members.iter().filter(|(field_sid, _ty)| !field_sid.is_quantum()).count()
        );
        let _ = ty.iter().map(|(s, t)| {
            let tmp_layout: TypeLayout = layout_cache.layout_of(t);
            let tmp_size: u32 = tmp_layout.size();

            if tmp_size > 0 {  // quantum fields do not contribute for struct size
                let tmp_align: u32 = tmp_layout.align();
                struct_offset = StructLayout::align_layout(struct_offset, tmp_align);

                //
                // struct_size += prev_size.abs_diff(tmp_size);  // add padding
                // prev_size = tmp_size;
                // // align should be 1, 4, 8, so it's safe to unwrap
                // struct_align = struct_align.checked_next_multiple_of(tmp_align).unwrap();
                // struct_offset += struct_align;

                members.push(
                    MemberLayout {
                        name: s.clone(),
                        offset: struct_offset,
                        layout: tmp_layout,
                    }
                );

                struct_offset += tmp_size;
                if tmp_align > struct_align { struct_align = tmp_align; }
            }

        }).collect::<Vec<()>>();  // I know for loop is more idiomatic, but I prefer map :>

        Self {
            size: StructLayout::align_layout(struct_offset, struct_align),
            align: struct_align,
            members,
        }
    }

    fn align_layout(offset: u32, align: u32) -> u32 {
        (offset + align - 1) & !(align - 1)
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



#[derive(Clone, Debug)]
pub struct ArrayLayout {
    pub size: u32,
    pub align: u32,

}

#[cfg(test)]
mod tests {
    use std::sync::Arc;
    use crate::frontend::types::{Ty, TyPrimitive, TyStruct};
    use crate::layout::adt::StructLayout;
    use crate::layout::arch::Arch;
    use crate::layout::base::LayoutCache;
    use crate::layout::primitives::PrimitiveLayout;
    use crate::SymbolId;

    #[test]
    fn check_classical_struct_layout() {
        let mut lcache = LayoutCache::new(Arch::get_arch64());
        lcache.initialize(Some(Arch::get_arch64()));

        // define struct1
        let struct1_name = SymbolId(1, false);
        let mut struct1_ty = TyStruct::new(&struct1_name);

        let struct1_field1 = TyPrimitive::U32;
        let struct1_field1_name = SymbolId(2, false);
        let struct1_field1_layout = PrimitiveLayout::layout(&struct1_field1, Some(Arch::get_arch64()));

        let struct1_field2 = TyPrimitive::F64;
        let struct1_field2_name = SymbolId(3, false);
        let struct1_field2_layout = PrimitiveLayout::layout(&struct1_field2, Some(Arch::get_arch64()));

        struct1_ty.add_member(&struct1_field1_name, Ty::Primitive(struct1_field1));
        struct1_ty.add_member(&struct1_field2_name, Ty::Primitive(struct1_field2));

        lcache.insert_layout(&Ty::Struct(struct1_ty.clone()), &Some(Arch::get_arch64()));

        let struct1_layout = lcache.layout_of(&Ty::Struct(struct1_ty));

        println!("struct layout: {:?}", struct1_layout);
        assert_eq!(struct1_layout.size(), 16);
        assert_eq!(struct1_layout.align(), 8);

        // define struct2
        let struct2_name = SymbolId(4, false);
        let mut struct2_ty = TyStruct::new(&struct2_name);

        let struct2_field1 = TyPrimitive::U32;
        let struct2_field1_name = SymbolId(5, false);
        let struct2_field1_layout = PrimitiveLayout::layout(&struct2_field1, Some(Arch::get_arch64()));

        let struct2_field2 = TyPrimitive::F64;
        let struct2_field2_name = SymbolId(6, false);
        let struct2_field2_layout = PrimitiveLayout::layout(&struct2_field2, Some(Arch::get_arch64()));

        let struct2_field3 = TyPrimitive::Bool;
        let struct2_field3_name = SymbolId(7, false);
        let struct2_field3_layout = PrimitiveLayout::layout(&struct2_field3, Some(Arch::get_arch64()));

        let struct2_field4 = TyPrimitive::Bool;
        let struct2_field4_name = SymbolId(8, false);
        let struct2_field4_layout = PrimitiveLayout::layout(&struct2_field4, Some(Arch::get_arch64()));

        struct2_ty.add_member(&struct2_field1_name, Ty::Primitive(struct2_field1));
        struct2_ty.add_member(&struct2_field2_name, Ty::Primitive(struct2_field2));
        struct2_ty.add_member(&struct2_field2_name, Ty::Primitive(struct2_field3));
        struct2_ty.add_member(&struct2_field2_name, Ty::Primitive(struct2_field4));

        lcache.insert_layout(&Ty::Struct(struct2_ty.clone()), &Some(Arch::get_arch64()));

        let struct2_layout = lcache.layout_of(&Ty::Struct(struct2_ty));
        println!("struct layout: {:?}", struct2_layout);
        assert_eq!(struct2_layout.size(), 24);
        assert_eq!(struct2_layout.align(), 8);

    }


}
