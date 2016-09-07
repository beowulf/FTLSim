#!/usr/bin/env python

import NAND;
import Statistics;

from Page import Page;
from Block import Block;

import FTL;

class DAC(FTL.FTL):
	name = "DAC";
	REGIONS = 4;
	SYNC_GC_THRESHOLD = 1;

	def __init__(self, args, blocks):
		FTL.FTL.__init__(self, args, blocks);

		for k,v in args.items():
			if k == "regions":
				DAC.REGIONS = v;

		self.update_blocks = [None for i in range(self.REGIONS)];

	# Process read requests
	def process_read(self, lpn, lpns):
		if self.l2p[lpn] == Page.INVALID:
			return False;
		ppn = self.l2p[lpn];
		self.read_page(ppn);

		return True;


	def reclaim_block(self, victim = None):
		if victim == None:
			victim = self.select_victim_block();
		region = max(victim.region - 1, 0);

		# Copy valid pages
		victim_lpns = [l for l in victim.lpns if l != Page.INVALID];
		for lpn in victim.lpns:
			if lpn == Page.INVALID: continue;

			(block, offset) = self.get_update_ppn(region);
			self.backup_lsb_page(block, offset, lpn, victim_lpns, in_reclaim = True);

			self.migrate_page(self.l2p[lpn], block, offset);
			self.update_mapping(lpn, block, offset);

		self.erase_block(victim);
		self.free_blocks.append(victim);


	def get_update_ppn(self, region):
		update_block = self.update_blocks[region];

		if update_block == None:
			update_block = self.update_blocks[region] = self.allocate_block();
			update_block.region = region;

		(block, offset) = (update_block, update_block.offset);
		update_block.offset += 1;

		if update_block.offset == NAND.PAGES_PER_BLOCK:
			update_block.status = Block.USED;
			self.update_blocks[region] = None;

		return (block, offset);


	# Process write request
	def process_write(self, lpn, lpns):
		if self.l2p[lpn] == Page.INVALID:
			region = 0;
			(block, offset) = self.get_update_ppn(0);
		else:
			(old_block_id, old_offset) = NAND.from_ppn(self.l2p[lpn]);
			old_block = self.blocks[old_block_id];
			region = min(old_block.region + 1, self.REGIONS - 1);
			(block, offset) = self.get_update_ppn(region);

		# Backup LSB page if necessary
		self.backup_lsb_page(block, offset, lpn, lpns);

		self.write_page(block, offset);
		self.update_mapping(lpn, block, offset);

		while len(self.free_blocks) <= self.SYNC_GC_THRESHOLD:
			self.reclaim_block();
