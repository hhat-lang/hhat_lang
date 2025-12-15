#![allow(dead_code, unused_attributes, unused_attributes, unused_variables)]

mod instr;
mod mem;
mod utils;
mod data;
//----------------------
// LET THE TESTS BEGIN
//----------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::mem::alloc::{free_memblock, AllocSuccess};
    use crate::mem::defs::MAX_MEMBLOCK_SIZE;
    use std::ptr::NonNull;

    /// Create small memory blocks with [`mem::alloc::alloc_memblock`] and [`mem::base::MemBlock`]
    #[test]
    fn create_memblock_small() {
        println!("Create memblock small:");

        let align: usize = 8;
        let block_size: usize = (1 << 4) as usize; // 16
        let block_ptr1 = mem::alloc::alloc_memblock(block_size, align);
        let block_ptr2 = mem::alloc::alloc_memblock(block_size, align);

        let ptr1: NonNull<u8> = match block_ptr1 {
            Ok(x) => {
                println!(
                    "  - allocated memory 1! {:} , {:}",
                    x.as_ptr() as u8,
                    x.addr()
                );
                x
            },
            Err(_) => {
                return assert!(false);
            }
        };

        let ptr2: NonNull<u8> = match block_ptr2 {
            Ok(x) => {
                println!(
                    "  - allocated memory 2! {:}, {:}",
                    x.as_ptr() as u8,
                    x.addr()
                );
                x
            },
            Err(_) => return assert!(false),
        };

        let mut memblock: mem::base::MemBlock = match mem::base::MemBlock::new(block_size) {
            Ok(x) => {
                assert_eq!(x.get_size(), block_size);
                {
                    println!("  - memblock ptr is equal to {:}", block_size + 16);
                    x
                }
            }
            Err(_) => {
                return assert!(false);
            }
        };

        match free_memblock(block_size, align, ptr1) {
            Ok(AllocSuccess::MemoryFreed) => assert!(true),
            Ok(other) => assert!(false),
            Err(_) => assert!(false),
        };

        match free_memblock(block_size, align, ptr2) {
            Ok(AllocSuccess::MemoryFreed) => assert!(true),
            Ok(other) => assert!(false),
            Err(_) => assert!(false),
        };

        match memblock.free() {
            Ok(AllocSuccess::MemoryFreed) => assert!(true),
            Ok(other) => assert!(false),
            Err(_) => assert!(false),
        }
    }

    /// Create the largest memory blocks enabled with [`mem::base::MemBlock`]
    #[test]
    fn create_memblock_large() {
        println!("Create memblock large:");

        assert!(MAX_MEMBLOCK_SIZE.is_power_of_two());

        let mut memblock: mem::base::MemBlock = match mem::base::MemBlock::new(MAX_MEMBLOCK_SIZE) {
            Ok(x) => {
                assert_eq!(x.get_size(), MAX_MEMBLOCK_SIZE);
                println!("memblock with the expected size {:}", MAX_MEMBLOCK_SIZE);
                x
            }
            Err(_) => {
                return assert!(false);
            }
        };

        let _ = memblock.free();
    }
}
