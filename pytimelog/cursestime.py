#!/usr/bin/env python

# wdw 6 aug '15 ascii/curses version

# https://docs.python.org/2/howto/curses.html#curses-howto

NLIST = 100
HEIGHT = 11

import curses, time
from pytimelog import Timelog

def do_topmenu(t, w):
    w.clear(); w.refresh()
    curses.curs_set(1) # show cursor
    w.addstr(20, 1, "1: file, 2: settings, 3: Parse, 4: Quit.? ")
    w.refresh()
    time.sleep(1)
    curses.curs_set(0) # hide cursor

def do_note(t, w):
    print "do note: fixme"
    time.sleep(1)

def key_in(t, w, c):
        if c == curses.KEY_F2:
            do_note(t, w)
        elif c == curses.KEY_F4:
            t.do_new_week()
        elif c == curses.KEY_F6:
            t.do_new_day()
        elif c == curses.KEY_F8:
            t.do_start_stop()
        elif c == curses.KEY_UP:
            t.cursor_up()
        elif c == curses.KEY_DOWN:
            t.cursor_down()
        elif c == curses.KEY_NPAGE:
            t.cursor_page_up()
        elif c == curses.KEY_PPAGE:
            t.cursor_page_down()
        elif c == curses.KEY_HOME:
            t.cursor_home()
        elif c == curses.KEY_END:
            t.cursor_end()
        elif (c < 256) and ( chr(c) in 'Mm' ) :
            #print "mmm???"
            #curses.beep()
            #time.sleep(1)
            do_topmenu(t, w)
        elif (c < 256) and ( chr(c) in 'Qq' ) :
            return True
        else:
            print "???"
            curses.beep()
            time.sleep(1)
        return False

def display(t, w):
    w.clear(); w.refresh()
    curses.curs_set(0) # hide cursor
    head1, head2 = t.heading()
    w.addstr(0, 1, head1)
    w.addstr(1, 1, head2)
    for i in range(HEIGHT):
        if (i + t.curline) < t.nlist:
            item = t.timelist[ i + t.curline ]
            line = item[0]
            line = '%d %d %s' % (t.curline, t.nlist, line)
            w.addstr(i+3, 1, ': ' + line)

    line = "q: quit, m: menu, F2: note, F4: new week, F6: new day, F8: start/stop"
    w.addstr(i+4, 1, '  ' + line)
    w.addstr(i+5, 1, '  ')

def main(w):
    w.nodelay(1)
    t = Timelog(NLIST, HEIGHT)
    t.load_file('test01.log')
    while True:
        display(t, w)
        c = w.getch()
        if c < 0:
            time.sleep(.100) # FIXME
            continue
        if key_in(t, w, c):
            break;

    if t.changed:
        t.save_file('test01.log')

if __name__ == '__main__':
    curses.wrapper(main)

