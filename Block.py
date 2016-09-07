#!/usr/bin/env python

import NAND;
from Page import Page;

class Block:
	FREE = 0;
	INUSE = 1;
	USED = 2;
	GC = 3;

	def __init__(self, id):
		self.id = id;
		self.erase();
		self.region;

	def erase(self):
		self.offset = 0;
		self.status = Block.FREE;
		self.lpns = [Page.INVALID for i in range(NAND.PAGES_PER_BLOCK)];
		self.valid_pages = 0;
		self.last_accessed = 0;
		self.region = 0;

	def dump(self, include_lpns = False):
		print "Block id=%d, offset=%d, status=%d," % \
			(self.id, self.offset, self.status),

		valid_pages = \
			NAND.PAGES_PER_BLOCK - sum([l == Page.INVALID for l in self.lpns]);

		if include_lpns:
			print "valid=%d," % valid_pages, "lpns=", self.lpns;
		else:
			print "valid=%d" % valid_pages;
