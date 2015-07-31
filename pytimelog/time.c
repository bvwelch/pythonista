/*
   bw 22 may 94 time.c for HP95      
   
Notes:

   The program is somewhat non-standard (at least for the hp95) in its usage
   of files.  It is not assumed that the entire file will necessarily fit
   into memory.  So, when OPENING a large file, only the last NLIST records
   are available.  Also, when SAVING a file, any "new" records are merely
   appended to the existing file.  This might cause confusion if the user is
   try to "backup" his existing file by saving it under a new name.  In that
   situation, a new file is created, containing only the "new" records.

   For this program, the formula for overtime is: overtime = hrs > 40/wk

   The over-all layout of the program was inspired by the paper
   "Anatomy of an Application" by Craig A. Finseth

   todo: in place editing, clipboard, holiday, vacation, help key, fixups
*/

/*              "1234567890123456789012345678901234567890"         */

#define VERSION "Time V2.1"

#include "\bill\hp95\src\hp95dev\headers\interfac.h"
#include "\bill\hp95\src\hp95dev\headers\event.h"
#include "\bill\hp95\src\hp95dev\headers\fileio.h"
#include "\bill\hp95\src\hp95dev\headers\edit.h"
#include "\bill\hp95\src\hp95dev\headers\menu.h"
#include "\bill\hp95\src\hp95dev\headers\fmenu.h"
#include "\bill\hp95\src\hp95dev\headers\smtime.h"

/*
  these would normally come from C-library's include files, but I don't
  want to take a chance on the C compiler causing any fixup trouble, or
  clashes with HP's include files.
*/
#define NULL (char *) 0
void sprintf();
int sscanf();
void *memcpy(void *, void *, int);
void *memset(void *, int c, int count);
char *strcpy(char *, char *);
int strlen(char *);

#define NLIST 100
#define MAXLEN 100
#define HEIGHT 11
#define SCRWIDTH 40
#define ULONG unsigned long
#define MAX_FILES 30
#define FM_BUF_SIZE ( MAX_FILES * (sizeof (FILEINFO) ) )
#define DEFPATH "C:\\_DAT"
#define DEFFILE "*.LOG"

struct list {
  int new;
  char buf[MAXLEN];
} list[NLIST];
unsigned int nlist;
unsigned int curline;

char *defaultfile = "C:\\_DAT\\time.log";

char myfile[80];
FILE myfile_struct;
FILE *fp = &myfile_struct;
FILEINFO fmbuffer[MAX_FILES];

int yadj = 0;
int app_done;
int changed;

/*
  these variables are stored in the file ( "V" lines)
*/
ULONG yrtotal;    /* in secs */
ULONG wktotal;    /* in secs */
ULONG daytotal;   /* in secs */
ULONG start_time; /* in secs */
int working;

void heading();
void display();
void refresh();
void key_in(unsigned int);
void do_topmenu();
void do_start_stop();
void do_new_week();
void do_new_day();
void do_note();
void do_settings();
void do_vline();
void do_filemenu();
void load_file();
void save_file();
void add_item(char *, int);
ULONG calc_ovr(ULONG wktotal, ULONG delta);
ULONG get_time();
char * get_date_time_str();
char * get_date_str();
int msg(char *);
int get_str(char *, char *, char *);
int getmenu(char *, int);
void get_filename(char *, char *, char *, char *);
char *fgets(char *buf, int n, FILE *fp);
void fputs(char *s, FILE *fp);
void hidecursor();

void
main(void)
{
  EVENT e;
  int tick = ~0;

  m_init();

  start_time = get_time();  /* default value */

  strcpy(myfile, defaultfile);
  load_file();

  refresh();

  e.kind = E_KEY;
  do {
    if (curline > (nlist - 1)) curline = nlist - 1;
    if (nlist == 0) curline = 0;

    if (e.kind == E_KEY) display();

    m_event(&e);
    switch (e.kind) {
    case E_NONE:
      tick++;
      tick &= 31;
      if (tick == 0) heading();
      m_posttime();
      break;
    case E_ACTIV:
      refresh();
      display();
      break;
    case E_DEACT:
      tick = ~0;         /* force new heading when we get back */
      break;
    case E_KEY:
      key_in(e.data);
      break;
    }

  } while (!app_done && (e.kind != E_TERM));

  if (changed) {
    save_file();
  }

  m_fini();
}

void
heading()
{
  char *head;
  static ULONG delta, yrt, wkt, wmin, dt, dhr, dmin, dsec, bhr, bmin, bsec, togo, tgmin, tghr;
  static char buf1[MAXLEN], buf2[MAXLEN];
  int len;

  delta = get_time() - start_time;

  if (working) {
    head = "WRK";
    wkt = wktotal + delta;
    dt = daytotal + delta;
    yrt = yrtotal + calc_ovr(wkt, delta);
  } else {
    head = "BRK";
    yrt = yrtotal;
    wkt = wktotal;
    dt = daytotal;
  }

  wmin = (wkt % 3600L) / 60L;
  wmin %= 60L;

  dhr = dt / 3600L;
  dmin = (dt % 3600L) / 60L;
  dsec = dt % 60L;
  if (dsec >= 30L) dmin++;
  if (dmin >= 60L) dhr++;
  dmin %= 60L;

  bhr = delta / 3600L;
  bmin = (delta % 3600L) / 60L;
  bsec = delta % 60L;
  if (bsec >= 30L) bmin++;
  if (bmin >= 60L) bhr++;
  bmin %= 60L;

  togo = wkt / 28800L;
  togo *= 28800L;
  togo = wkt - togo;
  togo = 28800L - togo;
  tghr = togo / 3600L;
  tgmin = (togo % 3600L) / 60L;

  hidecursor();

  sprintf(buf1, "%s   %2d:%02d", VERSION, (int) tghr, (int) tgmin);
  memset(buf2, ' ', SCRWIDTH);
  len = strlen(buf1);
  if (len > SCRWIDTH) {
    memcpy(buf2, buf1, SCRWIDTH);
  } else {
    memcpy(buf2, buf1, len);
  }
  m_disp(-3, 0, buf2, SCRWIDTH, 0, 0);

  sprintf(buf1,  "OVR:%3d WK: %2d:%02d DAY: %02d:%02d %s: %02d:%02d",
         (int) (yrt/3600L), (int) (wkt/3600L), (int) wmin,
         (int) dhr, (int) dmin, head, (int) bhr, (int) bmin);

  memset(buf2, ' ', SCRWIDTH);
  len = strlen(buf1);
  if (len > SCRWIDTH) {
    memcpy(buf2, buf1, SCRWIDTH);
  } else {
    memcpy(buf2, buf1, len);
  }
  m_disp(-2, 0, buf2, SCRWIDTH, 0, 0);

  memset(buf2, 0xCD, SCRWIDTH);
  m_disp(-1, 0, buf2, SCRWIDTH, 0, 0);
}

void
display()
{
  unsigned int i, len;
  char *p;
  static char linebuf[MAXLEN];

  m_clear(-3, 0, 16, SCRWIDTH);
  heading();

  for (i=0; (i < HEIGHT) && ((i + curline) < nlist); i++) {
    p = list[curline+i].buf;
    len = strlen(p);
    if (len > SCRWIDTH) len = SCRWIDTH;
    memset(linebuf, ' ', SCRWIDTH);
    memcpy(linebuf, p, len);
    m_disp(yadj + i, 0, linebuf, SCRWIDTH, 0, 0);
  }

  if (i<HEIGHT) {
    m_clear(yadj + i, 0, HEIGHT - (yadj + i), SCRWIDTH);
  }

  m_disp(11, 0,   "            New     New                 ", SCRWIDTH, 1, 0);

  if (working) {
    m_disp(12, 0, "    Note    Week    Day     Stop        ", SCRWIDTH, 1, 0);
  } else {
    m_disp(12, 0, "    Note    Week    Day     Start       ", SCRWIDTH, 1, 0);
  }
}

void
refresh()
{
}

void
key_in(unsigned int key)
{
  switch (key) {
  case 0xc800:                      /* MENU */
  case 0x8500:                      /* F11 (for use in app95) */
   do_topmenu();
   break;
  case 0x3c00:			    /* F2 */
    do_note();
    break;
  case 0x3e00:			    /* F4 */
    do_new_week();
    break;
  case 0x4000:			    /* F6 */
    do_new_day();
    break;
  case 0x4200:			    /* F8 */
    do_start_stop();
    break;
  case 0x4700:                      /* home */
    curline = 0;
    break;
  case 0x4f00:                      /* end */
    curline = nlist - 1;
    break;
  case 0x4800:                      /* up */
    if (curline >= 1) curline--;
    break;
  case 0x5000:                      /* down */
    curline++;
    break;
  case 0x4900:                      /* pg up */
    if (curline >= HEIGHT) {
      curline -= HEIGHT;
    } else {
      curline = 0;
    }
    break;
  case 0x5100:                      /* pg down */
    curline += HEIGHT;
    break;
  default:
    m_thud();
    break;
  }
}

void
do_topmenu()
{
  int choice;

  choice = getmenu("File\0Settings\0Parse\0Quit", 4);
  if (choice == -1) return;

  switch (choice) {
  case 0:
    do_filemenu();
    break;
  case 1:
    do_settings();
    break;
  case 2:
    do_vline();
    break;
  case 3:
    app_done = 1;
    break;
  }
}

void
do_start_stop()
{
  ULONG delta, hr, min, sec, cur_time;
  char *head;
  static char buf1[MAXLEN];

  cur_time = get_time();
  delta = cur_time - start_time;

  if (working) {
    wktotal += delta;
    daytotal += delta;
    yrtotal += calc_ovr(wktotal, delta);
    head = "E";
    working = 0;
  } else {
    head = "B";
    working = 1;
  }

  start_time = cur_time;
  hr = delta / 3600L;
  min = (delta % 3600L) / 60L;
  sec = delta % 60L;
  if (sec >= 30L) min++;
  if (min >= 60L) hr++;
  min %= 60L;

/*
  note: "working" has been toggled above 
*/

  if (working) {
    sprintf(buf1, "%s         %s, %02d:%02d", head, get_date_time_str(), 
                                          (int) hr, (int) min);
  } else {
    sprintf(buf1, "%s            %s, %02d:%02d", head, get_date_time_str(), 
                                          (int) hr, (int) min);
  }

  add_item(buf1, 1);
}

void
do_new_week()
{
  ULONG hr, min, sec;
  char *s;
  static char buf1[MAXLEN];

  if (working) {
    msg("Sorry, you must do a STOP first");
    return;
  }
  hr = wktotal / 3600L;
  min = (wktotal % 3600L) / 60L;
  sec = wktotal % 60L;
  if (sec >= 30L) min++;
  if (min >= 60L) hr++;
  min %= 60L;
  s = get_date_str();
  sprintf(buf1, "WT %02d:%02d, %s", (int) hr, (int) min, s);
  add_item(buf1, 1);
  strcpy(buf1, " ");
  add_item(buf1, 1);
  wktotal = 0L;
}

void
do_new_day()
{
  ULONG hr, min, sec;
  char *s;
  static char buf1[MAXLEN];

  if (working) {
    msg("Sorry, you must do a STOP first");
    return;
  }
  hr = daytotal / 3600L;
  min = (daytotal % 3600L) / 60L;
  sec = daytotal % 60L;
  if (sec >= 30L) min++;
  if (min >= 60L) hr++;
  min %= 60L;
  s = get_date_str();
  sprintf(buf1, "DT %02d:%02d, %s", (int) hr, (int) min, s);
  add_item(buf1, 1);
  strcpy(buf1, " ");
  add_item(buf1, 1);
  daytotal = 0L;
}

void
do_note()
{
  static char buf1[MAXLEN];

  if (get_str("Note", buf1, "") != 0) add_item(buf1, 1);
}

void
do_settings()
{
  int choice, stat;
  ULONG hr, min, sec;
  static char buf1[MAXLEN], buf2[MAXLEN];

  if (working) {
    msg("Sorry, you must do a STOP first");
    return;
  }
  choice = getmenu("Overtime\0Weekly\0Daily\0Both", 4);
  if (choice == -1) return;

  switch (choice) {
  case 0:
    hr = yrtotal / 3600L;
    min = (yrtotal % 3600L) / 60L;
    sec = yrtotal % 60L;
    if (sec >= 30L) min++;
    if (min >= 60L) hr++;
    min %= 60L;
    sprintf(buf2, "%d:%02d", (int) hr, (int) min);
    memset(buf1, MAXLEN, 0);
    if (get_str("Overtime:", buf1, buf2) != 0) {
      stat = sscanf(buf1, "%ld:%ld", &hr, &min);
      if (stat != 2) {
        m_thud();
        break;
      }
      yrtotal = (hr * 3600L) + (min * 60L);
      sprintf(buf1, "; Changed overtime to %lx", yrtotal);
      add_item(buf1, 1);
    }
    break;
  case 1:
    hr = wktotal / 3600L;
    min = (wktotal % 3600L) / 60L;
    sec = wktotal % 60L;
    if (sec >= 30L) min++;
    if (min >= 60L) hr++;
    min %= 60L;
    sprintf(buf2, "%d:%02d", (int) hr, (int) min);
    memset(buf1, MAXLEN, 0);
    if (get_str("Weekly Total:", buf1, buf2) != 0) {
      stat = sscanf(buf1, "%ld:%ld", &hr, &min);
      if (stat != 2) {
        m_thud();
        break;
      }
      wktotal = (hr * 3600L) + (min * 60L);
      sprintf(buf1, "; Changed weekly total to %lx", wktotal);
      add_item(buf1, 1);
    }
    break;
  case 2:
    hr = daytotal / 3600L;
    min = (daytotal % 3600L) / 60L;
    sec = daytotal % 60L;
    if (sec >= 30L) min++;
    if (min >= 60L) hr++;
    min %= 60L;
    sprintf(buf2, "%02d:%02d", (int) hr, (int) min);
    memset(buf1, MAXLEN, 0);
    if (get_str("Daily Total:", buf1, buf2) != 0) {
      stat = sscanf(buf1, "%ld:%ld", &hr, &min);
      if (stat != 2) {
        m_thud();
        break;
      }
      daytotal = (hr * 3600L) + (min * 60L);
      sprintf(buf1, "; Changed daily total to %lx", daytotal);
      add_item(buf1, 1);
    }
    break;
  case 3:
    choice = getmenu("Advance\0Backup", 2);
    if (choice == -1) return;
    if (choice == 0) {
      memset(buf1, MAXLEN, 0);
      if (get_str("Amount to Advance:", buf1, "00:30") == 0) break;
      stat = sscanf(buf1, "%ld:%ld", &hr, &min);
      if (stat != 2) {
        m_thud();
        break;
      }
#if 0
      start_time += (hr * 3600L) + (min * 60L);
#endif
      wktotal += (hr * 3600L) + (min * 60L);
      daytotal += (hr * 3600L) + (min * 60L);
      sprintf(buf1, "; Advanced both %d:%02d", (int)hr, (int)min);
    } else {
      memset(buf1, MAXLEN, 0);
      if (get_str("Amount to Backup:", buf1, "00:30") == 0) break;
      stat = sscanf(buf1, "%ld:%ld", &hr, &min);
      sprintf(buf1, "; Backup both %d:%02d", (int)hr, (int)min);
      if (stat != 2) {
        m_thud();
        break;
      }
#if 0
      start_time -= (hr * 3600L) + (min * 60L);
#endif
      wktotal -= (hr * 3600L) + (min * 60L);
      daytotal -= (hr * 3600L) + (min * 60L);
    }
#if 0
    sprintf(buf1, "; Changed starting time to %lx", start_time);
#endif
    add_item(buf1, 1);
    break;
  }
}

void
do_vline()
{
  static ULONG xyrtotal, xwktotal, xdaytotal, xstart_time;
  static ULONG yhr, ymin, whr, wmin, dhr, dmin;
  static char buf1[MAXLEN];
  char *p;
  int xworking;

  p = list[curline].buf;
  if (*p != 'V') return;
  sscanf(p, "V %lx %lx %lx %lx %d", &xyrtotal, &xwktotal, &xdaytotal,
                                              &xstart_time, &xworking);
  yhr = xyrtotal / 3600L;
  ymin = (xyrtotal % 3600L) / 60L;
  if (ymin >= 60L) yhr++;
  ymin %= 60L;

  whr = xwktotal / 3600L;
  wmin = (xwktotal % 3600L) / 60L;
  if (wmin >= 60L) whr++;
  wmin %= 60L;

  dhr = xdaytotal / 3600L;
  dmin = (xdaytotal % 3600L) / 60L;
  if (dmin >= 60L) dhr++;
  dmin %= 60L;

  sprintf(buf1, "OVR: %d:%02d WK: %d:%02d DAY: %d:%02d",
			(int)yhr, (int)ymin, (int)whr, (int)wmin,
                        (int)dhr, (int)dmin);
  msg(buf1);
 }

void
do_filemenu()
{
  int choice, key;
  static char buf1[MAXLEN];

  choice = getmenu("Open\0Save", 2);
  if (choice == -1) return;

  if (choice == 0) {
    if (changed != 0) {
      key = msg("Replace file without saving? (Y/N)");
      if ((key != 'Y') && (key != 'y')) return;
    }
    get_filename("File to open:", DEFPATH, DEFFILE, buf1);
  } else {
    get_filename("File to save:", DEFPATH, DEFFILE, buf1);
  }

  if (strlen(buf1) == 0) return;
  strcpy(myfile, buf1);

  if (choice == 0) {
    load_file();
  } else {
    save_file();
  }
}

/*
  Load file into memory.  If file has too many records, just keep the records
  at the tail-end of the file.
*/
void
load_file()
{
  unsigned int i, stat;
  char *p;
  static char buf1[MAXLEN];

  nlist = 0;

  stat = m_openro(fp, myfile, strlen(myfile), 0, 0);
  if (stat != 0) {
    msg("load_file: Can't open log file");
    return;
  }

  while (fgets(buf1, MAXLEN-1, fp) != NULL) {
    add_item(buf1, 0);
  }

  m_close(fp);

  changed = 0;

  for (i=0; i<nlist; i++) {
    p = list[i].buf;
    if (*p == 'V') {
      sscanf(p, "V %lx %lx %lx %lx %d", &yrtotal, &wktotal, &daytotal,
                                        &start_time, &working);
    }
  }
}

/*
  Append any new records to the file.  Create a "V" record and store it
  in the file.
*/
void
save_file()
{
  unsigned int i, stat;
  static char buf1[MAXLEN];

  stat = m_open(fp, myfile, strlen(myfile), 0, 0);
  if (stat != 0) {
    stat = m_create(fp, myfile, strlen(myfile), 0, 0);
    if (stat != 0) {
      msg("save_file: Can't open or create log file");
      return;
    }
  }

  m_seek(fp, seek_end, 0L);

  sprintf(buf1, "V  %lx %lx %lx %lx %d", yrtotal, wktotal, daytotal,
                                         start_time, working);
  add_item(buf1, 1);
  strcpy(buf1, " ");
  add_item(buf1, 1);

  for (i=0; i<nlist; i++) {
    if (list[i].new) {
      fputs(list[i].buf, fp);
      list[i].new = 0;
    }
  }

  m_close(fp);

  changed = 0;
}

/*
  add an entry, and mark it "new" or "old".  If there is no room, discard
  the first entry to make room.
*/
void
add_item(char *s, int new)
{
  int i;

  if (nlist >= NLIST) {
    for (i=1; i<NLIST; i++) {
      strcpy(list[i-1].buf, list[i].buf);
      list[i-1].new = list[i].new;
    }
    nlist = NLIST - 1;
  }

  if (strlen(s) > MAXLEN-1) {
    memcpy(list[nlist].buf, s, MAXLEN-1);
    list[nlist].buf[MAXLEN-1] = '\0';
  } else {
    strcpy(list[nlist].buf, s);
  }
  list[nlist].new = new;

  nlist++;
  if (nlist > HEIGHT) curline = nlist - HEIGHT;
  if (new) changed = 1;
}

/*
  calculate incremental amount of overtime.
*/
ULONG
calc_ovr(ULONG wktotal, ULONG delta)
{
  ULONG ovr;

  ovr = 0L;
  if (wktotal > 40L*3600L) {
    ovr = wktotal - 40L*3600L;
    if (ovr > delta) ovr = delta;
  }
  return (ovr);
}

/*
  derived from K&R, 1st Ed, pg 104
  needs design review !
*/
ULONG
get_time()
{
  static int day_tab[2][13] = {
	{ 0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 },
	{ 0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 } };
  DTM dtmp;
  ULONG t;
  unsigned int i, leap, day, year, month;

  m_getdtm(&dtmp);
  year = (unsigned int) dtmp.dt_year;
  month = (unsigned int) dtmp.dt_month;
  day = (unsigned int) (dtmp.dt_date - 1L);

  leap = year%4 == 0 && year%100 != 0 || year%400 == 0;
  for (i=1; i<month; i++)
    day += day_tab[leap][i];

  for (i=1980; i<year; i++) {
    day += 365;
    leap = year%4 == 0 && year%100 != 0 || year%400 == 0;
    if (leap) day++;
  }

  t = ((ULONG) day * 24L * 3600L) + (dtmp.dt_hour * 3600L) +
                                    (dtmp.dt_minute * 60L) + dtmp.dt_second;
  return (t);
}

char *
get_date_time_str()
{
  int i;
  DTM dtmp;
  char far *p;
  static char buf1[MAXLEN];

  m_getdtm(&dtmp);
  p = m_tell_anytime(2, 0, 0, NULL, &dtmp);

  for (i=0; i<SCRWIDTH-1; i++) {
    buf1[i] = *p++;
    if (buf1[i] == '\0') break;
  }
  buf1[i] = '\0';

  return (buf1);
}

char *
get_date_str()
{
  int i;
  DTM dtmp;
  char far *p;
  static char buf1[MAXLEN];

  m_getdtm(&dtmp);
  p = m_tell_anytime(0, 0, 0, NULL, &dtmp);

  for (i=0; i<SCRWIDTH-1; i++) {
    buf1[i] = *p++;
    if (buf1[i] == '\0') break;
  }
  buf1[i] = '\0';

  return (buf1);
}

/*
  Finseth's GetKey
*/
int
msg(char *s)
{
  EVENT e;

  m_lock();
  message(s, strlen(s), "", 0);
  do m_event(&e); while (e.kind != E_KEY);
  msg_off();
  m_unlock();
  return (e.data);
}

/*
  derived from Finseth's GetStr
*/
int
get_str(char *prompt, char *buf, char *def)
{
  EDITDATA ed;
  EVENT e;
  int note_done = 0;
  int ok = 1;
  int result;

  edit_top(&ed, def, strlen(def), MAXLEN-1, prompt, strlen(prompt), "", 0);
  e.kind = E_KEY;
  while (!note_done) {
    if ((e.kind == E_KEY) || (e.kind == E_ACTIV)) edit_dis(&ed);
    m_event(&e);
    switch (e.kind) {
    case E_ACTIV:
      refresh();
      display();
      break;
    case E_TERM:
      app_done = 1;
      note_done = 1;
      ok = 0;
      break;
    case E_BREAK:
      note_done = 1;
      ok = 0;
      break;
    case E_KEY:
      if (e.data == 0x1b) {
        note_done = 1;
        ok = 0;
      } else {
        edit_key(&ed, e.data, &result);
        if (result == 1) note_done = 1;
      }
      break;
    }
  }
  display();
  if (!ok) return (0);
  strcpy(buf, ed.edit_buffer);
  return (1);
}

/*
  derived from Finseth's GetMenu
*/
int
getmenu(char *mstr, int cnt)
{
  MENUDATA u;
  EVENT e;
  int which = 0;
  int menu_done = 0;
  static char buf1[MAXLEN], buf2[MAXLEN];

  menu_setup(&u, mstr, cnt, 1, NULL, 0, NULL);
  hidecursor();
  menu_on(&u);

  e.kind = E_KEY;
  while (!menu_done) {
    if (e.kind == E_KEY || e.kind == E_ACTIV) {
      menu_dis(&u);
      memset(buf2, 0xCD, SCRWIDTH);
      m_disp(-1, 0, buf1, SCRWIDTH, 0, 0);
    }
    m_event(&e);
    switch (e.kind) {
    case E_ACTIV:
      refresh();
      display();
      break;
    case E_TERM:
      app_done = 1;
      menu_done = 1;
      break;
    case E_KEY:
      if (e.data == 0x1b) {
        which = -1;
        menu_done = 1;
      } else {
        menu_key(&u, e.data, &which);
        if (which != -1) menu_done = 1;
      }
      break;
    }
  }
  menu_off(&u);
  if (app_done) return (-1);
  return (which);
}

void
get_filename(char *prompt, char *path, char *pattern, char *result)
{
  static FMENU f;
  static EDITDATA ed;
  static EVENT e;
  int which = 0;
  int fmenu_done = 0;
  int stat = RET_ABORT;

  strcpy(result, "");

  f.fm_path = (char far *) path;
  f.fm_pattern = (char far *) pattern;
  f.fm_buffer = (FILEINFO far *) fmbuffer;
  f.fm_buf_size = FM_BUF_SIZE;
  f.fm_startline = -2;
  f.fm_startcol = 0;
  f.fm_numlines = 13;
  f.fm_numcols = SCRWIDTH;
  f.fm_filesperline = 3;

  ed.prompt_window = 1;
  ed.prompt_line_length = 0;
  ed.message_line = (char far *) prompt;
  ed.message_line_length = strlen(prompt);

  m_clear(-3, 0, 14, SCRWIDTH);

  fmenu_init(&f, &ed, "", 0, 0);

  hidecursor();
  e.kind = E_KEY;
  while (!fmenu_done) {
    if (e.kind == E_KEY || e.kind == E_ACTIV) {
      fmenu_dis(&f, &ed);
    }
    m_event(&e);
    switch (e.kind) {
    case E_ACTIV:
      refresh();
      break;
    case E_TERM:
      app_done = 1;
      fmenu_done = 1;
      break;
    case E_BREAK:
      stat = RET_ABORT;
      fmenu_done = 1;
      break;
    case E_KEY:
      if (e.data == 0x1b) {
        stat = RET_ABORT;
        fmenu_done = 1;
      } else {
        stat = fmenu_key(&f, &ed, e.data);
        switch (stat) {
        case RET_UNKNOWN:
        case RET_BAD:
          m_thud();
          break;
        case RET_ACCEPT:
        case RET_ABORT:
          fmenu_done = 1;
          break;
        }
      }
      break;
    }
  }
  fmenu_off(&f, &ed);
  display();
  if (app_done) return;
  if (stat == RET_ABORT) return;
  strcpy(result, ed.edit_buffer);
}

/*
 derived from K&R 1st Ed, pg 155
 but kludged to remove the trailing '\n'
*/

char *
fgets(char *s, int n, FILE *fp)
{
  int stat, len;
  char c, *cs;

  cs = s;
  while (--n > 0) {
    stat = m_read(fp, &c, 1, &len);
    if (stat != 0) break;
    if (len != 1) break;
    if (c == '\r') continue;
    if (c == '\n') break;
    *cs++ = c;
  }
  *cs = '\0';
  if ((stat != 0) && (cs == s)) return (NULL);
  if ((len != 1) && (cs == s)) return (NULL);
  return (s);
}

/*
 derived from K&R 1st Ed, pg 156
 but kludged to add the trailing '\r\n'
*/

void
fputs(char *s, FILE *fp)
{
  char c;

  while (c = *s++) {
    m_write(fp, &c, 1);
  }

  m_write(fp, "\r\n", 2);
}

void
hidecursor()
{
  _asm {
  mov ah, 1
  mov cx, 0ff00h
  int 10h
  }
}

