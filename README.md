# maltQt
LANL Open Source Release ID O4736

This program is Open-Source under the BSD-3 License.
 
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:
 
Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
 
Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
 
Neither the name of the copyright holder nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.  THIS
SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Getting started

You will need to install PySide6/Qt6 to use the main branch.  In case
you only have PySide2/Qt5 available, use branch `qt5`.

Load up JSON files with optional source directories specified using this command:
```
maltQt.py <file1.json> [file2.json file3.json...] [-d /path/to/src,/path/to/src2/,...]
```
Hover over graphical elements to display tool tips.

## Command Line Arguments
- At least one JSON file is required
- More JSON Files are optional
- Source directories are specified with the `-d` flag.  Separate
  multiple source directories with commas

## Timeline Tab
- Click on the "Timeline" tab to display allocation timeline
- Click in timeline to see stack at that point
- Click in stack to display source code at that point
- Left and right arrows or drag-mouse will display other points in the
  stack

### Searching
- Enter a search term in the search bar and hit 'enter'.  This will
  display the first stack that includes the provided regular
  expression.
- Use the left and right green arrows to jump to next stack with your
  expression to right or left of current point
- Hitting 'enter' repeatedly will also jump forward to next stack with expression.  
- Hitting 'shift-enter' will jump to previous stack with expression
- Keeping 'Alt/Option' key pressed with above key strokes / mouse
  presses will jump forward by ten searches for quickly getting to a
  particular point in the timeline

## Global Peak Stacks Tab
- Click on the "Global Peak Stacks" tab to display the stacks at
  global peak sorted by allocated memory
- Clicking on any allocation entry will display the stack and source
  code associated with that location on the right
- Source code display also includes the sum of all allocations that
  passed through that line

## Leaks Tab
- Click on the "Leaks" tab to display the leaks detected by Malt
- Clicking on any leak entry will display the stack and source code
  associated with that location on the right
- Source code display also includes the sum of all leaks that passed
  through that line

## Preferences Tab
- Click on the "Preferences" tab to add source code directories.  The
  default is to display all the source code directories specified thus
  far
- Clicking on a row in the table will allow you to modify / add new
  entries to this table
- The code first looks for files in the location specified in the JSON
  file.  Failing that, it will search recursively through the
  directories specified for the file stopping as soon as it finds the
  file

## Comments / Bug reports
Send all comments / bug reports to `sriram@lanl.gov`
