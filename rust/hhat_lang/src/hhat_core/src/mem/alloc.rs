use crate::mem::defs::BlockSize;
use std::alloc::{alloc, dealloc, Layout};
use std::ptr::NonNull;

/// Allocate memory space for [`crate::mem::base::MemBlock`] for a given block size and alignment
/// and return a result with either the pointer ([`NonNull`]) or an error ([`AllocError`]).
pub fn alloc_memblock(block_size: BlockSize, align: usize) -> Result<NonNull<u8>, AllocError> {
    unsafe {
        let layout: Layout = match Layout::from_size_align(block_size, align) {
            Ok(layout) => layout,
            Err(_) => return Err(AllocError::ConstraintsNotSatisfied),
        };
        let ptr: *mut u8 = alloc(layout);
        if ptr.is_null() {
            Err(AllocError::NullPointer)
        } else {
            Ok(NonNull::new_unchecked(ptr))
        }
    }
}

pub fn free_memblock(
    block_size: BlockSize,
    align: usize,
    ptr: NonNull<u8>,
) -> Result<AllocSuccess, AllocError> {
    unsafe {
        let layout: Layout = match Layout::from_size_align(block_size, align) {
            Ok(layout) => layout,
            Err(_) => return Err(AllocError::ConstraintsNotSatisfied),
        };
        dealloc(ptr.as_ptr(), layout);
        Ok(AllocSuccess::MemoryFreed)
    }
}

/// Define allocation success
/// - `MemoryFreed`
pub enum AllocSuccess {
    MemoryFreed,
    PointerFreed,
}

/// Define allocation errors:
/// - `NotPowerOfTwo`
/// - `InvalidBlockSize`
/// - `InvalidAlignment`
/// - `ConstraintsNotSatisfied`
/// - `NotEnoughMemory`
/// - `NullPointer`
/// - `MemoryAlreadyFreed`
pub enum AllocError {
    NotPowerOfTwo,
    InvalidBlockSize,
    InvalidAlignment,
    ConstraintsNotSatisfied,
    NotEnoughMemory,
    NullPointer,
    MemoryAlreadyFreed,
}
