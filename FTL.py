#!/usr/bin/env python

import NAND;
import Statistics;

from Block import Block;
from Page import Page;

class FTL:
	def __init__(self, args, blocks):
		self.blocks = [Block(i) for i in range(blocks)];
		self.l2p = [Page.INVALID for i in range(blocks * NAND.PAGES_PER_BLOCK)];
		self.free_blocks = [b for b in self.blocks];
		self.backup_block = self.allocate_block();

		if "no_backup" in args:
			self.no_backup = args["no_backup"];
		else:
			self.no_backup = False;

		if "per_request" in args:
			self.per_request = args["per_request"];
		else:
			self.per_request = False;

		if "statistics_page" in args:
			self.statistics_page = args["statistics_page"];
		else:
			self.statistics_page = None;

		if "statistics_request" in args:
			self.statistics_request = args["statistics_request"];
		else:
			self.statistics_request = None;

	def read_page(self, ppn):
		Statistics.pages_read += 1;
		Statistics.add_time('R', ppn);


	def write_page(self, block, offset):
		ppn = NAND.to_ppn(block, offset);

		block.valid_pages += 1;
		block.last_accessed = Statistics.clock;

		Statistics.pages_written += 1;
		Statistics.add_time('W', ppn);


	def erase_block(self, block, backup_block = False):
		# print "Erase", block.id
		assert block.status == Block.USED or block.status == Block.GC;
		block.erase();

		Statistics.blocks_erased += 1;
		Statistics.add_time('E', block.id);

		if backup_block:
			Statistics.blocks_erased_backup += 1;


	def migrate_page(self, ppn, block, offset):
		self.read_page(ppn);
		self.write_page(block, offset);

		Statistics.pages_migrated += 1;


	def process(self, RW, lba, sector_count):
		# Get target LPNs
		page_start = lba / NAND.SECTORS_PER_PAGE;
		page_end = (lba + sector_count + NAND.SECTORS_PER_PAGE - 1) \
					/ NAND.SECTORS_PER_PAGE;

		lpns = range(page_start, page_end);

		start_request = Statistics.elapsed;

		if RW == 'R':
			Statistics.requests_read += 1;
			Statistics.requests_pages_read += len(lpns);
		else:
			Statistics.requests_write += 1;
			Statistics.requests_pages_write += len(lpns);

		for lpn in lpns:
			start = Statistics.elapsed;
			if RW == 'W':
				self.process_write(lpn, lpns);
			elif RW == 'R':
				self.process_read(lpn, lpns);
			end = Statistics.elapsed;
			if self.statistics_page is not None:
				self.statistics_page.write("%s %d\n" % (RW, end - start));

		end_request = Statistics.elapsed;
		if self.statistics_request is not None:
			self.statistics_request.write(
					"%s %d\n" % (RW, end_request - start_request));


	def allocate_block(self):
		b = self.free_blocks.pop();
		b.status = Block.INUSE;

		return b;


	def select_victim_block(self):
		victim = None;
		score_max = 0;

		# select a victim block according to cost-benefit
		for b in self.blocks:
			if b.status != Block.USED: continue;
			if b.valid_pages == 0:	# Free block!
				victim = b;
				break;

			age = Statistics.clock - b.last_accessed;
			score = age * ((NAND.PAGES_PER_BLOCK / float(b.valid_pages)) - 1);

			if score < score_max: continue;

			victim = b;
			score_max = score;

		victim.status = Block.GC;

		return victim;


	def update_mapping(self, lpn, block, offset):
		# Invalidate old mapping
		old_ppn = self.l2p[lpn];
		if old_ppn != Page.INVALID:
			(old_block, old_offset) = NAND.from_ppn(old_ppn);
			assert self.blocks[old_block].lpns[old_offset] == lpn;
			self.blocks[old_block].lpns[old_offset] = Page.INVALID;
			self.blocks[old_block].valid_pages -= 1;

		# update map
		self.l2p[lpn] = NAND.to_ppn(block, offset);
		block.lpns[offset] = lpn;

		return;


	def backup_lsb_page(self, block, offset, lpn, request_lpns, in_reclaim = False):
		if not NAND.is_msb(offset) or self.no_backup: return;

		pair_offset = NAND.get_paired_page(offset);
		pair_lpn = block.lpns[pair_offset];

		if lpn == pair_lpn:
			Statistics.pages_overwritten += 1;
			return;

		if pair_lpn in request_lpns:
			if self.per_request and not in_reclaim:
				Statistics.pages_skipped += 1;
				return;
			elif in_reclaim:
				return;

		self.read_page(NAND.to_ppn(block, pair_offset));
		self.write_page(self.backup_block, self.backup_block.offset);

		Statistics.pages_backup += 1;
		self.backup_block.offset += 1;
		while self.backup_block.offset < NAND.PAGES_PER_BLOCK and \
			NAND.is_msb(self.backup_block.offset):
			self.backup_block.offset += 1;

		if self.backup_block.offset == NAND.PAGES_PER_BLOCK:
			self.backup_block.status = Block.USED;
			self.erase_block(self.backup_block, backup_block = True);
			self.backup_block.status = Block.INUSE;
