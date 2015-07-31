
# wdw 30 july '15.

# translation of time.c, for the lx95/100, from 1994 !

# wanted: an example, existing data file...

# why are the V lines a mix of hex and decimal ???

from collections import deque

NLIST = 100
HEIGHT = 11

class Timelog(object):
    def __init__(self):
        self.changed    = False
        self.timelist   = deque()
        self.nlist      = 0
        self.curline    = 0
        self.yrtotal    = 0
        self.wktotal    = 0
        self.daytotal   = 0
        self.start_time = 0
        self.working    = 0

    def load_file(self, fname):
        try:
            fd = open(fname, 'r')
        except:
            print "can't open file"
            return
        for line in fd:
            line = line.strip()
            if line:
                self.add_item(line, False)
            else:
                self.add_item(" ", False)   # FIXME: are blank lines useful?
        fd.close()
        self.changed = False
        for item in self.timelist():
            line = item[0].split()
            if len(line) == 6:
                if line[0] == 'V':
                    try:
                       p1 = int(line[1], 16) # sscanf ?
                       p2 = int(line[2], 16)
                       p3 = int(line[3], 16)
                       p4 = int(line[4], 16)
                       p5 = int(line[5])
                    except:
                        return
                    self.yrtotal    = p1
                    self.wktotal    = p2
                    self.daytotal   = p3
                    self.start_time = p4
                    self.working    = p5

    def save_file(self, fname):
        try:
            fd = open(fname, 'a')
        except:
            print "can't open file"
            return
        vline = "V %x %x %x %x %d" % (self.yrtotal, self.wktotal, self.daytotal, 
                self.start_time, self.working)
        self.add_item(vline, True)
        self.add_item(" ", True)    # FIXME are blank lines useful?
        for item in self.timelist():
            if item[1]:
                fd.write(item[0] + '\n')
        self.changed = False

    def add_item(self, line, is_new):
        while len(self.timelist) >= NLIST:
            self.timelist.popleft()
        self.timelist.append( [line, is_new] )
        self.nlist = len(self.timelist)
        if self.nlist > HEIGHT:
            self.curline = self.nlist - HEIGHT
        if is_new:
            self.changed = True

if __name__ == '__main__':
    t = Timelog()


