import sqlite3
import tkinter.ttk
from tkinter.ttk import Treeview
from tkinter.messagebox import askokcancel
from tkinter import filedialog
from tkinter import *
from var import *
from tkinter.font import Font
from tkinter.ttk import Style
from myLibrary import *
import datetime as dt
from PIL import ImageTk, Image
from ttkwidgets.autocomplete import AutocompleteEntryListbox

def get_current_date(s = '%Y.%m.%d'):
    return  dt.datetime.today().strftime(s)

def loadBooksToDb():
    file_name = filedialog.askopenfilename(title='Книги',
        filetypes=(("CSV files", "*.csv"), ("TXT files", "*.txt"), ("All files", "*.*")))
    try:
        with open(file_name) as f:
            l = []
            for el in f.read().split('\n'):
                l.append(el.split(';'))
    except:
        # showwarning('Ошибка', 'Ошибка чтения/обработки файла')
        return False
    l.pop(-1)
    c = 0
    # try:
    conn = sqlite3.connect('library.db')
    for el in l:
        if not isDigitList((el[3], el[4], el[5])):
            showwarning('Ошибка',
                        f'Для ID:{el[0]}; {el[1]}; {el[2]} введены не численные значения в поля «Год, Всего, Доступно» {el[3], el[4], el[5]}\n Загрузка отменена.')
            return False
    for el in l:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO books (author, name, year, amount, avaliavable_amount, genre, comment) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (el[1].strip(), el[2].strip(), el[3].strip(), el[4].strip(), el[5].strip(), el[6].strip(), el[7].strip()))
        c += 1
    conn.commit()
    showwarning('Load books', f'Загружено {c} позиц.')

def loadStudentsToDb():
    file_name = filedialog.askopenfilename(title='Ученики',
        filetypes=(("CSV files", "*.csv"), ("TXT files", "*.txt"), ("All files", "*.*")))
    try:
        with open(file_name) as f:
            l = []
            for el in f.read().split('\n'):
                l.append(el.split(';'))
    except:
        # showwarning('Ошибка', 'Ошибка чтения/обработки файла')
        return False
    l.pop(-1)
    c = 0
    # try:
    conn = sqlite3.connect('library.db')
    for el in l:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO students (fio, class) VALUES (?, ?)",
            (el[1].strip(), el[2].strip()))
        c += 1
    conn.commit()
    showwarning('Load students', f'Загружено {c} учеников.')

# DELETE SIMULATE IF BLOCK
def loadBooksStudentsToDb(simulate=0):
    file_name = filedialog.askopenfilename(title='Лист выдачи',
        filetypes=(("CSV files", "*.csv"), ("TXT files", "*.txt"), ("All files", "*.*")))
    try:
        with open(file_name) as f:
            l = []
            for el in f.read().split('\n'):
                l.append(el.split(';'))
    except:
        # showwarning('Ошибка', 'Ошибка чтения/обработки файла')
        return False
    l.pop(-1)
    c = 0
    # try:
    conn = sqlite3.connect('library.db')
    for el in l:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO books_students (student_id, book_id, amount, date_took, date_back, comment) VALUES (?, ?, ?, ?, ?, ?)",
            (el[1].strip(), el[2].strip(), el[3].strip(), el[4].strip(), el[5].strip(), el[6].strip()))
        if not(el[5].strip().find('-') == 4) and simulate:
            cur.execute('SELECT avaliavable_amount FROM books WHERE id=?', (el[2].strip(),))
            n = cur.fetchone()[0]
            cur.execute('UPDATE books SET avaliavable_amount=? WHERE id=?', (int(n)-int(el[3].strip()), el[2].strip()))
        c += 1
    conn.commit()
    showwarning('Load books-students', f'Загружено {c} позиц.')

class Info_wnd:
    def __init__(self):
        self.wnd = Tk()
        self.wnd.title('Справка '+prog_name)
        self.wnd.resizable(False,False)
        self.wnd.focus_force()
        frame1 = Frame(self.wnd, background='#bfbfff')
        frame1.pack(fill=BOTH)

        text = Text(master=frame1, padx=20, pady=15, width=120, height=25, cursor="question_arrow")
        text.pack(fill=BOTH, side=LEFT)
        text.insert(0.0, info_text)
        text.configure(state=DISABLED)

        scroll = Scrollbar(master=frame1, command=text.yview)
        scroll.pack(side=LEFT, fill=Y)

        text.config(yscrollcommand=scroll.set)

        self.wnd.mainloop()

class Table_class:
    def __init__(self, master, root, columns=('None', 'None', 'None', 'None', 'None', 'None', 'None', 'None'),
                 colwidth = (50, 50, 50 , 50 , 50 , 50 , 50 , 50 ), fList=['', '', '', '', '', '', '', ''],
                 table_name='books', table_id=0):
        self.master = master
        self.root = root
        self.columns = columns
        self.colwidth = colwidth
        self.fList = fList
        self.table_name = table_name
        self.table_id = table_id
        self.table_rows = 23
        # СОРТИРОВКА ПО СТОЛБЦАМ
        self.rev = {"#%d" % x: False for x in range(1, len(columns) + 1)}
        self.filter_on = True
        self.strict_filter = 0


        s = Style()
        s.theme_use('clam')
        s.configure('Treeview.Heading', background="green3")

        self.root.bind('<Enter>', lambda x: scaling(x))
        self.root.bind('<Control-s>', lambda x: self.saveShownData())


        self.frame_find = Frame(self.master, background='#F0F8FF')
        self.frame_find.pack(fill=X, side=TOP)

        # def f_btn_filter():
        #     self.filter_on = not self.filter_on
        #     self.call_filters()

        btn_filter = placeLabel(self.frame_find, text='Поиск 🔎', pady=5, background='#F0F8FF', font=Font(size=9, weight='bold')) #command=lambda: f_btn_filter(),
        btn_filter.pack(side=LEFT, anchor=NE)
        # btn_filter.configure(font=Font(family="Times New Roman", size=14))
        self.call_filters()


        btn_frame = Frame(self.frame_find, background='#F0F8FF')
        btn_frame.pack(side=RIGHT,anchor=N)

        placeButton(btn_frame, text='Добавить запись', side=TOP, anchor=E, command=lambda:self.addOnePos())
        placeButton(btn_frame, text='Удалить отображенные', pady=0, side=TOP, anchor=E, command=lambda: self.delShownData())
        placeButton(btn_frame, text='Сохранить таблицу', side=TOP, anchor=E, command=lambda: self.saveShownData())

        self.scr_frame = Frame(self.master)
        self.scr_frame.pack(fill=Y, side=RIGHT)

        self.tree_frame = Frame(self.master)
        self.tree_frame.pack(fill=BOTH)

        self.tree = Treeview(self.tree_frame, height=self.table_rows, columns=columns)
        self.tree.pack(fill=BOTH, side=TOP)
        self.tree.column('#0', width=0, stretch=NO)

        #Генератор таблицы (columns, colwidth)
        for i in range(len(self.columns)):
            self.tree.column(f'#{i + 1}', anchor=CENTER, width=int(self.colwidth[i]))
            self.tree.heading(f'#{i+1}', text=self.columns[i])
        #Сортировка по столбцам
        self.tree.bind('<Button-3>', lambda x: self.treeview_sort_column(self.tree.identify_column(mouse_coord(x))))
        #Редактирование элемента
        self.tree.bind('<Double-Button-1>', lambda x: __editLibraryTree__())
        self.tree.bind('<Delete>', lambda x: self.delShownData(delSel=True))

        verscrlbar = Scrollbar(self.scr_frame, orient="vertical", command=self.tree.yview)
        verscrlbar.pack(fill=Y, side=LEFT)
        self.tree.configure(yscrollcommand=verscrlbar.set)

        self.load_db_data()

        self.bottom_frame = Frame(self.master, background='#F0F8FF')
        self.bottom_frame.pack(fill=X, side=BOTTOM)

        self.lbl1 = Label(self.bottom_frame, text=f'Строк в таблице: {len(self.tree.get_children())}', background='#F0F8FF')
        self.lbl1.pack()
        # self.lbl1.bind('<1>', lambda x: lbl1.configure(text=len(self.tree.get_children())))

        def scaling(event):
            n = int(self.root.geometry().split('+')[0].split('x')[1])
            self.tree.configure(height=int(self.table_rows*(n/642)))

        def mouse_coord(event):
            x = event.x
            return x

        def __editLibraryTree__():
            def get_cur_entries():
                for i in range(len(l)):
                    l[i] = entries[i].get().strip()
                # lbl_1.configure(text=l)
                l[0] = id
                return l
            # try:
            l = self.tree.item(self.tree.selection())['values']

            editWnd = Tk()
            # editWnd.geometry(f"{int(wx // 2)}x{int(wy // 5)}+{int(wx // 4)}+{int(wy // 3)}")
            editWnd.title(f'Редактировать запись «ID {l[0]}»')
            editWnd.resizable(False,False)
            editWnd.focus_force()
            id = l[0]
            frame1 = Frame(editWnd)  # , background='green')
            frame1.pack(padx=10, pady=10)
            headers = []
            entries = []
            for el in self.rev:
                headers.append(self.tree.heading(el)['text'])
            c = 0
            for i in range(len(headers)):
                Label(frame1, text=headers[i], padx=5).grid(row=1, column=c)
                entries.append(Entry(frame1, width=self.colwidth[i]//10))
                entries[i].grid(row=2, column=c)
                entries[i].insert(index=0, string=str(l[i]))
                c += 1
            for i in range(len(headers)):
                entries[i].bind('<Key>', lambda x: get_cur_entries())
            entries[0].configure(state=DISABLED)
            c = int(c // 2) - 1
            if self.table_id == 1:
                # placeLabel(frame1, text='---> В данной таблице некоторые поля недоступны для редактирования <---', is_pack=False).grid(row=0, column=0, columnspan=2)
                for i in range(len(headers)):
                    entries[i].configure(state=DISABLED)
                entries[7].configure(state=NORMAL)
                if l[6] == '-':
                    placeButton(frame1, text='Вернуть книги', is_pack=False, command=lambda: returnBook(get_cur_entries())).grid(row=3, column=c-1)
            placeButton(frame1, text='Сохранить', is_pack=False, command=lambda:saveChanges(get_cur_entries())).grid(row=3, column=c)
            placeButton(frame1, text='Отмена', is_pack=False, command=lambda:editWnd.destroy()).grid(row=3, column=c+1)

            def returnBook(l):
                l[6] = get_current_date()
                conn = sqlite3.connect('library.db')
                cur = conn.cursor()
                cur.execute('UPDATE books_students SET date_back=?, comment=? WHERE id=?', (l[6], l[7], l[0]))
                cur.execute("SELECT book_id FROM books_students WHERE id = ?", (l[0], ))
                book_id = cur.fetchone()[0]
                cur.execute('SELECT avaliavable_amount FROM books WHERE id=?', (book_id,))
                n = cur.fetchone()[0]
                cur.execute('UPDATE books SET avaliavable_amount=? WHERE id=?', (int(n) + int(l[4].strip()), book_id))
                conn.commit()
                editWnd.destroy()
                self.__refreshTree__()

            def saveChanges(l):
                conn = sqlite3.connect('library.db')
                cur = conn.cursor()
                cur.execute(f"SELECT * FROM pragma_table_info('{self.table_name}') AS tblInfo")
                var = cur.fetchall()
                heads = []
                if self.table_id != 1:
                    for i in range(len(var)):
                        heads.append(var[i][1])
                    s = f'UPDATE {table_name} SET'
                    for i in range(1, len(heads)):
                        s += ', ' + str(heads[i]) + '=?'
                    s = s.replace(',', '', 1)
                    s += f' WHERE {heads[0]}=?'
                    l.append(l[0]); l.pop(0)
                    # print(s,l)
                    cur.execute(s, l)
                else:
                    for i in range(len(var)):
                        heads.append(var[i][1])
                    s = f'UPDATE {table_name} SET'
                    n = 3
                    for i in range(len(heads[n:])):
                        s += ', ' + str(heads[i+n]) + '=?'
                    s = s.replace(',', '', 1)
                    s += f' WHERE {heads[0]}=?'
                    l.append(l[0]); l.pop(0); l.pop(0)
                    l = l[n - 1:]
                    # print(s,l)
                    cur.execute(s, l)
                conn.commit()
                self.__refreshTree__()
                editWnd.destroy()

    def treeview_sort_column(self, col='#1', reverse=False):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: int(t[0]), reverse=self.rev[col])
        except:
            l.sort(reverse=self.rev[col])
        for k in self.rev.keys():
            self.tree.heading(k, text=self.tree.heading(k, "text").replace("v", "").replace("^", ""))
        self.tree.heading(col, text=["^", "v"][self.rev[col]] + self.tree.heading(col, "text"))
        self.rev[col] = not self.rev[col]
        # if reverse: self.rev[col] = not self.rev[col]
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

    def load_db_data(self):
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM {self.table_name}')
        var = cur.fetchall()
        var = list(map(list, var))
        if self.table_id == 1:
            for i in range(len(var)):
                try:
                    cur.execute(f'SELECT fio, class FROM students WHERE id=?', (var[i][1],))
                    x = cur.fetchone()
                    var[i][1] = x[0]
                    var[i].insert(2, x[1])
                    cur.execute(f'SELECT author, name, year FROM books WHERE id=?', (var[i][3],))
                    var[i][3] = '; '.join(list(map(str, cur.fetchone())))
                    # var[i][3][0] = var[i][3][0][0:10]
                except Exception as err:
                    print('STUDENT ID' , var[i][1], 'OR BOOK ID', var[i][3], 'NOT FOUND', err)
        addList = []
        check_frs = ''
        for f in self.fList:
            check_frs += f
        if check_frs != '':
            for el in var:
                if compare_two_tuples(self.fList, el, self.strict_filter):
                    addList.append(el)
        else:
            addList = var
        # for row in addList:
        list(map(lambda row: self.tree.insert(parent='', index='end', values=(row)), addList))
            # self.tree.insert(parent='', index='end', values=(row))
        try:
            self.lbl1.configure(text=f'Строк в таблице: {len(self.tree.get_children())}')
        except: pass
        conn.commit()

    def call_filters(self):
        if not self.filter_on:
            try:
                self.frame_find_grid.forget()
                return
            except Exception as err:
                print(Exception, err)
                return
        self.frame_find_grid = Frame(self.frame_find, background='#F0F8FF', highlightbackground="black", highlightthickness=1)
        self.frame_find_grid.pack(side=LEFT, fill=X)
        l = []
        c = 0
        for i in range(len(self.columns)):
            Label(self.frame_find_grid, text=self.columns[i], background='#F0F8FF').grid(row=0, column=i, pady=5, padx=5)
            l.append(Entry(self.frame_find_grid, width=self.colwidth[i]//10))
            l[i].grid(row=1, column=i, pady=5, padx=5)
            l[i].insert(0, self.fList[i])
            c += 1

        def clear_filters(l):
            for el in l:
                el.delete(0, 'end')
            use_filters(l)

        def use_filters(l, f = 0):
            if f:
                self.strict_filter = not self.strict_filter
            for i in range(len(l)):
                self.fList[i] = l[i].get()
            self.__refreshTree__()
        chk_box = Checkbutton(self.frame_find_grid, text='Искать с первого символа', variable=self.strict_filter,
                              onvalue=1, offvalue=0, command=lambda: use_filters(l, 1), background='#F0F8FF')
        chk_box.grid(row=3, column=2, columnspan=3)
        self.root.bind('<Key>', lambda x:use_filters(l))
        btn_clear = placeButton(self.frame_find_grid, is_pack=False, text='Очистить поля', command=lambda: clear_filters(l))
        btn_clear.grid(row=3, column=1)
        # wnd.mainloop()

    def saveShownData(self):
        s = ''
        for t in self.__getTable__():
            for el in t:
                s += str(el) + ';'
            s += '\n'
        s = s.replace(';\n', '\n')
        file_name = self.table_name + str(dt.datetime.now().strftime(" %d.%m.%y"))
        file_name = filedialog.asksaveasfilename(filetypes=(("CSV files", "*.csv"), ("All files", "*.*")), initialfile=file_name, defaultextension='.csv')
        if file_name == '': return False
        if file_name.find('.csv') == -1:
            file_name += '.csv'
        with open(file_name, 'w') as f:
            f.write(s)

    def delShownData(self, delSel=False):
        s = ''
        lst1 = []
        if delSel:
            curTableList = (self.tree.item(self.tree.selection())["values"], )
        else:
            curTableList = self.__getTable__()
        c = len(curTableList)
        import os
        directory = 'Удалённые записи'
        if not os.path.exists(directory):
            os.makedirs(directory)
        if askokcancel('Удаление записей', f'ВНИМАНИЕ!\nУдалить {c} записей из таблицы?'):
            if self.table_id == 1:
                conn = sqlite3.connect('library.db')
                cur = conn.cursor()
                for el in curTableList:
                    cur.execute(f"DELETE FROM {self.table_name} WHERE id=?", (el[0],))
            else:
                conn = sqlite3.connect('library.db')
                cur = conn.cursor()
                for el in curTableList:
                    try:
                        cur.execute(f'SELECT id FROM books_students WHERE {self.table_name[0:-1]}_id=?', (el[0],))
                        m = cur.fetchall()
                        if m != []:
                            m = list(map(lambda x: x[0],m))
                            for elem in m:
                                cur.execute(f"SELECT * FROM books_students WHERE id=?", (elem, ))
                                x = list(cur.fetchall()[0])
                                try:
                                    cur.execute(f"SELECT fio, class FROM students WHERE id=?", (x[1],))
                                    x[1] = ' '.join(cur.fetchall()[0])
                                except: showwarning('Ошибка', f'(ID выдачи {elem}) Ученик с id {x[1]} не существует')
                                try:
                                    cur.execute(f"SELECT author, name FROM books WHERE id=?", (x[2],))
                                    x[2] = ' '.join(cur.fetchall()[0])
                                except: showwarning('Ошибка', f'(ID выдачи {elem}) Книги с id {x[2]} не существует')
                                s += ';'.join(map(str, x)).replace(';-;', ';НЕ СДАНО;', 1) + '\n'
                            lst1 += map(lambda x: x, m)
                    except Exception as err: showwarning('Ошибка', 'error while checking books_students table' + str(err)); return
                if s != '':
                    if askokcancel('Внимание', f'Найдены связанные записи:\n\n{s[0:650]}...\n\nПродолжить удаление?'):
                        for el in curTableList:
                            cur.execute(f"DELETE FROM {self.table_name} WHERE id=?", (el[0],))
                        for el in lst1:
                            cur.execute(f"DELETE FROM books_students WHERE id=?", (el,))
                        c += len(lst1)
                        with open(f'{directory}/Удалены {self.table_name} {get_current_date(s="%Y-%m-%d %H.%M.%S")} (связ.).csv', 'w', encoding='windows-1251') as file:
                            file.write(s)
                    else: return
                else:
                    for el in curTableList:
                        cur.execute(f"DELETE FROM {self.table_name} WHERE id=?", (el[0],))
            with open(f'{directory}/Удалены {self.table_name} {get_current_date(s="%Y-%m-%d %H.%M.%S")}.csv', 'w', encoding='windows-1251') as file:
                str1 = ''
                for el in curTableList:
                    str1 += ';'.join(map(str, el)) + '\n'
                file.write(str1)
            showwarning('Удаление записей', f'ВНИМАНИЕ!\nУдалено {c} записей из таблицы')
            conn.commit()
            self.__refreshTree__()

    def addOnePos(self):
        wnd = Tk()
        wnd.title('Добавить запись')
        wnd.resizable(False, False)
        wnd.focus_force()
        l = []
        c = 0
        if self.table_id == 1:
            columns = ('Ученик/филиал', 'Автор', 'Название', 'Год', 'Кол-во', 'Выдано', 'Комментарий')
            autocomplList = []
            conn = sqlite3.connect('library.db')
            cur = conn.cursor()
            cur.execute(f"SELECT fio, class FROM students")
            autocomplList.append(sorted(list(set(map(lambda x: x[0] + ', ' + x[1], cur.fetchall())))))
            cur.execute(f"SELECT author FROM books")
            autocomplList.append(sorted(list(set(map(lambda x: x[0], cur.fetchall())))))
            conn.commit()
            for i in range(len(columns)):
                Label(wnd, text=columns[i]).grid(row=0, column=i, pady=5, padx=5)
                if i <= 3:
                    l.append(AutocompleteEntryListbox(wnd, ))
                    l[i].grid(row=1, column=i, pady=5, padx=5)
                else:
                    l.append(Entry(wnd, ))
                    l[i].grid(row=1, column=i, pady=10, padx=5, sticky=N)
                c += 1
            l[-1].insert('0', '-')
            l[-2].insert('0', get_current_date())
            l[-2].configure(state=DISABLED, width=10)
            l[0].configure(completevalues=autocomplList[0], width=25)
            l[1].configure(completevalues=autocomplList[1], width=25)
            l[2].configure(width=25)
            l[3].configure(width=8)
            l[4].configure(width=8)
            l[2].bind('<Enter>', lambda x: tryName(x))
            l[2].bind('<FocusIn>', lambda x: tryName(x))
            autocomplList.append([])
            def tryName(event):
                try:
                    cur.execute(f"SELECT name FROM books WHERE author = ?", (l[1].get(), ))
                    autocomplList[2] = sorted(list(set(map(lambda x: x[0], cur.fetchall()))))
                except: pass
                l[2].configure(completevalues=autocomplList[2])
            l[3].bind('<Enter>', lambda x: tryYear(x))
            l[3].bind('<FocusIn>', lambda x: tryYear(x))
            autocomplList.append([])
            def tryYear(event):
                try:
                    cur.execute(f"SELECT year FROM books WHERE name = ?", (l[2].get(),))
                    autocomplList[3] = list(set(map(lambda x: str(x[0]), cur.fetchall())))
                except:
                    pass
                l[3].configure(completevalues=autocomplList[3])

        else:
            for i in range(1, len(self.columns)):
                Label(wnd, text=self.columns[i]).grid(row=0, column=i-1, pady=5, padx=5)
                l.append(Entry(wnd, width=self.colwidth[i] // 10))
                l[i-1].grid(row=1, column=i-1, pady=5, padx=5)
                c += 1


        def saveOnePos():
            conn = sqlite3.connect('library.db')
            cur = conn.cursor()
            if self.table_id == 1:
                lst = list(map(lambda x: x.get(), l))
                lst.insert(1, lst[0].split(', ')[1])
                lst[0] = lst[0][0:lst[0].find(',')]
                for el in lst:
                    if el == '':
                        showwarning('Ошибка', 'Поля ввода не должны быть пустыми')
                        wnd.focus_force()
                        return
                try:
                    cur.execute("SELECT id FROM students WHERE fio = ? AND class = ?", (lst[0], lst[1]))
                    student_id = cur.fetchone()[0]
                except:
                    showwarning('Ошибка', f'{lst[0], lst[1]} не существует')
                    wnd.focus_force()
                    return
                try:
                    cur.execute("SELECT id FROM books WHERE author = ? AND name = ? AND year = ?", (lst[2], lst[3],  lst[4]))
                    book_id = cur.fetchone()[0]
                except:
                    showwarning('Ошибка', f'{lst[2], lst[3], lst[4]} не существует')
                    wnd.focus_force()
                    return
                try:
                    cur.execute('SELECT avaliavable_amount FROM books WHERE id=?', (book_id,))
                    n = cur.fetchone()[0]
                    if (int(n) - int(lst[5].strip())) < 0:
                        if askokcancel('Внимание',
                                       f'После операции останется доступно {(int(n) - int(lst[5].strip()))} книг. Продолжить?'):
                            pass
                        else: showwarning('Сообщение', 'Выдача отменена'); wnd.focus_force(); return
                    cur.execute(
                        f"INSERT INTO books_students (student_id, book_id, amount, date_took, date_back, comment) VALUES (?, ?, ?, ?, ?, ?)",
                        (student_id, book_id, lst[5], lst[6], '-', lst[7]))
                    cur.execute('UPDATE books SET avaliavable_amount=? WHERE id=?',
                                (int(n) - int(lst[5].strip()), book_id))
                except:
                    showwarning('Ошибка', 'Ошибка записи в Базу Данных.')
                    wnd.focus_force()
                    return

            else:
                lst = list(map(lambda x: x.get(), l))
                for el in lst:
                    if el == '':
                        showwarning('Ошибка', 'Поля ввода не должны быть пустыми')
                        wnd.focus_force()
                        return
                cur.execute(f"SELECT * FROM pragma_table_info('{self.table_name}') AS tblInfo")
                var = cur.fetchall()
                heads = []
                for i in range(len(var)):
                    heads.append(var[i][1])
                s = f'INSERT INTO {self.table_name} ('
                for i in range(1, len(heads)):
                    s += ', ' + str(heads[i])
                s = s.replace(',', '', 1)
                s += f') VALUES ('
                for i in range(1, len(heads)):
                    s += ', ?'
                s = s.replace(', ?', '?', 1)
                s += ')'
                cur.execute(s,lst)
            conn.commit()
            self.__refreshTree__()
            self.treeview_sort_column()
            self.treeview_sort_column()
            wnd.destroy()


        btn_save = placeButton(wnd, is_pack=False, text='Добавить', command=lambda: saveOnePos())
        btn_save.grid(row=2, column=(c-1)//2)

        btn_cancel = placeButton(wnd, is_pack=False, text='Отмена', command=lambda:wnd.destroy())
        btn_cancel.grid(row=2, column=(c-1)//2+1)

        wnd.mainloop()

    def __refreshTree__(self):
        # x = self.tree.get_children()
        list(map(lambda item: self.tree.delete(item), self.tree.get_children()))
        # for item in x:
        #     self.tree.delete(item)
        self.load_db_data()

    def __getTable__(self):
        l = list(map(lambda x: self.tree.item(x)['values'], self.tree.get_children()))
        return l

    def __destroy__(self):
        self.tree_frame.destroy()



class Main_class:
    def __init__(self):
        self.root = Tk()
        self.root.title(prog_name)
        wx = self.root.winfo_screenwidth()
        wy = self.root.winfo_screenheight()
        self.root.geometry(f"{int(wx // 2)}x{int(wy // 2)}+{int(wx * (wx / 10000))}+{int(wy * (wy / 10000))}")
        self.root.minsize(int(wx // 1.5), int(wy // 1.4))

        menubar = Menu(self.root)
        self.root.configure(menu=menubar, background='white')
        fileMenu = Menu(menubar)
        # saveCurrentTable()
        menubar.add_cascade(label="Импорт данных", menu=fileMenu)
        fileMenu.add_command(label="Импорт книг", command=lambda:loadBooksToDb())
        fileMenu.add_command(label="Импорт учеников", command=lambda:loadStudentsToDb())
        fileMenu.add_command(label="Импорт листа выдачи", command=lambda: loadBooksStudentsToDb())
        menubar.add_command(label="Сохранить таблицу", command=lambda: self.wnd.saveShownData())
        # menubar.add_command(label="QR-код", command=lambda: Window_qr_code())
        menubar.add_command(label="Справка", command=lambda: Info_wnd())

        # fileMenu.delete()


        self.frame1 = Frame(self.root, background='#F0F8FF')
        self.frame1.pack(fill=X)
        btn1 = placeButton(self.frame1, text='Таблица выдачи и получения книг',
                           command=lambda: [self.root.title(prog_name + ' «Таблица выдачи и получения книг»'), self.__show_table__(1)])
        btn1.pack(side=LEFT)
        btn2 = placeButton(self.frame1, text='Книги',
                           command=lambda: [self.root.title(prog_name + ' «Книги»'), self.__show_table__(2)])
        btn2.pack(side=LEFT)
        btn3 = placeButton(self.frame1, text='Ученики/филиалы',
                           command=lambda: [self.root.title(prog_name + ' «Ученики/филиалы»'), self.__show_table__(3)])
        btn3.pack(side=LEFT)

        self.frame3 = Frame(self.root, background='white')
        self.frame3.pack(fill=BOTH, anchor=CENTER)
        try:
            img = ImageTk.PhotoImage(Image.open('hello.png').resize((wx//3, wy//3)))
            lbl1 = Label(self.frame3, text='text', image=img, borderwidth=0)
            lbl1.pack(anchor=CENTER, pady=50)
        except: placeLabel(self.frame3, text='No Image')
        placeLabel(self.frame3, text=hello_lbl, background='white', font=Font(size=14))

        self.root.mainloop()

    def __show_table__(self, table_id=0):
        try:
            self.frame2.destroy()
        except: pass
        try:
            self.frame3.destroy()
        except: pass
        self.frame2 = Frame(self.root, background=None)
        self.frame2.pack(fill=BOTH)
        match table_id:
            case 1:
                # self.lbl = Label(self.frame2, text='Выдача - возврат')
                # self.lbl.pack()
                self.wnd = Table_class(self.frame2, self.root, columns=('ID', 'Ученик/филиал', 'Класс', 'Автор Название', 'Кол-во', 'Выдано', 'Получено', 'Комментарий'),
                                  colwidth=(40, 180, 40, 380, 40, 70, 70, 100),
                                  table_name='books_students', table_id=1)
            case 2:
                # self.lbl = Label(self.frame2, text='Прием - списание')
                # self.lbl.pack()
                self.wnd = Table_class(self.frame2, self.root, columns=('ID', 'Автор', 'Название', 'Год', 'Кол-во', 'Доступно', 'Жанр', 'Комментарий'),
                                  colwidth=(50, 210, 210, 50, 50, 50, 50, 210),
                                  table_name='books', table_id=2)
            case 3:
                # self.lbl = Label(self.frame2, text='Таблица учеников')
                # self.lbl.pack()
                self.wnd = Table_class(self.frame2, self.root, columns=('ID', 'Ученик/филиал', 'Класс'),
                                  colwidth=(50, 250, 250),
                                  table_name='students', table_id=3)
            case _:
                self.lbl = Label(self.frame2, text='ID таблицы не указан')
                self.lbl.pack()

def main():
    init_db()
    wnd = Main_class()

if __name__ == '__main__':
    main()