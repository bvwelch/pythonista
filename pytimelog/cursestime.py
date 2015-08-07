#!/usr/bin/env python

# wdw 6 aug '15 ascii/curses version

# https://docs.python.org/2/howto/curses.html#curses-howto

NLIST = 100
HEIGHT = 11

import curses, time
from pytimelog import Timelog

def do_topmenu(w):
    print "topmenu: fixme"
    time.sleep(1)

def do_note(w):
    print "do note: fixme"
    time.sleep(1)

def key_in(t, w, c):
        if c == curses.KEY_F2:
            do_note(w)
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
            do_topmenu(w)
        elif (c < 256) and ( chr(c) in 'Qq' ) :
            return True
        return False

def display(t, w):
    w.clear()
    head1, head2 = t.heading()
    w.addstr(0, 1, head1)
    w.addstr(1, 1, head2)
    for i in range(HEIGHT):
        if (i + t.curline) < t.nlist:
            item = t.timelist[i]
            line = item[0]
            w.addstr(i+3, 1, ': ' + line)

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

