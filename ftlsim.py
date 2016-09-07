#!/usr/bin/env python

import os;
import sys;
import argparse;
import datetime;

import FTLFactory;
import Statistics;
import NAND;
import SSD;

from Trace import *;

args = None;

def parse_argv():
	global args;

	parser = argparse.ArgumentParser(description='FTL simulator');
	parser.add_argument(
			'infile',
			nargs = '?',
			default = '-',
			type = argparse.FileType('r'),
			help = "Read operations from the workload file. \
					If omitted, read from stdin");
	parser.add_argument(
			'-outfile',
			nargs = '?',
			type = argparse.FileType('w'),
			help = "Write results additionally to the output file.");
	parser.add_argument(
			'-verbose', '-v',
			action = 'count',
			default = 0,
			help = "Print out more information");
	parser.add_argument(
			'-quiet', '-q',
			action = 'count',
			default = 0,
			help = "Print out the summary only");
	parser.add_argument(
			'-ftl',
			nargs = '?',
			default = "page",
			choices = ["page", "dac"],
			help = "FTL implementation");
	parser.add_argument(
			'-no_backup',
			action = 'store_true',
			default = argparse.SUPPRESS,
			help = "Do not backup LSB pages");
	parser.add_argument(
			'-per_request',
			action = 'store_true',
			default = argparse.SUPPRESS,
			help = "Do per-page backup scheme");
	parser.add_argument(
			'-clean_init',
			action = 'store_true',
			help = "Start with clean SSD instead of filled one");
	parser.add_argument(
			'-statistics_page',
			nargs = '?',
			type = argparse.FileType('w'),
			default = argparse.SUPPRESS,
			help = "Write out per-page timing statistics to the file");
	parser.add_argument(
			'-statistics_request',
			nargs = '?',
			type = argparse.FileType('w'),
			default = argparse.SUPPRESS,
			help = "Write out per-request timing statistics to the file");

	# FTL-specific arguments
	# For DAC
	parser.add_argument(
			'--regions',
			type = int,
			default = argparse.SUPPRESS,
			help = "DAC: # of regions");

	args = parser.parse_args();

	trace_init(args.verbose - args.quiet, args.outfile);

	ftl_args = {};
	ftl_args["ftl"] = args.ftl;

	# FTL parameters
	for k,v in vars(args).items():
		if k in [ "no_backup", "statistics_page", "statistics_request",
				"per_request",
				"regions",
				"interval", "low_watermark", "high_watermark",
				"omega_threshold", "size_threshold",
				"print_workload_locality"]:
			ftl_args[k] = v;

	return ftl_args;

def process_workload(ftl, workload):

	progress_marks = [];
	progress_last = datetime.datetime.now();
	progress_delta = 0;

	if workload is not sys.stdin:
		trace("- Workload file:", workload.name, level = 1);

		num_requests = sum(1 for l in workload);
		trace("- Requests to process:", num_requests);
		progress_delta = num_requests / 10;
		progress_marks = [num_requests * i / 10 for i in range(10)];
		workload.seek(0);


	trace("- Running workloads ...");
	for l in workload.xreadlines():
		e = l.strip().lstrip().split();

		if (len(e)) == 0: continue;

		RW = e[0].upper();

		# Skip comments
		if RW[0] == '#': continue;

		sector_start = long(e[1]);
		sector_count = long(e[2]);

		assert sector_count <= SSD.SECTOR_MAX;

		# Wrap-around to the LBA space
		if sector_start >= SSD.SECTOR_MAX:
			sector_start %= SSD.SECTOR_MAX;

		sector_end = sector_start + sector_count;

		if sector_end <= SSD.SECTOR_MAX:
			ftl.process(RW, sector_start, sector_count);
		else:
			ftl.process(RW, sector_start, SSD.SECTOR_MAX - sector_start);
			ftl.process(RW, 0, sector_end - SSD.SECTOR_MAX);

		if Statistics.clock in progress_marks:
			trace("  %d%% " % (progress_marks.index(Statistics.clock) * 10),
					level = 4);

			now = datetime.datetime.now();
			elapsed = now - progress_last;
			progress_last = now;
		Statistics.clock += 1;


def main():
	global args;
	ftl_args = parse_argv();

	trace("***********************************************************");
	trace("*                  FTL simulator v0.9-l                   *");
	trace("*                                                         *");
	trace("*                       by sanghoon@calab.kaist.ac.kr     *");
	trace("***********************************************************");
	trace

	ftl = FTLFactory.create(ftl_args);
	if ftl == None:
		print "Cannot create FTL", args.ftl;
		return;

	trace("- Run at", datetime.datetime.now(), level = 1);
	trace("- FTL:", ftl.name, level = 1);
	for k,v in ftl_args.items():
		if k != "ftl":
			trace("  " + k + " =", v, level = 1);

	if not args.clean_init:
		trace("- Fill up usable space ...", newline = False);
		for req in range(int(SSD.BLOCKS * (1 - SSD.PROVISION_RATIO))):
			sector_start = req * NAND.PAGES_PER_BLOCK * NAND.SECTORS_PER_PAGE;
			ftl.process('W',
					sector_start, NAND.PAGES_PER_BLOCK * NAND.SECTORS_PER_PAGE);
		Statistics.reset();
		trace("Done");

	dt_start = datetime.datetime.now();

	try:
		process_workload(ftl, args.infile);
	except KeyboardInterrupt as e:
		print;
		pass;

	dt_finish = datetime.datetime.now();

	trace();
	trace("- Run for", dt_finish - dt_start);
	trace("- Results");
	trace();

	Statistics.print_stats();


if __name__ == "__main__":
	main();
