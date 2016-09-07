#!/usr/bin/env python

import SSD;

import PageFTL;
import DAC;

def create(args):
	ftl = args["ftl"];

	if ftl == "page":
		return PageFTL.PageFTL(args, SSD.BLOCKS);
	elif ftl == "dac":
		return DAC.DAC(args, SSD.BLOCKS);
	return None;
