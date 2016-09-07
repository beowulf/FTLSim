PY = ftlsim.py Statistics.py Trace.py \
		Page.py Block.py NAND.py SSD.py \
		FTL.py FTLFactory.py PageFTL.py DAC.py

.PHONY: all
all:
	python -m compileall ${PY}

.PHONY: clean
clean:
	rm *.pyc
