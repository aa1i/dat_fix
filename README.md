# doscan
Tool to scan wav files from a DAT transfer for drop-outs

Scan a wav file from a DAT transfer for drop outs.  These seem to manifest as regions of repeated samples. 
The thresh parameter adjusts the threshold number of repeated samples to be considered a drop out.

# TODO
[ ]  tool to compare multiple takes from the same transfer and find the number of samples to shift to align them

[ ]  handle multiple takes/files, align them, detect drop out regions, and fill from takes without dropouts.
