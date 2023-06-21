Simple FTL simulator, Copyright Sang-Hoon Kim <sanghoonkim@ajou.ac.kr>, 2023.

# Overview

This FTL simulator provides page-mapping FTL and DAC [1]. Unlike other FTL simulators, this simulator performs the LSB backup [2] to counter the paired-page interference.


# Usage
To get help,

    $ ./ftlsim.py --help

You can modify `NAND.py` to change the NAND flash configurations including the number of pages per block, the number of sectors per page, times to read/write/erase, and paired-page configuration. `SSD.py` configures the total SSD size and the over-provisioning ratio.

## Workload file
The workload file should be the following form. You can also input operations from the console.

	# The lines starting with # are ignored
	# Read 32 sectors from sector 16
	R 16 32
	# Write 8 sectors from sector 96
	W 96 8

The operations will be automatically wrap-around if the sector number exceeds the total storage size.

# References

 [1] Mei-Ling et al., "Using data clustering to improve cleaning performance for flash memory," Software-Practice and Experience, Vol. 29, No. 3, pp 267--290, 1999.
 [2] LSB backup
