// Utils for perfect hash function generation, naming scopes for
// identifiers such as variables, types and functions

use std::collections::HashSet;

//---------------------------
// NAME & NAMESPACE SECTION
//---------------------------

#[derive(Debug, Clone, Eq, PartialEq, Hash)]
pub struct FullName {
    namespace: Vec<String>,
    name: String,
}

//--------------------------------------------
// CONSTANTS FOR PERFECT HASH FUNCTION LOGIC
//--------------------------------------------

const PHF_A_LIMIT: u64 = 1_000_000;
const PHF_R_LIMIT: u32 = 37;
const PRIME_CONVERTER: u64 = 257;

/// transform string into u64 according to the formula
/// `value = value as u64 * PRIME_CONVERTER + char as u64`
/// where `value` is iterated over each of the chars
/// contained in the string
pub fn str_to_int(s: &String) -> u64 {
    let mut value: u64 = 0;

    for ch in s.chars() {
        value = value.wrapping_mul(PRIME_CONVERTER).wrapping_add(ch as u64);
    }

    value
}

/// Generates an u64 number to serve as the hash number for the given string
pub fn get_hash(s: &String, a: u64, r: u32, n: u64) -> u64 {
    let x: u64 = str_to_int(s);
    let product: u64 = x.wrapping_mul(a);
    let mixed: u64 = product ^ (product >> r);
    mixed % n
}

/// Finds the perfect hash ([PHF wiki](https://en.wikipedia.org/wiki/Perfect_hash_function)
/// and [PHF paper](https://cmph.sourceforge.net/papers/esa09.pdf)) parameters `a` and `r`
/// for a given array of strings
pub fn find_phf_params(strs: Vec<String>) -> Option<(u64, u32)> {
    let n: u64 = strs.len() as u64;

    for a in 1..PHF_A_LIMIT {
        for r in 0..PHF_R_LIMIT {
            let mut seen: HashSet<u64> = HashSet::new();
            let mut collision: bool = false;

            for s in &strs {
                let h: u64 = get_hash(s, a, r, n);

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
pub fn gen_phf(
    values: Vec<String>,
    vec_size: usize,
) -> Option<(Vec<Option<String>>, u64, u32)> {
    let n: u64 = values.len() as u64;

    // check whether the array length `n` is equal `N`
    if n as usize != vec_size {
        panic!(
            "Types list provided to the IRa types definition stack must be of a \
            fixed-sized as the constant N, i.e. the total number of strings parsed."
        )
    }

    match find_phf_params(values.clone()) {
        Some((a, r)) => {
            let mut mapping: Vec<Option<String>> = Vec::with_capacity(n as usize);

            for s in &values {
                let idx: usize = get_hash(s, a, r, n) as usize;
                mapping[idx] = Some(s.clone());
            }
            Some((mapping, a, r))
        }

        None => None,
    }
}
