#hannah.drew@stud.th-deg.de
#franziska.botzler@stud.th-deg.de
#moritz.etemad@stud.th-deg.de
import json
from tkinter import *
import tkinter as tk

library_filename = "lib.json"
library=[]
try:
    fh = open(library_filename, "r")
    library = json.load(fh)
    fh.close()
except Exception as e:
    print("unable to open ", library_filename)
    library = []

def book_list():
    print("lib size: ", len(library))
    newWindow = Toplevel(root)
    newWindow.title("List books")
    newWindow.geometry("200x200")
    T = Text(newWindow, height=10, width=40)
    T.grid()
    if len(library) == 0:
        T.insert(END, "No books available.\n")
    else:
        for item in library:
            book_details = f"Title: {item['title']}\nAuthor: {item['author']}\nYear: {item['year']}\n\n"
            T.insert(END, book_details)

def add():
    Label(root, text='Title').grid(row=4)
    Label(root, text='Author').grid(row=5)
    Label(root, text='Year').grid(row=6)
    e1 = tk.Entry(root)
    e2 = tk.Entry(root)
    e3 = tk.Entry(root)
    e1.grid(row=4, column=1)
    e2.grid(row=5, column=1)
    e3.grid(row=6, column=1)

    def save_new_entry():
        new_entry = {}
        new_entry["title"] = e1.get().strip()
        new_entry["author"] = e2.get().strip()
        new_entry["year"] = e3.get().strip()
        library.append(new_entry)
        lib_filename = open(library_filename, "w")
        json.dump(library, lib_filename, indent=4)
        e1.delete(0, END)
        e2.delete(0, END)
        e3.delete(0, END)

    sub_btn = tk.Button(root, text='Save', command=save_new_entry)
    sub_btn.grid(row=7, column=1)

def delete():
    Label(root, text='Title').grid(row=4, column=2)
    Label(root, text='Author').grid(row=5, column=2)
    e4 = tk.Entry(root)
    e5 = tk.Entry(root)
    e4.grid(row=4, column=3)
    e5.grid(row=5, column=3)

    def delete_book():
        global library
        with open("lib.json", "r") as f:
            data=json.load(f)
        title_to_delete = e4.get().strip().lower()
        author_to_delete = e5.get().strip().lower()

        library = [book for book in data if not (book.get("title", "").strip().lower() == title_to_delete and book.get("author", "").strip().lower() == author_to_delete)]

        with open(library_filename, "w") as file:
            json.dump(library, file, indent=4)
        file.close()

        e4.delete(0, END)
        e5.delete(0, END)

    _btn = tk.Button(root, text='Delete', command=delete_book)
    _btn.grid(row=7, column=3)

root = tk.Tk()
root.title("Lib")
root.geometry("400x300")
button1 = tk.Button(root, text="List books", command=lambda: book_list())
button1.grid(row=0)
button2 = tk.Button(root, text="Add book", command=lambda: add())
button2.grid(row=1)
button3 = tk.Button(root, text="Delete book", command=lambda: delete())
button3.grid(row=3)

root.mainloop()