#alwina.ring@stud.th-deg.de
#hannah.drew@stud.th-deg.de
import json, random, string, threading
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

root = tk.Tk()
root.geometry("900x500")
menu = Menu(root)
root.config(menu=menu)
filemenu = Menu(menu)
menu.add_cascade(label='Menu', menu=filemenu)
filemenu.add_command(label='New', command=lambda: create_library())
filemenu.add_command(label='Open', command=lambda: open_library())
filemenu.add_command(label='Create 1 Mio', command=lambda: create_book_entries())

T1 = Text(root, height=1, width=40)
T1.grid(row=0, column=0, columnspan=3)

Label(root, text='Title').grid(row=2, column=0)
Label(root, text='Author').grid(row=3, column=0)
Label(root, text='Year').grid(row=4, column=0)
e1 = tk.Entry(root)
e2 = tk.Entry(root)
e3 = tk.Entry(root)
e1.grid(row=2, column=1)
e2.grid(row=3, column=1)
e3.grid(row=4, column=1)
search_btn=Button(root, text="Search", command=lambda:start_search())
search_btn.grid(row=5, column=1)

v = IntVar()
Radiobutton(root, text='with status', variable=v, value=1, command=lambda:not_show_column(show = True)).grid(row=2, column=2)
Radiobutton(root, text='no status', variable=v, value=2, command=lambda:not_show_column(show = False)).grid(row=3, column=2)

columns = ("book_title", "book_author", "year", "status")
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading("book_title", text="Title", anchor="center")
tree.heading("book_author", text="Author", anchor="center")
tree.heading("year", text="Year", anchor="center")
tree.heading("status", text="Status", anchor="center")
tree.grid(row=6, column=0, rowspan=10, columnspan=4)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=6, column=4, rowspan=10,sticky="ns")

library=[]
default_filename="default_library.json"
current_filename=default_filename
try:
    with open(current_filename, "r+") as file:
        library = json.load(file)
    T1.delete(1.0, END)
    T1.insert(END, f"Amount of books: {len(library)}")
except (FileNotFoundError, json.JSONDecodeError):
    library = []
    with open(current_filename, "w") as file:
        json.dump(library, file, indent=4)
    T1.delete(1.0, END)
    T1.insert(END, f"Amount of books: {len(library)}")

def open_library():
    global current_filename, library
    file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
    if file_path:
        current_filename = file_path
        try:
            with open(file_path, "r+") as f1:
                library = json.load(f1)
            T1.delete(1.0, END)
            T1.insert(END, f"Amount of books: {len(library)}")
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showinfo("Error", "Unable to load library.")

def create_library():
    global current_filename, library
    new_file_path = filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
    if new_file_path:
        current_filename = new_file_path
        library = []
        with open(current_filename, "w") as f2:
            json.dump(library, f2, indent=4)
        T1.delete(1.0, END)
        T1.insert(END, f"Amount of books: {len(library)}")
        messagebox.showinfo("Notice", "New library was created.")
    else:
        messagebox.showinfo("Error", "No new library was created.")

stop_adding=False
def create_book_entries():
    global stop_adding
    stop_adding = False
    new_window = tk.Toplevel(root)
    new_window.title("Book entries")
    new_window.geometry("280x220")
    lb = tk.Listbox(new_window, height=10, width=40)
    lb.grid(row=0, column=0)
    scrollbar2 = ttk.Scrollbar(new_window, orient="vertical", command=lb.yview)
    lb.configure(yscrollcommand=scrollbar2.set)
    scrollbar2.grid(row=0, column=1, sticky="ns")
    def start_thread():
        while not stop_adding:
            for i in range(1000000):
                if stop_adding:
                    break
                lb.insert(END,(random.choices(string.ascii_lowercase, k=5)))
                new_window.update()
        threading.Thread(target=start_thread, daemon=True).start()
    def cancel_thread():
        global stop_adding
        stop_adding=True
    btn = Button(new_window, text="Create 1 Million book entries", command=start_thread)
    btn.grid()
    btn2 = Button(new_window, text="Cancel", command=cancel_thread)
    btn2.grid()

def update_treeview(library):
    for row in tree.get_children():
        tree.delete(row)
    for book in library:
        tree.insert('', 'end', values=(book["title"], book["author"], book["year"], book["status"]))

def start_search():
    global library, current_filename
    title_to_find = e1.get().strip().lower()
    author_to_find = e2.get().strip().lower()
    year_to_find = e3.get().strip().lower()
    filtered_books = [item for item in library if (title_to_find in item["title"].lower() if title_to_find else True) and (author_to_find in item["author"].lower() if author_to_find else True) and (year_to_find in str(item["year"]) if year_to_find else True)]
    if filtered_books:
        update_treeview(filtered_books)
    else:
        messagebox.showinfo("Error", "Book was not found. Please check for spelling.")

def not_show_column(show):
    if show == False:
        exclusionlist = ["status"]
        displaycolumns = []
        for col in tree["columns"]:
            if col not in exclusionlist:
                displaycolumns.append(col)
        tree["displaycolumns"] = displaycolumns
    else:
        displaycolumns = []
        for col in tree["columns"]:
            displaycolumns.append(col)
        tree["displaycolumns"] = displaycolumns

def add():
    global library, current_filename
    new_window = Toplevel(root)
    new_window.title("Add book")
    new_window.geometry("200x200")
    Label(new_window, text='Title').grid(row=1, column=0)
    Label(new_window, text='Author').grid(row=2, column=0)
    Label(new_window, text='Year').grid(row=3, column=0)
    f1 = tk.Entry(new_window)
    f2 = tk.Entry(new_window)
    f3 = tk.Entry(new_window)
    f1.grid(row=1, column=1)
    f2.grid(row=2, column=1)
    f3.grid(row=3, column=1)
    def add_book():
        if current_filename:
            title = f1.get().strip()
            author = f2.get().strip()
            year = f3.get().strip()
            if title and author and year:
                new_book = {"title": title, "author": author, "year": year, "status": "available"}
                library.append(new_book)
                with open(current_filename, "w") as f:
                    json.dump(library, f, indent=4)
                T1.delete(1.0, END)
                T1.insert(END, f"Amount of books: {len(library)}")
                update_treeview(library)
                new_window.destroy()
    save_btn=Button(new_window, text="Save", command=add_book)
    save_btn.grid(column=1)
add_button = Button(root, text="Add Book", command=add)
add_button.grid(row=30, column=1)

def change_status_to_delete():
    global library, current_filename
    new_window3 = Toplevel(root)
    new_window3.title("Delete book")
    new_window3.geometry("200x200")
    Label(new_window3, text='Title').grid(row=1, column=0)
    Label(new_window3, text='Author').grid(row=2, column=0)
    f1 = tk.Entry(new_window3)
    f2 = tk.Entry(new_window3)
    f1.grid(row=1, column=1)
    f2.grid(row=2, column=1)
    def actual_change():
        title = f1.get().strip()
        author = f2.get().strip()
        for b in library:
            if b["title"].lower() == title.lower() and b["author"].lower() == author.lower():
                b["status"] = "deleted"
                with open(current_filename, "w") as f4:
                    json.dump(library, f4, indent=4)
        update_treeview(library)
        T1.delete(1.0, END)
        T1.insert(END, f"Amount of books: {len(library)}")
        new_window3.destroy()
    delete_button = Button(new_window3, text="Another delete button", command=actual_change)
    delete_button.grid(column=1)
delete_btn = Button(root, text="Delete book", command= change_status_to_delete)
delete_btn.grid(row=31, column=1)

def item_double_click(event):
    selected_item = tree.selection()
    if selected_item:
        item_data = tree.item(selected_item)
        current_status=item_data["values"][3]
        new_window2 = tk.Toplevel(root)
        new_window2.geometry("200x200")
        new_window2.title("Book status")
        combo_box = ttk.Combobox(new_window2, values=["available","lent out", "missing"])
        combo_box.grid()
        combo_box.set("available")
        combo_box.bind("<<TreeviewSelection>>")
        def choose_status():
            selected_status = combo_box.get()
            for b2 in library:
                if b2["title"] == item_data["values"][0] and b2["author"] == item_data["values"][1]:
                    b2["status"] = selected_status
                    with open(current_filename, "w") as f3:
                        json.dump(library, f3, indent=4)
                    new_window2.destroy()
                    update_treeview(library)
        save_btn = Button(new_window2, text="Save", command=choose_status)
        save_btn.grid()
tree.bind("<Double-1>", item_double_click)

root.mainloop()