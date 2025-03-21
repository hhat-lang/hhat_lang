use std::ptr::write;

use crate::mem::alloc::AllocError;
use crate::mem::base::MemBlock;
use crate::mem::defs::{ALIGNMENT, MAX_MEMBLOCK_SIZE};

/// The actual stack memory container
///
/// It can hold several `StackPage`s according to what is needed.
///
/// `pages` contains the `StackPage` data, whereas `page_index` is
/// responsible to hold information on which page to find some data
pub struct StackMemory {
    pages: Vec<StackPage>,
    cur_page: isize,
}

impl StackMemory {
    pub fn new(&mut self, max_size: usize) -> Self {
        StackMemory {
            pages: {
                match max_size {
                    0 => Vec::new(),
                    _ => {
                        let mut v: Vec<StackPage> = Vec::with_capacity(max_size);
                        // create a stack page with max memory size
                        let page: StackPage = match StackPage::new(MAX_MEMBLOCK_SIZE) {
                            Ok(x) => x,
                            Err(x) => panic!(""),
                        };
                        v.push(page);
                        v
                    }
                }
            },
            cur_page: -1,
        }
    }

    /// When `StackMemory` needs to expand memory, a new page must be created.
    /// A page is a `StackPage`.
    pub fn new_page(&mut self, size: usize) -> Result<(), StackError> {
        match StackPage::new(size) {
            Ok(page) => {
                self.pages.push(page);
                let cur_page = self.cur_page;
                self.cur_page = cur_page + 1;
                Ok(())
            }
            Err(err) => Err(err),
        }
    }

    pub fn page_cursor(&mut self, page_num: isize) -> *const u16 {
        self.pages[page_num as usize].cursor()
    }

    pub fn push<T>(&mut self, data: T) {
        unsafe {
            todo!()
            // figure out how to get the offset for `data`
            // self.pages[-1].write(data, );
        }
    }

    pub fn pop(&mut self) -> Option<()> {
        todo!()
    }
}

/// Stack page memory
///
/// To create a new `StackPage`, use `StackPage::new(size)` where `size` must be power
/// of two, `usize` type and bounded to [`MAX_MEMBLOCK_SIZE`].
///
/// For now, the stack page can support pointers of size u16.
pub struct StackPage {
    memblock: MemBlock,
    cursor: *const u16,
    limit: *const u16,
}

impl StackPage {
    pub fn new(size: usize) -> Result<Self, StackError> {
        match MemBlock::new(size) {
            Ok(memblock) => Ok(StackPage {
                memblock,
                cursor: MAX_MEMBLOCK_SIZE as *const u16,
                limit: MAX_MEMBLOCK_SIZE as *const u16,
            }),
            Err(x) => match x {
                AllocError::ConstraintsNotSatisfied => Err(StackError::LayoutError),
                AllocError::InvalidAlignment => Err(StackError::InvalidAlignment),
                AllocError::InvalidBlockSize => Err(StackError::InvalidBlockSize),
                AllocError::MemoryAlreadyFreed => Err(StackError::MemoryAlreadyFreed),
                AllocError::NotEnoughMemory => Err(StackError::NotEnoughMemory),
                AllocError::NotPowerOfTwo => Err(StackError::SizeNotPowerOfTwo),
                AllocError::NullPointer => Err(StackError::NullPointer),
            },
        }
    }

    /// Makes available a space in the Stack's memory block of size `alloc_size` and
    /// returns a pointer to it.
    pub fn alloc(&mut self, alloc_size: usize) -> Result<*const u16, StackError> {
        let start_ptr = self.memblock.as_ptr() as usize;
        let cursor_ptr = self.cursor as usize;

        let next_ptr: usize = match cursor_ptr.checked_sub(alloc_size) {
            Some(ptr) => ptr & ALIGNMENT, // align to word boundary
            _ => return Err(StackError::NoNextPointer),
        };

        if next_ptr < start_ptr {
            Err(StackError::NotEnoughMemory)
        } else {
            self.cursor = next_ptr as *const u16;
            Ok(next_ptr as *const u16)
        }
    }

    /// write data to the stack page(?)
    pub unsafe fn write<T>(&mut self, data: T, offset: usize) -> *const T {
        let p = self.memblock.as_ptr().add(offset) as *mut T;
        write(p, data);
        p
    }

    /// To free the memory space given by the `ptr` pointer.
    pub unsafe fn free(&mut self, ptr: *const u16) {
        let _ = self.memblock.free();
    }

    pub fn cursor(&self) -> *const u16 {
        self.cursor
    }
}

/// Possible stack errors to communicate
pub enum StackError {
    InvalidBlockSize,
    InvalidAlignment,
    InvalidStackPage,
    LayoutError,
    MemoryAlreadyFreed,
    NoNextPointer,
    NotEnoughMemory,
    NullPointer,
    SizeNotPowerOfTwo,
}
