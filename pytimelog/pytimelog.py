
# wdw 30 july '15.

# FIXME what is the purpose of 'delta' in calc_ovr???

# translation of time.c, for the lx95/100, from 1994 !

VERSION = "Time V0.1"

from collections import deque
import time, datetime

class Timelog(object):
    def __init__(self, nlmax, numrows):
        self.changed    = False
        self.timelist   = deque()
        self.nlistmax   = nlmax
        self.height     = numrows
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
            time.sleep(2)
            return -1
        for line in fd:
            line = line.strip()
            if line:
                self.add_item(line, False)
            else:
                self.add_item(" ", False)
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
                        time.sleep(2)
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
            time.sleep(2)
            return -1
        vline = "V %x %x %x %x %d" % (self.yrtotal, self.wktotal, self.daytotal, 
                self.start_time, self.working)
        self.add_item(vline, True)
        self.add_item(" ", True)
        for item in self.timelist:
            if item[1]:
                fd.write(item[0] + '\n')
        self.changed = False
        return 0

    def add_item(self, line, is_new):
        self.bounds_check()
        while len(self.timelist) >= self.nlistmax:
            self.timelist.popleft()
        self.timelist.append( [line, is_new] )
        self.nlist = len(self.timelist)
        if self.nlist > self.height:
            self.curline = self.nlist - self.height
        if is_new:
            self.changed = True

    def heading(self):
        delta = self.get_time() - self.start_time
        if self.working:
            head = "WRK"
            wkt = self.wktotal + delta
            dt = self.daytotal + delta
            yrt = self.yrtotal + self.calc_ovr(wkt, delta)
        else:
            head = "BRK"
            yrt = self.yrtotal
            wkt = self.wktotal
            dt = self.daytotal

        wmin = (wkt % 3600) / 60
        wmin %= 60L

        dhr = dt / 3600
        dmin = (dt % 3600) / 60
        dsec = dt % 60
        if dsec >= 30:
            dmin += 1
        if dmin >= 60:
            dhr += 1
        dmin %= 60

        bhr = delta / 3600
        bmin = (delta % 3600) / 60
        bsec = delta % 60
        if bsec >= 30:
            bmin += 1
        if bmin >= 60:
            bhr += 1
        bmin %= 60

        togo = wkt / 28800
        togo *= 28800
        togo = wkt - togo
        togo = 28800 - togo
        tghr = togo / 3600
        tgmin = (togo % 3600) / 60

        line1 = "%s   %2d:%02d" % ( VERSION, tghr,  tgmin)
        line2 = "OVR:%3d WK: %2d:%02d DAY: %02d:%02d %s: %02d:%02d" % ( yrt/3600, wkt/3600, wmin, dhr,dmin, head, bhr,bmin)
        return [ line1, line2 ]

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
            time.sleep(2)
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
            time.sleep(2)
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

    def get_ovr_settings(self):
        hr = self.yrtotal / 3600
        min = (self.yrtotal % 3600) / 60
        sec = self.yrtotal % 60
        if (sec >= 30):
            min += 1
        if (min >= 60):
            hr += 1
        min %= 60
        return [ hr, min ]

    def put_ovr_settings(self, hr, min):
        if self.working:
            print "Sorry, you must do a STOP first"
            time.sleep(2)
            return -1
        self.yrtotal = (hr * 3600) + (min * 60)
        line = "; Changed overtime to %lx" % self.yrtotal
        self.add_item(line, True)
        return 0

    def get_weekly_settings(self):
        hr = self.wktotal / 3600
        min = (self.wktotal % 3600) / 60
        sec = self.wktotal % 60
        if (sec >= 30):
            min += 1
        if (min >= 60):
            hr += 1
        min %= 60
        return [ hr, min ]

    def put_weekly_settings(self, hr, min):
        if self.working:
            print "Sorry, you must do a STOP first"
            time.sleep(2)
            return -1
        self.wktotal = (hr * 3600) + (min * 60)
        line = "; Changed weekly total to %lx" % self.wktotal
        self.add_item(line, True)
        return 0

    def get_daily_settings(self):
        hr = self.daytotal / 3600
        min = (self.daytotal % 3600) / 60
        sec = self.daytotal % 60
        if (sec >= 30):
            min += 1
        if (min >= 60):
            hr += 1
        min %= 60
        return [hr, min]

    def put_daily_settings(self, hr, min):
        if self.working:
            print "Sorry, you must do a STOP first"
            time.sleep(2)
            return -1
        self.daytotal = (hr * 3600) + (min * 60)
        line = "; Changed daily total to %lx" % self.daytotal
        self.add_item(line, True)
        return 0

    def do_advboth_settings(self, hr, min):
        if self.working:
            print "Sorry, you must do a STOP first"
            time.sleep(2)
            return -1
        self.wktotal += (hr * 3600) + (min * 60)
        self.daytotal += (hr * 3600) + (min * 60)
        line = "; Advanced both %d:%02d" % (hr, min)
        self.add_item(line, True)
        return 0

    def do_bckboth_settings(self, hr, min):
        if self.working:
            print "Sorry, you must do a STOP first"
            time.sleep(2)
            return -1
        self.wktotal -= (hr * 3600) + (min * 60)
        self.daytotal -= (hr * 3600) + (min * 60)
        line = "; Backup both %d:%02d" % (hr, min)
        self.add_item(line, True)
        return 0

    def do_parse_vline(self):
        self.bounds_check()
        item = self.timelist[self.curline]
        line = item[0].split()
        if len(line) == 6:
            if line[0] == 'V':
                try:
                   xyrtotal  = int(line[1], 16) # sscanf ?
                   xwktotal  = int(line[2], 16)
                   xdaytotal = int(line[3], 16)
                   stime     = int(line[4], 16)
                   xworking  = int(line[5])
                except:
                    return "error parsing V line: %s" % line

        yhr = xyrtotal / 3600
        ymin = (xyrtotal % 3600) / 60
        if (ymin >= 60):
            yhr += 1
        ymin %= 60

        whr = xwktotal / 3600
        wmin = (xwktotal % 3600) / 60
        if (wmin >= 60):
            whr += 1
        wmin %= 60

        dhr = xdaytotal / 3600
        dmin = (xdaytotal % 3600) / 60
        if (dmin >= 60L):
            dhr += 1
        dmin %= 60

        line = "OVR: %d:%02d WK: %d:%02d DAY: %d:%02d" % (yhr, ymin, whr, wmin, dhr, dmin)
        return line
        
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

    def get_date_str(self):
        t = datetime.datetime.now()
        s = t.strftime("%m/%d/%y")
        return s

    def cursor_home(self):
        self.curline = 0

    def cursor_end(self):
        self.curline = self.nlist - 1

    def cursor_up(self):
        if self.curline >= 1:
            self.curline -= 1

    def cursor_down(self):
        self.curline += 1
        self.bounds_check()

    def cursor_page_up(self):
        if self.curline >= self.height:
            self.curline -= self.height
        else:
            self.curline = 0

    def cursor_page_down(self):
        self.curline += self.height
        self.bounds_check()

    def bounds_check(self):
        if self.curline > (self.nlist - 1):
            self.curline = self.nlist - 1
        if self.curline < 0:
            self.curline = 0
        if self.nlist == 0:
            self.curline = 0

NLIST = 100
HEIGHT = 11

if __name__ == '__main__':
    t = Timelog(NLIST, HEIGHT)
    t.load_file('test01.log')
    time.sleep(5)
    t.do_start_stop()
    time.sleep(65)
    t.do_start_stop()
    time.sleep(115)
    t.do_start_stop()
    t.save_file('test01.log')

