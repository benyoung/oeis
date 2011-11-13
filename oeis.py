#!/usr/bin/python

#----------------------------------------------------------------
# Command-line tool to query the OEIS.  Written in python.
#
# usage: 
#       oeis.py 1 2 5 14 42
#       oeis.py -n4 1 2 5 14 42
#
# Everything here should be usable from sage.
# You need to install pycurl to make this work.

import pycurl
import re
import copy
from collections import defaultdict
from optparse import OptionParser

#=========================================================================
# This is copy-pasted from a pycurl example script.  I have renamed things.
class BagOfStuffFromTheInternet:
    def __init__(self):
        self.contents = ""

    def callback(self, buf):
        self.contents += buf

#----------------------------------------------------------------------
# Query the online encyclopedia of integer sequences, requesting at most
# n responses.  Return everything it says as a string.
def rawquery(sequence, n):
    querystr = "http://oeis.org/search?q="
    querystr += ",".join([str(x) for x in sequence])
    querystr += "&n=" + str(n) + "&fmt=text"

    t = BagOfStuffFromTheInternet()
    c = pycurl.Curl()
    c.setopt(c.URL, querystr)
    c.setopt(c.WRITEFUNCTION, t.callback)
    c.perform()
    c.close()
    return t.contents


#==================================================================
# A stub for rawquery, so I can develop offline, and so I don't have to wait
# for responses from OEIS, which can be slow.  The file "sampleresponse"
# should exist.
def dummyquery(sequence, n):
    f = open('sampleresponse', 'r')
    response = f.read()
    f.close()
    return response

#==================================================================
# Parse what the OEIS said.  Returns a list of records, one per matching
# sequence.  Each record is a defaultdict(list), whose keys are single-letter
# field names in the OEIS database, see 
#
#     http://oeis.org/wiki/OEIS_sequence_entries
#
# Each of the values are a list of entries (since many of the fields in the
# OEIS can have multiple values).  
# 
# There is an extra field, "Anumber", which contains [sequences number]

def oeis_parse(response):
    output = []
    record = defaultdict(list)
    currentseq = ""
    for line in response.split("\n"):
        match = re.match("Showing (.*)", line)
        if match:
            print "Showing " + match.group(1) + " matching sequences."
        match = re.match("\%(.)\s+(A\d+)\s+(.*)$", line)
        if match:
            field = match.group(1)
            seq = match.group(2)
            text = match.group(3)
            if seq != currentseq:
                output.append(copy.copy(record))
                record = defaultdict(list)
                record["Anumber"].append(seq)
                currentseq = seq
            record[field].append(text)
    output.append(record)
    output.pop(0)
    return output

#==========================================================================

parser = OptionParser()
parser.add_option("-n",  default=10, type="int", dest="num_responses")

(options, positional_arguments) = parser.parse_args()
sequence = [int(arg) for arg in positional_arguments]

what_oeis_said = rawquery(sequence, options.num_responses)
records = oeis_parse(what_oeis_said)

for record in records:
    print record["Anumber"][0], " ", record["N"][0]





