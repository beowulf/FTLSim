#!/usr/bin/env python

import NAND;
from Trace import *;

clock = 0;
elapsed = 0;

requests_read = 0;
requests_write = 0;
requests_pages_read = 0;
requests_pages_write = 0;

pages_read = 0;
pages_written = 0;
pages_migrated = 0;
pages_skipped = 0;
pages_overwritten = 0;

blocks_erased = 0;
blocks_erased_backup = 0;

pages_backup = 0;

def print_stats():
	if requests_pages_write != 0:
		WAF = (float(pages_written) / float(requests_pages_write));
	else:
		WAF = 0.0;

	template = [
		[2, 3, 1, "Clock",		clock],
		[1, 3, 1, "Elapsed",	elapsed / 1000000],
		[2, 3, 0, ""],
		[2, 3, 0, "Request"],
		[2, 3, 1, "Read",		requests_read],
		[2, 3, 1, "Write",		requests_write],
		[2, 3, 1, "PagesRead",	requests_pages_read],
		[2, 3, 1, "PagesWrite",	requests_pages_write],
		[2, 3, 0, ""],
		[2, 3, 0, "Pages"],
		[2, 3, 1, "Read",		pages_read],
		[2, 3, 1, "Written",	pages_written],
		[2, 3, 1, "Migrated",	pages_migrated],
		[2, 3, 1, "Overwritten",pages_overwritten],
		[2, 3, 1, "Backup",		pages_backup],
		[2, 3, 1, "Skipped",	pages_skipped],
		[2, 3, 0, ""],
		[2, 3, 0, "Blocks"],
		[1, 2, 1, "Erased",		blocks_erased],
		[2, 3, 1, "Data",		(blocks_erased - blocks_erased_backup)],
		[2, 3, 1, "Backup",		blocks_erased_backup],
		[2, 3, 0, ""],
		[0, 3, 1, "WAF",		WAF],
	];

	for i, e in enumerate(template):
		if e[1] <= trace_level():	# Print entry comment
			trace("%02d:" % i, level = 4, newline = False);
			if e[2] == 0:
				trace(e[3], level = e[0]);
				continue;

			indent = " " * (12 - len(e[3]));
			trace("%s%s:" % (indent, e[3]), newline = False);

		if len(e) >= 5:
			trace(e[4], level = e[0]);


def reset():
	global clock;
	global elapsed;

	global requests_read;
	global requests_write;
	global requests_pages_read;
	global requests_pages_write;

	global pages_read;
	global pages_written;
	global pages_migrated;
	global pages_skipped;
	global pages_overwritten;

	global blocks_erased;
	global blocks_erased_backup;

	global pages_backup;

	clock = 0;
	elapsed = 0;

	requests_read = 0;
	requests_write = 0;
	requests_pages_read = 0;
	requests_pages_write = 0;

	pages_read = 0;
	pages_written = 0;
	pages_migrated = 0;
	pages_overwritten = 0;
	pages_skipped = 0;

	blocks_erased = 0;
	blocks_erased_backup = 0;

	pages_backup = 0;


def add_time(rw, target):
	global elapsed;
	if rw == 'R':
		if NAND.is_lsb(target):
			elapsed += NAND.US_READ_LSB;
		else:
			elapsed += NAND.US_READ_MSB;
	elif rw == 'W':
		if NAND.is_lsb(target):
			elapsed += NAND.US_WRITE_LSB;
		else:
			elapsed += NAND.US_WRITE_MSB;
	elif rw == 'E':
		elapsed += NAND.US_ERASE_BLOCK;


if __name__ == "__main__":
	clock = 10;
	trace_init(1, None);
	print_stats();
