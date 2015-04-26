# wdw 18 dec '10

# rotating logfile.  derived from preproc logger
#
# This module just takes care of writing to a rotating log file. It does not
# know anything about where the data comes from.  However, the 'annotate'
# routine will prepend a timestamp to the logfile.

import sys, os
from time import localtime, mktime, strftime

log_filename_pattern = './%s_%04d-%02d-%02d.log'

class Logfiler(object):
    def __init__(self, fnameprefix):
        self.log_file = None
        self.fnameprefix = fnameprefix
        self.open()

    def open(self):
        self.log_day = mktime(localtime())
        self.log_date    = localtime(self.log_day)[2]
        self.log_month   = localtime(self.log_day)[1]
        self.log_year    = localtime(self.log_day)[0]
        log_filename = log_filename_pattern % (self.fnameprefix, self.log_year, self.log_month, self.log_date)
        self.log_file = open(log_filename, 'a')

    def rename(self, fnameprefix):
        if self.log_file:
            old_filename = log_filename_pattern % (self.fnameprefix, self.log_year, self.log_month, self.log_date)
            self.fnameprefix = fnameprefix
            new_filename = log_filename_pattern % (self.fnameprefix, self.log_year, self.log_month, self.log_date)
            os.rename(old_filename, new_filename)

    def close(self):
        if self.log_file:
            self.log_file.close()

    def write(self, line):
        """ no frills, just write the line 'as-is' to the file """
        self.check_for_midnite()
        if self.log_file:
            self.log_file.write(line + '\n')
            self.log_file.flush()

    def annotate(self, msg):
        """ adds date/time-stamp to the entry """
        lt = localtime()
        ymd = strftime("%Y-%m-%d", lt)
        hms = strftime("%H:%M:%S", lt)
        line = '''"%s %s"\t%s''' % ( ymd, hms, msg)
        self.write(line)

    def check_for_midnite(self):
        self.log_day = mktime(localtime())
        if self.log_date != localtime(self.log_day)[2]:
            if self.log_file:
                self.log_file.close()
            self.open()

# usage example: std input is written to rotating logfile
def main():

    if len(sys.argv) != 2:
	    print "usage: %s: filenameprefix" % sys.argv[0]
	    raise SystemExit(1)

    log = Logfiler('mylog')
    while log:
        line = sys.stdin.readline()
        if line:
            log.annotate(line)
            #log.write(line)
        else:
            log.close()
            log = None
 
if __name__ == '__main__':
    main()
