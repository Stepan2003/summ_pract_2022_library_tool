import sqlite3
import tkinter.ttk
from tkinter.ttk import Treeview
from tkinter.messagebox import showwarning
from tkinter import filedialog
from tkinter import *
from var import *


def isDigitList(l):
    for x in l:
        if not x.replace(' ', '').isdigit():
            return False
    return True



def init_db():
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS books(
           id INTEGER PRIMARY KEY,
           author TEXT,
           name TEXT,
           year INT,
           amount INT,
           avaliavable_amount INT,
           genre TEXT,
           comment TEXT);
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS books_students(
           id INTEGER PRIMARY KEY,
           student_id INT,
           book_id TEXT,
           amount INT,
           date_took TEXT,
           date_back TEXT,
           comment TEXT);
        """)
    cur.execute("""CREATE TABLE IF NOT EXISTS students(
           id INTEGER PRIMARY KEY,
           fio TEXT,
           class TEXT);
            """)
    conn.commit()

def placeLabel(wnd, text = 'None', font = None, background=None,
               side = None, fill = None, expand = None, anchor = None,
               padx = gl_padx, pady = gl_pady, ipadx = None, ipady = None,
               is_pack=True):
    lbl = Label(wnd, text = text, font=font, background=background)
    if is_pack:
        lbl.pack(side = side, fill=fill, expand=expand, anchor=anchor,
                 padx = padx, pady = pady, ipadx = ipadx, ipady = ipady)
    return lbl

def placeButton(wnd, text = 'None', font = None, command = None, bg = 'white', width=None, height=None,
                side = None, fill = None, expand = None, anchor = None,
                padx = gl_padx, pady = gl_pady, ipadx = None, ipady = None,
                is_pack=True):
    btn = Button(wnd, text = text, font=font, command=command, bg=bg, width=width, height=height,
                 activebackground='#345',activeforeground='white')
    if is_pack:
        btn.pack(side = side, fill=fill, expand=expand, anchor=anchor,
             padx = padx, pady = pady, ipadx = ipadx, ipady = ipady)
    return btn

def placeEntry(wnd, text = 'None', width = None, textvariable = None,
                side = None, fill = None, expand = None, anchor = None,
                padx = gl_padx, pady = gl_pady, ipadx = None, ipady = None,
               is_pack=True):
    entry = Entry(wnd, text = text, width=width, textvariable=textvariable)
    if is_pack:
        entry.pack(side = side, fill=fill, expand=expand, anchor=anchor,
                 padx = padx, pady = pady, ipadx = ipadx, ipady = ipady)
    return entry


def compare_two_tuples(f, b, is_strict_filter):
    c = 0
    if is_strict_filter:
        for i in range(len(f)):
            try:
                if compare_two_words(str(f[i]), str(b[i])) or str(f[i]) == '':
                    c += 1
            except: pass
        if c == len(b):
            return True
        return False
    else:
        for i in range(len(f)):
            try:
                if (str(b[i]).lower()).find(f[i].lower()) != -1 or str(f[i]) == '':
                    c += 1
            except: pass
        if c == len(b):
            return True
        return False

def compare_two_words(f,b):
    f, b = str(f).capitalize(), str(b).capitalize()
    try:
        for i in range(len(f)):
            if f[i] != b[i]:
                return False
        else: return True
    except: return False
