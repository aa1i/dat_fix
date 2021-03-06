# dat_fix
Collection of tools to scan and repair wav files from a DAT transfer to detect and correct drop-outs

Scan a wav file from a DAT transfer for drop outs.  These seem to manifest as regions of repeated samples. 
The thresh parameter adjusts the threshold number of repeated samples to be considered a drop out.

# Usage

* transfer two or more takes from the master DAT
* open file, read file info with get_file_info()
* find length of tape leader with get_leader_length()
* scan using scan_file() to detect dropout regions
* compute "dropout_score" using dropout_score()
* repeat for additional takes
* use do_scan_and_fill_2() to scan main take for dropouts, and fill from secondary take
* compute "dropout_score" using dropout_score() on corrected file to look for imporovement

## Workflow

Transfer the recording off the DAT to a wave file on a computer.  It is assumed the user knows how to do this. Use a pure digital transfer. Coaxial S/PDIF is recommended.

  Get multiple takes (2-3+) of the same master tape.  They should be byte-identical except for dropouts, and variable length leader/trailer sections.  The tools currently scan for and ignore the leader region. The trailer may require further work.

### Visualization / Verification

I find it helpful to load the main take into Audacity, then import the corrected file as a second track. using the zoom and "time shift" tools, align the two tracks sample to sample.  You will have to zoom in very close to see the individal samples for the final alignment.

  Select the main tack, then Effect/Invert. Select both tracks, then Tracks/Mix and Render to New Track.  The difference track should be mostly zero. If not, undo the mix and render and invert, then re-align the tracks and repeat.

  The non-zero portions of the difference will be where the corrections were applied. By selecting a region around the correction and using "solo" you can listen to the corrected and un-corrected audio.

### thresh paramter

Good settings for 44.1 kHz / 48 kHz sources seem to range from 20 to 50 to 100. Lower values mor aggressively correct dropouts.  Settings below 20 tend to generate false positives where the audio data doesn't change much (low amplitude, low frequency?).  Settings above 100 allow too many dropouts through.

# modules

## get\_file\_info

```python
    def get_file_info( self, file ):
        """
        " Get information from wave file header
        " 
        " inputs:
        "   file{} - dictionary with info on the wav file from the dat transfer
        "   file[ "name" ] - the name of the file
        "
        " outputs:
        "   file[ "nchannels" ] - number of audio channels per frame in the file
        "   file[ "sampwidth" ] - number of bytes per channel 
        "   file[ "sampwidth" ] - number of bytes per channel 
        "   file[ "framerate" ] - number of frames per second 
        "   file[ "nframes" ]   - total number of frames in the file 
        """
```

## get_leader_length

```python
    def get_leader_length( self, file ):
        """
        " Scan for an arbitrarily long sequence of zero samples
        " at the start of a file, so that it can be eliminated
        "
        " inputs:
        "   file{} - dictionary with info on the wav file from the dat transfer
        "   file[ "name" ] - the name of the file
        "   file[ "nchannels" ] - number of audio channels per frame in the file
        "   file[ "sampwidth" ] - number of bytes per channel 
        "   file[ "sampwidth" ] - number of bytes per channel 
        "   file[ "framerate" ] - number of frames per second 
        "   file[ "nframes" ]   - total number of frames in the file 
        "
        " outputs:
        "   file[ "leader_length" ] - count of initial zero sample in the file
        "
        " assumes sampwidth == 2 ???
        """
```

## scan\_file

```python
def scan_file( self, fname, thresh=100 ):
        """
        " scan the specified wave file for sequences of duplicated
        " samples of length greater than thresh. These sequences
        " are assumed to be drop-outs resulting from imperfect
        " playback of a DAT tape
        "
        " input:
        "   fname: filename to scan
        "   thresh: <optional> threshold length of dropout sequences in samples.
        "           default: 100, although 50, 25, 20 also seem to perform reas>onably well
        "           low thresh values (<10) risk false positives generated by real
        "           content of the wave file (possibly low frequency or low volume sections)
        "
        " output:
        "   diagnostics printed to stdout
        """
```

## do\_scan\_and\_fill\_2

```python
    def do_scan_and_fill_2( self, file_list, thresh=100 ):
        """
        " look for dropouts in file 1 where sample values are duplicated 
        " for more than thresh samples, and then attempt to fill them from
        " another file if there duplicate sample run length is less.
        "
        " This should work well for dropouts where the level is held constant
        " and successive takes yield shorter dropouts or dropouts in different areas.
        "
        " this will not work for noisy dropouts where the value changes rapidly.
        "
        " inputs:
        "    file_list: list of file info dicts provided by get_file_info() function
        "               requires two files
        "               TODO: this reall needs two and only two files, specify directly rather than as a list?
        "    thresh:    optional - specify threshold dropout size to fill
        "
        " outputs:
        "    out.wav:   merged file
        """
```

## median filter

This is a fast correcting filter using three files, but may not work well if there is large disparity between the takes.

```python
    def median_3( self, file_list ):
        """
        " take three copies of a file
        " and use a median filter to eliminate dropouts where possible
        "
        " Note: this is fairly fast and shows some improvement, 
        " but can sometimes propagate errors
        """
```

# TODO
[ ]  tool to compare multiple takes from the same transfer and find the number of samples to shift to align them

[ ]  handle multiple takes/files, align them, detect drop out regions, and fill from takes without dropouts.
[ ] detect and trim variable length trailer regions

[ ] add tool to align tracks / calculate the relative shift between takes