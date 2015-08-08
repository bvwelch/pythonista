#!/usr/bin/env python

# wdw 6 aug '15 ascii/curses version

# https://docs.python.org/2/howto/curses.html#curses-howto

NLIST = 100
HEIGHT = 11

import curses, time
from pytimelog import Timelog

def display(t, w):
    w.clear(); w.refresh()
    curses.curs_set(0) # hide cursor
    head1, head2 = t.heading()
    w.addstr(0, 1, head1)
    w.addstr(1, 1, head2)
    for i in range(HEIGHT):
        n = i + t.curline
        if n < t.nlist:
            item = t.timelist[ n ]
            line = item[0]
            line = '%02d: %s' % (n, line)
            w.addstr(i+3, 1, line)

    line = " q: quit, m: menu, F2: note, F4: new week, F6: new day, F8: start/stop"
    w.addstr(i+4, 1,  line)
    w.addstr(i+5, 1, '  ')

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
            t.cursor_page_down()
        elif c == curses.KEY_PPAGE:
            t.cursor_page_up()
        elif c == curses.KEY_HOME:
            t.cursor_home()
        elif c == curses.KEY_END:
            t.cursor_end()
        elif (c < 256) and ( chr(c) in 'Mm' ) :
            do_topmenu(t, w)
        elif (c < 256) and ( chr(c) in 'Qq' ) :
            return True
        else:
            print "???"
            curses.beep()
            time.sleep(1)
        return False

def do_topmenu(t, w):
    c = msg(w, "1: file, 2: settings, 3: Parse. ? ")
    if (c < 256) and ( chr(c) == '1' ) :
        do_filemenu(t, w)
    elif (c < 256) and ( chr(c) == '2' ) :
        do_settings(t, w)
    elif (c < 256) and ( chr(c) == '3' ) :
        line = t.do_parse_vline()
        msg(w, line)

def do_filemenu(t, w):
    c = msg(w, "1: open, 2: save. ? ")
    if (c < 256) and ( chr(c) == '1' ) :
        fname = get_str(w, "file to open: ")
        t.load_file(fname)
    elif (c < 256) and ( chr(c) == '2' ) :
        fname = get_str(w, "save file as: ")
        t.save_file(fname)

def do_settings(t, w):
    c = msg(w, "1: Overtime, 2: Weekly, 3: Daily, 4:Both. ? ")
    if (c < 256) and ( chr(c) == '1' ) :
        hr, min = t.get_ovr_settings()
        hr, min = get_hr_min(w, 'Overtime', hr, min)
        t.put_ovr_settings(hr, min)
    elif (c < 256) and ( chr(c) == '2' ) :
        hr, min = t.get_weekly_settings()
        hr, min = get_hr_min(w, 'Overtime', hr, min)
        t.put_weekly_settings(hr, min)
    elif (c < 256) and ( chr(c) == '3' ) :
        hr, min = t.get_daily_settings()
        hr, min = get_hr_min(w, 'Overtime', hr, min)
        t.put_daily_settings(hr, min)
    elif (c < 256) and ( chr(c) == '4' ) :
        c = msg(w, "1: Advance, 2: Backup. ? ")
        if (c < 256) and ( chr(c) == '1' ) :
            hr, min = get_hr_min(w, 'Amount to advance', 0, 30)
            t.do_advboth_settings(hr, min)
        elif (c < 256) and ( chr(c) == '2' ) :
            hr, min = get_hr_min(w, 'Amount to backup', 0, 30)
            t.do_bckboth_settings(hr, min)

def get_hr_min(w, prompt, hr, min):
    reply = get_str(w, '%s: %02d:%02d ? ' % (prompt, hr, min) )
    if not reply:
        return [hr, min]
    reply = reply.strip()
    reply = reply.split(':')
    try:
        p1 = int(reply[0])
        p2 = int(reply[1])
        return [p1, p2]
    except:
        msg(w, "error: expect hr:min")
        return [hr, min]

def do_note(t, w):
    line = get_str(w, "Note: ")
    t.do_note('; ' + line)

def get_str(w, prompt):
    w.nodelay(0)
    curses.echo()
    w.clear()
    curses.curs_set(1) # show cursor
    w.addstr(3, 1, prompt)
    w.refresh()
    reply = w.getstr()
    w.clear()
    curses.curs_set(0) # hide cursor
    w.refresh()
    w.nodelay(1)
    curses.noecho()
    return reply

def msg(w, s):
    w.nodelay(0)
    w.clear()
    curses.curs_set(1) # show cursor
    w.addstr(3, 1, s)
    w.refresh()
    c = w.getch()
    w.clear()
    curses.curs_set(0) # hide cursor
    w.refresh()
    w.nodelay(1)
    return c

def main(w):
    w.nodelay(1)
    t = Timelog(NLIST, HEIGHT)
    t.load_file('')
    while True:
        display(t, w)
        c = w.getch()
        if c < 0:
            time.sleep(.100) # FIXME
            continue
        if key_in(t, w, c):
            break;

    if t.changed:
        t.save_file('')

if __name__ == '__main__':
    curses.wrapper(main)

