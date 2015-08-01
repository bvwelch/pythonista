
# wdw 30 july '15.

# FIXME what is the purpose of 'delta' in calc_ovr???

# translation of time.c, for the lx95/100, from 1994 !

from collections import deque
import time, datetime

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
        self.start_time = self.get_time()
        self.working    = 0

    def load_file(self, fname):
        try:
            fd = open(fname, 'r')
        except:
            print "can't open file"
            return -1
        for line in fd:
            line = line.strip()
            if line:
                self.add_item(line, False)
            else:
                self.add_item(" ", False)   # FIXME: are blank lines useful?
        fd.close()
        self.changed = False
        for item in self.timelist:
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
                        print "error parsing V line", line
                        return -1
                    self.yrtotal    = p1
                    self.wktotal    = p2
                    self.daytotal   = p3
                    self.start_time = p4
                    self.working    = p5
        return 0

    def save_file(self, fname):
        try:
            fd = open(fname, 'a')
        except:
            print "can't open file"
            return -1
        vline = "V %x %x %x %x %d" % (self.yrtotal, self.wktotal, self.daytotal, 
                self.start_time, self.working)
        self.add_item(vline, True)
        self.add_item(" ", True)    # FIXME are blank lines useful?
        for item in self.timelist:
            if item[1]:
                fd.write(item[0] + '\n')
        self.changed = False
        return 0

    def add_item(self, line, is_new):
        while len(self.timelist) >= NLIST:
            self.timelist.popleft()
        self.timelist.append( [line, is_new] )
        self.nlist = len(self.timelist)
        if self.nlist > HEIGHT:
            self.curline = self.nlist - HEIGHT
        if is_new:
            self.changed = True

    def do_start_stop(self):
        cur_time = self.get_time()
        delta = cur_time - self.start_time

        if self.working:
            self.wktotal += delta
            self.daytotal += delta
            self.yrtotal += self.calc_ovr(self.wktotal, delta)
            head = "E"
            self.working = 0
        else:
            head = "B"
            self.working = 1

        self.start_time = cur_time
        hr = delta / 3600
        min = (delta % 3600) / 60
        sec = delta % 60
        if (sec >= 30):
            min += 1
        if (min >= 60):
            hr += 1
        min %= 60

        # note: "working" has been toggled above
        if self.working:
            line = "%s            %s, %02d:%02d" % (head, self.get_date_time_str(), hr, min)
        else:
            line = "%s         %s, %02d:%02d"    % (head, self.get_date_time_str(), hr, min)
        self.add_item(line, True)

    def do_new_week(self):
        if self.working:
            print "Sorry, you must do a STOP first"
            return -1
        hr = self.wktotal / 3600
        min = (self.wktotal % 3600) / 60
        sec = self.wktotal % 60
        if (sec >= 30):
            min += 1
        if (min >= 60):
            hr += 1
        min %= 60
        s = self.get_date_str()
        line = "WT %02d:%02d, %s" % ( hr, min, s)
        self.add_item(line, True)
        self.add_item(" ", True)
        self.wktotal = 0
        return 0

    def do_new_day(self):
        if self.working:
            print "Sorry, you must do a STOP first"
            return -1
        hr = self.daytotal / 3600
        min = (self.daytotal % 3600) / 60
        sec = self.daytotal % 60
        if (sec >= 30):
            min += 1
        if (min >= 60):
            hr += 1
        min %= 60
        s = self.get_date_str()
        line = "DT %02d:%02d, %s" % ( hr, min, s)
        self.add_item(line, True)
        self.add_item(" ", True)
        self.daytotal = 0
        return 0

    def do_note(self, line):
        if line:
            self.add_item(line, True)

    def get_time(self):
        t = time.time()
        t =  int( round(t) ) # seconds since 1970
        return t

    # the formula for overtime is: overtime = hrs > 40/wk
    def calc_ovr(self, wktot, delta ):
        ovr = 0
        if (wktot > 40*3600):
            ovr = wktot - 40*3600
        if (ovr > delta):
            ovr = delta
        return ovr

    def get_date_time_str(self):
        t = datetime.datetime.now()
        s = t.strftime("%m/%d/%y %H:%M:%S")
        return s

if __name__ == '__main__':
    t = Timelog()
    t.load_file('test01.log')
    time.sleep(5)
    t.do_start_stop()
    time.sleep(65)
    t.do_start_stop()
    time.sleep(115)
    t.do_start_stop()
    t.save_file('test01.log')

