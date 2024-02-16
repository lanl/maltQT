#!/usr/bin/env python3
"""
Reads in a MALT JSON file and provides a human-traversable
  MaltReaderJSON(fname, filterBy=None):
       fname: The name of JSON file to parse, required
    filterBy: A top level filter for including only entities whose
              source file name contains this string.

Data Members of dictionary returned:
          data: Raw JSON data
         names: data["sites"]["strings"] array that holds the
                     names of all entities in the program
         instr: data["sites"]["instr"] array that holds indices into self.names for file, function, and line#
      instrMap: A reverse lookup from address in a stack list to 
                function names
       nameMap: A lookup from function name to addresses of interest
                inside that function.
         count: Dictionary with function names for keys and allocation
                counts for values
     exclusive: Dictionary with function names for keys and exclusive
                allocated memory for values
     inclusive: Dictionary with function names for keys and inclusive
                allocated memory for values
   globalPeaks: Dictionary with function names for keys and
                [inclusive@Peak, exclusive@Peak] memory for values

Methods:
   allocsByName(self, name, exclusive=False):
     Given a function name (regular expression), return the cumulative
     allocations of all functions that match that name. If exclusive
     is set to True, this function returns only exclusive allocations
     are returned. 

   flattenStack(self, stack):
     Given a stack list will return a string with line and function
     numbers "< line:func1 < line:func2 < ...".

   flattenStackFromId(self, stackId):
     Given a stack ID, returns the flattened stack for that stack Id.
     Calls flattenStack to do flattening. 

   getAnnotatedTimeline(self):
     Returns the timeline as a dictionary with real time in seconds
     and a flattened stack added to the data. 

   dumpTimeline(self, fname):
     Dumps timeline to CSV file with real time in seconds and
     flattened stack added to the data. If fname is None, output is
     sent to stdout.

   dumpGlobalPeak(self, fname):
     Dumps Global Peak data to CSV file with stacks added.  If fname
     is None, output is sent to stdout.

   dumpLeaks(self, fname):
     Dumps Leaks to CSV file with stacks added.  If fname is None,
     output is sent to stdout.

"""

import re
import json


class MaltReaderJSON:
    def __init__(self, fname, filterBy=None):
        """
        Geneerate an instance of class MaltReaderJSON from file fname.
        If filterBy is provided, only entries that have that string
        in the file name will be included in the data calculations.
        All allocations that are made by culled entities are ascribed
        to their parents.
        """

        # Read the data
        print(f"Reading {fname}")
        data = None
        with open(fname, "r") as fp:
            data = json.load(fp)
        self.data = data
        self.names = self.data["sites"]["strings"]
        self.instr = instr = self.data["sites"]["instr"]
        self.count = {}

        # Filter out uninteresting stuff
        self.filterDataByString_(filterBy)

        # Generate instr to name map
        self.callsite = {}
        self.instrMap = instrMap = {}
        self.nameMap = nameMap = {}
        for item, iDict in instr.items():
            if "file" in iDict:
                idFile = iDict["file"]
            else:
                idFile = None
            idFunction = iDict["function"]
            lineNo = iDict["line"] if "line" in iDict else -1
            myFile = self.names[idFile] if idFile is not None else "Unknown"
            myFunction = self.names[idFunction]
            instrMap[item] = [myFunction, myFile, lineNo]
            if myFunction not in nameMap:
                nameMap[myFunction] = []
            nameMap[myFunction].append(item)

        # Filter out allocs, callocs, ...
        self.filterAllocs_()

        # create indices for quick lookups
        # An experimental feature that isn't quite working yet
        self.index_()

    def addToIndex_(self, name, count, inclusive, exclusive=0, globalPeak=0):
        """Enables indexed searching for higher speed"""
        if name not in self.count:
            # Add entries in dictionary if they don't exist
            self.count[name] = 0
            self.inclusive[name] = 0
            self.exclusive[name] = 0
        self.count[name] += count
        self.inclusive[name] += inclusive
        self.exclusive[name] += exclusive

        if globalPeak > 0:
            if name not in self.globalPeak:
                self.globalPeak[name] = [0, 0]
            # always add to inclusive
            self.globalPeak[name][0] += globalPeak
            if exclusive > 0:
                # Add exclusive only if exclusive is non-zero
                self.globalPeak[name][1] += globalPeak

    def index_(self):
        """
        Enables indexing for searches by creating a reverse lookup.
        This populates self.inclusive, self.exclusive and
        self.globalPeaks all of which are dictionaries with the name
        of a subroutine as key and the appropriate memory as value,
        except for self.globalPeak which is a list with
        [inclusiveGlobalPeak, exclusiveGlobalPeak] as values
        """
        self.inclusive = {}
        self.exclusive = {}
        self.globalPeak = {}

        stats = self.data["stacks"]["stats"]
        for item in stats:
            theStack = item["stack"]
            infos = item["infos"]
            count = infos["alloc"]["count"]
            sumAlloc = infos["alloc"]["sum"]
            globalPeak = infos["globalPeak"]
            if (sumAlloc == 0 or len(theStack) == 0) and globalPeak == 0:
                continue
            inclusive = exclusive = sumAlloc
            theStackId = item["stackId"]
            self.callsite[theStackId] = theStack
            for stackEntry in theStack:
                name = self.instrMap[stackEntry][0]
                self.addToIndex_(name, count, inclusive, exclusive, globalPeak)
                # reset exclusive to 0 for lower items in stack
                exclusive = 0
        print("indexing done")

    def filterDataByString_(self, filterBy):
        """
        Removes all entries that dont contain the filterBy string
        in the file from which they emanate
        """

        if filterBy is None:
            return

        names = self.names
        instr = self.instr
        removers = {}
        for item, iDict in instr.items():
            idFile = iDict["file"]
            myFile = names[idFile]
            if not myFile.find(filterBy) >= 0:
                removers[item] = 0

        # Now remove them from the stacks
        stats = self.data["stacks"]["stats"]
        for s in stats:
            myStack = s["stack"]
            newStack = {x: None for x in myStack}
            for item in myStack:
                if item in removers and item in newStack:
                    newStack.pop(item)
            s["stack"] = list(newStack)
        print(f"filtering by {filterBy} done.")

    def filterAllocs_(self):
        """
        Removes following entries:
           realloc, calloc, malloc, "operator new(unsigned long)",
           anything starting with "__gnu_cxx::"
        This will assign allocated memory to caller
        """
        names = self.names
        instr = self.instr
        removers = {}
        for entry in self.nameMap:
            if (
                entry
                in [
                    "calloc",
                    "malloc",
                    "posix_memalign",
                    "realloc",
                    "operator new(unsigned long)",
                ]
                or entry.startswith("__gnu_cxx::")
                or entry.find("/libstdc++/") > 0
            ):
                for item in self.nameMap[entry]:
                    removers[item] = 0

        # Now remove them from the stacks
        stats = self.data["stacks"]["stats"]
        for s in stats:
            myStack = s["stack"]
            newStack = {x: None for x in myStack}
            for item in myStack:
                if item in removers and item in newStack:
                    newStack.pop(item)
            s["stack"] = list(newStack)
        print(f"filtering Allocators done.")

    def allocsByName(self, name=None, exclusive=False, indices=False):
        """Given a name, prints all allocations associated by that name"""
        if name == None:
            name = "."
        reFound = re.compile(name, re.IGNORECASE)
        retVal = {}
        base = self.exclusive if exclusive else self.inclusive
        for entry in base:
            m = reFound.search(entry)
            if m is not None:
                retVal[entry] = [base[entry], self.count[entry]]
        return retVal

    def flattenStack(self, stack):
        location = ""
        for s in stack:
            if s in self.instrMap:
                imap = self.instrMap[s]
                func = imap[0]
                line = imap[2]
                location += f"< {line}:{func}"
            else:
                location += f"< ??:{s}"
        return location.strip()

    def flattenStackFromId(self, stackId):
        if not stackId in self.callsite:
            return "UNKNOWN"
        return self.flattenStack(self.callsite[stackId])

    def getAnnotatedTimeline(self):
        """
        returns the timeline as a dictionary with real time
        in seconds and a flattened stack added to the data.
        """
        timeline = {}
        timeScale = float(self.data["globals"]["ticksPerSecond"])
        memTimeline = self.data["timeline"]["memoryTimeline"]
        delta = float(memTimeline["perPoints"]) / timeScale
        fields = memTimeline["fields"]
        values = memTimeline["values"]
        callsite = memTimeline["callsite"]
        timeline["fields"] = ["t"] + fields + ["stack"]
        # timeline["values"] = [[0.0, 0.0, 0.0, []]] + [[]] * len(values)
        timeline["values"] = [[]] * len(values)
        for idx, v in enumerate(values):
            theSite = callsite[idx]
            if not theSite in self.callsite:
                stack = [theSite]
            else:
                addrStack = self.callsite[theSite]
                stack = []
                for s in addrStack:
                    if s in self.instrMap:
                        stack.append(self.instrMap[s])
                    else:
                        stack.append(["??", "??", -1])
            t = (idx + 1) * delta
            timeline["values"][idx] = [t] + v + [stack]
        return timeline

    def dumpTimeline(self, fname):
        """Dumps timeline to CSV file with stacks and time in seconds"""
        from pprint import pprint

        if fname is None:
            fp = sys.stdout
        else:
            fp = open(fname, "w")
        timeScale = float(self.data["globals"]["ticksPerSecond"])
        memTimeline = self.data["timeline"]["memoryTimeline"]
        print(memTimeline.keys())
        delta = float(memTimeline["perPoints"]) / timeScale
        fields = memTimeline["fields"]
        values = memTimeline["values"]
        callsite = memTimeline["callsite"]
        fp.write(f"""time(s),request,"{'","'.join(fields)}",location\n""")
        lastValue = 0
        for idx, v in enumerate(values):
            theSite = callsite[idx]
            location = self.flattenStackFromId(theSite)
            t = (idx + 1) * delta
            value = v[0] - lastValue
            fp.write(
                f"""{t},{value},{','.join([f"{x}" for x in v])},"{location.strip()}"\n"""
            )
            lastValue = v[0]

        if fname is not None:
            fp.close()

    def dumpGlobalPeak(self, fname):
        """Dumps Global Peak data to CSV file with stacks"""
        from pprint import pprint

        if fname is None:
            fp = sys.stdout
        else:
            fp = open(fname, "w")
        stats = self.data["stacks"]["stats"]
        fp.write(f"""Memory(MB),location\n""")
        for item in stats:
            theStack = item["stack"]
            infos = item["infos"]
            globalPeak = infos["globalPeak"]
            if globalPeak == 0:
                continue
            theStackId = item["stackId"]
            location = self.flattenStackFromId(theStackId)
            fp.write(f"""{float(globalPeak)/1048576.:.3f},"{location}"\n""")

        if fname is not None:
            fp.close()

    def dumpLeaks(self, fname):
        """Dumps Leaks to CSV file with stacks"""
        from pprint import pprint

        if fname is None:
            fp = sys.stdout
        else:
            fp = open(fname, "w")
        leaks = self.data["leaks"]
        fp.write(f"""Memory(MB),count,location\n""")
        for item in leaks:
            mem = item["memory"]
            count = item["count"]
            theStack = item["stack"]
            location = self.flattenStack(theStack)
            fp.write(f"""{float(mem)/1048576.:.3f},{count},"{location}"\n""")

        if fname is not None:
            fp.close()


if __name__ == "__main__":
    # A couple utility routines and a test program
    import sys

    def getArgs():
        """
        Uses argparse to populate fields in a struct
        Gets arguments from sys.argv

        run with "-h" for a list of arguments
        """
        import argparse

        parser = argparse.ArgumentParser(description="malt utils")

        parser.add_argument(
            "-e",
            dest="exclusive",
            action="store_true",
            help="Directs the code to report exclusive allocations",
        )
        parser.add_argument(
            "-n",
            dest="name",
            action="store",
            help="A regular expression for subroutines to search",
        )
        parser.add_argument(
            "-g",
            dest="globalPeaks",
            action="store_true",
            help="Print the top 10 global peak values",
        )
        parser.add_argument(
            "-f",
            dest="filter",
            action="store",
            help="Filter entries by only including those whose files have this string in the name",
        )
        parser.add_argument("files", help="remainder of command line", nargs="*")

        # parse the command line
        args = parser.parse_args()

        # sanity check on flags
        if args.globalPeaks and args.name:
            raise ValueError("___ERROR: only one of -n or -g should be spedified")
        elif args.globalPeaks is None and args.name is None:
            args.name = "."

        return args

    def sortByValueN(theValues, index=0):
        """Returns a list in acending sort for the results"""
        newDict = {
            f"{value[index]:16.0f}_{key}": value[index]
            for key, value in theValues.items()
        }
        retList = []
        for key in sorted(newDict.keys()):
            value = newDict[key]
            retList.append((key[17:], value))
        return retList

    def formatNumber(v, suffix=""):
        """
        Utility to format a number appropriately scaled
        with ''/k/M/G.  If suffix is specified, that is
        appended to the number, e.g. "B" for memory.
        """

        if v < 1024.0:
            s = f"{v:>6.0f} {suffix}"
        elif v < 1024.0 * 1024.0:
            s = f"{v/1024.:>6.1f}k{suffix}"
        elif v < 1024.0 * 1024.0 * 1024.0:
            s = f"{v/1024./1024.:>6.1f}M{suffix}"
        else:
            s = f"{v/1024./1024./1024.:>6.1f}G{suffix}"
        return s

    def formatNumber10(v, suffix=""):
        """
        Utility to format a number appropriately scaled
        with B/kB/MB/GB suffix
        """

        if v < 1000.0:
            s = f"{v:>6.0f} {suffix}"
        elif v < 1000.0 * 1000.0:
            s = f"{v/1000.:>6.1f}k{suffix}"
        elif v < 1000.0 * 1000.0 * 1000.0:
            s = f"{v/1000./1000.:>6.1f}M{suffix}"
        else:
            s = f"{v/1000./1000./1000.:>6.1f}G{suffix}"
        return s

    # -------------------------------
    # Main starts here
    # -------------------------------
    args = getArgs()
    name = args.name
    for fname in args.files:
        exclusive = args.exclusive
        filterBy = args.filter
        mt = MaltReaderJSON(fname, filterBy)
        topN = 10

        if args.globalPeaks:
            """Printing values at global peak memory usage"""
            retList = sortByValueN(mt.globalPeak, args.exclusive)
            # Print top N entries
            for entry in retList[-topN:]:
                key = entry[0]
                v = entry[1]
                if v == 0:
                    continue
                print(
                    f"    {formatNumber(v,'B')} {key[:20] + '...' + key[-57:] if len(key) > 77 else key  }"
                )
        else:
            """Printing memory allocations for entries that match regexp name"""
            myAllocs = mt.allocsByName(name, exclusive, False)
            retList = sortByValueN(myAllocs)

            # Print top N entries
            for entry in retList[-topN:]:
                key = entry[0]
                v = entry[1]
                if v == 0:
                    continue
                c = mt.count[key]
                print(
                    f"    {formatNumber(v,'B')} {formatNumber10(c)} {key[:20] + '...' + key[-57:] if len(key) > 77 else key  }"
                )

        # Dump timeline, global peak information, and leaks to CSV files
        import os

        base = os.path.splitext(fname)[0]
        mt.dumpTimeline(f"{base}_timeline.csv")
        mt.dumpGlobalPeak(f"{base}_globalPeak.csv")
        mt.dumpLeaks(f"{base}_leaks.csv")
