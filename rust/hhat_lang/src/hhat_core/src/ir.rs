// This file holds everything related to the intermediate representation (IR)
// part of H-hat.

use crate::data_impl::TypeDataIRa;
use std::collections::HashSet;

/// Identifier to hold variable, types, function names
pub struct Identifier {
    pub name: String,
    // todo: implement the rest
}

//----------------------------
//            IR
//----------------------------

/// Where types are defined and allocated for the IRa
pub struct TypesDef<T, const N: usize>
where
    T: TypeDataIRa,
{
    data: [Option<T>; N],
    types_list: [Option<String>; N],
    a_value: u64,
    r_value: u32,
}

impl<T, const N: usize> TypesDef<T, N> {
    /// Defining some constants for the PHF
    const A_LIMIT: u64 = 1_000_000;
    const R_LIMIT: u32 = 37;

    /// Generates an u64 number for the given string
    fn str_to_int(&mut self, s: &str) -> u64 {
        let base: u64 = 257;
        let mut value: u64 = 0;
        for ch in s.chars() {
            value = value.wrapping_mul(base).wrapping_add(ch as u64);
        }
        value
    }

    /// Generates an u64 number to serve as the hash number for the given string
    fn hash_func(&mut self, s: &str, a: u64, r: u32, n: u64) -> u64 {
        let x: u64 = self.str_to_int(s);
        let product: u64 = x.wrapping_mul(a);
        let mixed: u64 = product ^ (product >> r);
        mixed % n
    }

    /// Finds the perfect hash ([PHF wiki](https://en.wikipedia.org/wiki/Perfect_hash_function)
    /// and [PHF paper](https://cmph.sourceforge.net/papers/esa09.pdf)) parameters `a` and `r`
    /// for a given array of strings
    fn find_perfect_hash_params(&mut self, strs: &[String]) -> Option<(u64, u32)> {
        let n: u64 = strs.len() as u64;

        for a in 1..Self::A_LIMIT {
            for r in 0..Self::R_LIMIT {
                let mut seen: HashSet<u64> = HashSet::new();
                let mut collision: bool = false;
                for s in &strs {
                    let h: u64 = self.hash_func(s, a, r, n);
                    if !seen.insert(h) {
                        collision = true;
                        break;
                    }
                }
                if !collision {
                    return Some((a, r));
                }
            }
        }
        None
    }

    /// Generates the perfect hash results, returning tuple with a vector where the element
    /// is the string and the index is the actual result we want (as an u64 number), the
    /// `a` value as u64 number, used to retrieve the hash whenever needed, and the `r`
    /// value as u32 number, also used to retrieve the hash for the string
    fn gen_perfect_hash(&mut self, values: &[String]) -> Option<([Option<String>; N], u64, u32)> {
        let n: u64 = values.len() as u64;

        // check whether `n` is compatible with `N`
        if n as usize != N {
            panic!(
                "Types list provided to the IRa types definition stack must be of a \
                 fixed-sized as the constant N, i.e. the total number of types parsed."
            )
        }

        match self.find_perfect_hash_params(values) {
            Some((a, r)) => {
                let mut mapping: Vec<Option<String>> = vec![None; n as usize];
                for s in &values {
                    let idx: usize = self.hash_func(s, a, r, n) as usize;
                    mapping[idx] = Some(s.clone());
                }
                // at this point, it is guaranteed that mapping will have the length equals
                // to N, so no risk* to unwrap it
                let array_mapping: [Option<String>; N] = mapping.try_into().unwrap();
                (array_mapping, a, r)
            }
            None => None,
        }
    }

    pub fn new<const N: usize>() -> TypesDef<T, N>
    where
        T: TypeDataIRa,
    {
        TypesDef {
            data: [None; N],
            types_list: [None; N],
            a_value: 0,
            r_value: 0,
        }
    }

    pub fn push(&mut self, values: &[String], data: T)
    where
        T: TypeDataIRa,
    {
        match self.gen_perfect_hash(values) {
            Some((m, a, r)) => {
                self.types_list = m;
                self.a_value = a;
                self.r_value = r;
                // todo: implement the self.data ([Option<T>; N], where T implements TypeDataIRa)
            }
            None => {}
        }
    }
}

/// Intermediate representation (IR) version alpha, to be
/// evaluated by the interpreter (maybe JIT compiler?)
pub trait IRa {}
