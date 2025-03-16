use std::ptr::NonNull;

use crate::mem::alloc::{alloc_memblock, free_memblock, AllocError, AllocSuccess};
use crate::mem::defs::{BlockSize, ALIGNMENT};

/// Define a memory block for stack or heap (or something else?)
pub struct MemBlock {
    ptr: NonNull<u8>,
    align: usize,
    size: BlockSize,
    is_freed: bool,
}

impl MemBlock {
    pub fn new(size: usize) -> Result<MemBlock, AllocError> {
        if size.is_power_of_two() {
            let ptr = alloc_memblock(size, ALIGNMENT);
            match ptr {
                Ok(ptr) => Ok(MemBlock {
                    ptr,
                    align: ALIGNMENT,
                    size,
                    is_freed: false,
                }),
                Err(err) => Err(err),
            }
        } else {
            return Err(AllocError::NotPowerOfTwo);
        }
    }

    pub fn get_size(&self) -> usize {
        self.size
    }

    pub fn get_ptr(&self) -> NonNull<u8> {
        self.ptr
    }

    pub fn as_ptr(&self) -> *const u8 {
        self.ptr.as_ptr()
    }

    pub fn free(&mut self) -> Result<AllocSuccess, AllocError> {
        if !self.is_freed {
            free_memblock(self.size, self.align, self.ptr)
        } else {
            Err(AllocError::MemoryAlreadyFreed)
        }
    }
}

/// Memory block error enum, with fields:
/// - `OutOfMemory`
/// - `PointerOverflow`
pub enum MemError {
    OutOfMemory,
    PointerOverflow,
}
