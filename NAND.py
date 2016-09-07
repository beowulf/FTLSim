#!/usr/bin/env python

PAGES_PER_BLOCK = 128;					# 1 MB block
SECTORS_PER_PAGE = 16;					# 8 KB page
PAGE_SIZE = 512 * SECTORS_PER_PAGE;

# Time in us for flash operations
US_READ_LSB = 80;
US_READ_MSB = 120;

US_WRITE_LSB = 500;
US_WRITE_MSB = 1500;

US_ERASE_BLOCK = 1500;

def is_lsb(ppn):
	if ppn == 0x7f:
		return False;
	elif ppn == 0 or ppn % 2 == 1:
		return True;
	return False;


def is_msb(ppn):
	return not is_lsb(ppn);


def get_paired_page(offset):
	if offset == 0:
		return 2;
	elif offset == 2:
		return 0;
	elif offset == 0x7d:
		return 0x7f;
	elif offset == 0x7f:
		return 0x7d;
	elif is_lsb(offset):
		return offset + 3;
	else:
		return offset - 3;


def from_ppn(ppn):
	block = ppn / PAGES_PER_BLOCK;
	page = ppn % PAGES_PER_BLOCK;
	return block, page;


def to_ppn(block, page):
	return block.id * PAGES_PER_BLOCK + page;


if __name__ == "__main__":
	for i in range(PAGES_PER_BLOCK):
		if is_lsb(i):
			print "L",
		else:
			print "M",
		print "%02x  %02x" % (i, get_paired_page(i));
