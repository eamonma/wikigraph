import os
import sys
import datetime
from wikigraph import process_dump

if __name__ == "__main__":
    os.chdir(__file__[0:-len('wikigraph/main.py')])
    process_dump.process_xml()
