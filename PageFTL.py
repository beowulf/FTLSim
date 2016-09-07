#!/usr/bin/env python

import NAND;
import Statistics;

from Block import Block;
from Page import Page;
from FTL import FTL;


class PageFTL(FTL):
	name = "PageFTL";
	SYNC_GC_THRESHOLD = 1;

	def __init__(self, args, blocks):
		FTL.__init__(self, args, blocks);
		self.update_block = None;


	# Process read requests
	def process_read(self, lpn, lpns):
		if self.l2p[lpn] == Page.INVALID: return False;

		ppn = self.l2p[lpn];
		self.read_page(ppn);

		return True;


	def reclaim_block(self, victim = None):
		if victim == None:
			victim = self.select_victim_block();

		# Copy valid pages
		victim_lpns = [l for l in victim.lpns if l != Page.INVALID];
		for lpn in victim.lpns:
			if lpn == Page.INVALID: continue;

			(block, offset) = self.get_update_ppn();
			self.backup_lsb_page(block, offset, lpn, victim_lpns, in_reclaim = True);

			self.migrate_page(self.l2p[lpn], block, offset);
			self.update_mapping(lpn, block, offset);

		self.erase_block(victim);
		self.free_blocks.append(victim);


	def get_update_ppn(self):
		if self.update_block == None:
			self.update_block = self.allocate_block();

		update_block = self.update_block;

		(block, offset) = (update_block, update_block.offset);
		update_block.offset += 1;

		if update_block.offset == NAND.PAGES_PER_BLOCK:
			update_block.status = Block.USED;
			self.update_block = None;
		return (block, offset);


	# Process write requests
	def process_write(self, lpn, lpns):
		(block, offset) = self.get_update_ppn();

		# Backup LSB page if necessary
		self.backup_lsb_page(block, offset, lpn, lpns);

		self.write_page(block, offset);
		self.update_mapping(lpn, block, offset);

		while len(self.free_blocks) <= self.SYNC_GC_THRESHOLD:
			self.reclaim_block();
