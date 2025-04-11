import json, random, string
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Canvas
from PIL import Image, ImageTk
import pyocr
import pyocr.builders

class LibraryManager:
    def __init__(self):
        self.library = []
        self.current_filename = "default_library.json"
        self.load_library()

    def load_library(self):
        try:
            with open(self.current_filename, "r+") as file:
                self.library = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.library = []
            self.save_library()

    def save_library(self):
        with open(self.current_filename, "w") as file:
            json.dump(self.library, file, indent=4)

    def open_library(self, file_path):
        try:
            with open(file_path, "r+") as f:
                self.library = json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def create_library(self, file_path):
        self.library = []
        self.current_filename = file_path
        self.save_library()

    def add_book(self, title, author, year):
        new_book = {"title": title, "author": author, "year": year, "status": "available"}
        self.library.append(new_book)
        self.save_library()

    def change_book_status(self, title, author, status):
        for book in self.library:
            if book["title"].lower() == title.lower() and book["author"].lower() == author.lower():
                book["status"] = status
                self.save_library()
                break

    def search_books(self, title, author, year):
        return [book for book in self.library
                if (title.lower() in book["title"].lower() if title else True) and
                   (author.lower() in book["author"].lower() if author else True) and
                   (year in str(book["year"]) if year else True)]

    def update_treeview(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        for book in self.library:
            tree.insert('', 'end', values=(book["title"], book["author"], book["year"], book["status"]))

    def on_button_press(self, event, canvas):
        if self.rect_id:
            canvas.delete(self.rect_id)
        start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red",
                                                 width=2)
        self.rect_id = self.rect

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        self.label.config(text=f"Dimensions: {width} x {height}")

    def on_button_release(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        self.label.config(text=f"Dimensions: {width} x {height}")
        self.recognize_text_in_rectangle(self.start_x, self.start_y, event.x, event.y)

    def recognize_text_in_rectangle(self, x1, y1, x2, y2):
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            raise Exception("No OCR tool found")
        self.tool = tools[0]
        cropped_image = self.image.crop((x1, y1, x2, y2))
        recognized_text = self.tool.image_to_string(cropped_image, lang='eng', builder=pyocr.builders.TextBuilder())
        self.text_label.config(text=f"Recognized Text: {recognized_text.strip()}")

class LibraryApp:
    def __init__(self, root, library_manager):
        self.root = root
        self.library_manager = library_manager

        self.root.geometry("900x500")
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)
        self.create_menu()
        self.create_widgets()
        self.library_manager.update_treeview(self.tree)
        self.image_drawer()

    def create_menu(self):
        filemenu = Menu(self.menu)
        self.menu.add_cascade(label='Menu', menu=filemenu)
        filemenu.add_command(label='New', command=self.create_library)
        filemenu.add_command(label='Open', command=self.open_library)
        filemenu.add_command(label='Create 1 Mio', command=self.create_book_entries)

    def create_widgets(self):
        self.T1 = Text(self.root, height=1, width=40)
        self.T1.grid(row=0, column=0, columnspan=3)

        Label(self.root, text='Title').grid(row=2, column=0)
        Label(self.root, text='Author').grid(row=3, column=0)
        Label(self.root, text='Year').grid(row=4, column=0)
        self.e1 = tk.Entry(self.root)
        self.e2 = tk.Entry(self.root)
        self.e3 = tk.Entry(self.root)
        self.e1.grid(row=2, column=1)
        self.e2.grid(row=3, column=1)
        self.e3.grid(row=4, column=1)

        search_btn = Button(self.root, text="Search", command=self.start_search)
        search_btn.grid(row=5, column=1)

        self.v = IntVar()
        Radiobutton(self.root, text='with status', variable=self.v, value=1, command=lambda: self.not_show_column(True)).grid(row=2, column=2)
        Radiobutton(self.root, text='no status', variable=self.v, value=2, command=lambda: self.not_show_column(False)).grid(row=3, column=2)

        self.columns = ("book_title", "book_author", "year", "status")
        self.tree = ttk.Treeview(self.root, columns=self.columns, show='headings')
        self.tree.heading("book_title", text="Title", anchor="center")
        self.tree.heading("book_author", text="Author", anchor="center")
        self.tree.heading("year", text="Year", anchor="center")
        self.tree.heading("status", text="Status", anchor="center")
        self.tree.grid(row=6, column=0, rowspan=10, columnspan=4)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=6, column=4, rowspan=10, sticky="ns")

        add_button = Button(self.root, text="Add Book", command=self.add_book)
        add_button.grid(row=30, column=1)

        delete_btn = Button(self.root, text="Delete book", command=self.change_status_to_delete)
        delete_btn.grid(row=31, column=1)

        upload_btn = Button(self.root, text = "Upload image", command = self.image_drawer)
        upload_btn.grid(row=32, column=1)

        self.tree.bind("<Double-1>", self.item_double_click)

    def image_drawer(self):
        self.image_path = image_path
        new_window = tk.Toplevel(self.root)
        new_window.title("Upload picture")
        new_window.geometry("5500x550")
        self.canvas = Canvas(new_window, width=500, height=500)
        self.canvas.grid()
        self.image = Image.open(image_path)
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.rect_id = None
        self.label = Label(root, text="Dimensions: Width x Height", font=("Helvetica", 12))
        self.label.grid()
        self.text_label = Label(root, text="Recognized Text: ", font=("Helvetica", 12))
        self.text_label.grid()

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red",
                                                 width=2)
        self.rect_id = self.rect

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        self.label.config(text=f"Dimensions: {width} x {height}")

    def on_button_release(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        self.label.config(text=f"Dimensions: {width} x {height}")
        self.recognize_text_in_rectangle(self.start_x, self.start_y, event.x, event.y)

    def recognize_text_in_rectangle(self):
        self.library_manager.recognize_text_in_rectangle()
        self.text_label.config(text=f"Recognized Text: {recognized_text.strip()}")

    def open_library(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if file_path:
            if self.library_manager.open_library(file_path):
                self.library_manager.update_treeview(self.tree)
                self.T1.delete(1.0, END)
                self.T1.insert(END, f"Amount of books: {len(self.library_manager.library)}")
            else:
                messagebox.showinfo("Error", "Unable to load library.")

    def create_library(self):
        new_file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if new_file_path:
            self.library_manager.create_library(new_file_path)
            self.library_manager.update_treeview(self.tree)
            self.T1.delete(1.0, END)
            self.T1.insert(END, f"Amount of books: {len(self.library_manager.library)}")
            messagebox.showinfo("Notice", "New library was created.")
        else:
            messagebox.showinfo("Error", "No new library was created.")

    def create_book_entries(self):
        stop_adding = False
        new_window = tk.Toplevel(self.root)
        new_window.title("Book entries")
        new_window.geometry("280x220")
        lb = tk.Listbox(new_window, height=10, width=40)
        lb.grid(row=0, column=0)
        scrollbar2 = ttk.Scrollbar(new_window, orient="vertical", command=lb.yview)
        lb.configure(yscrollcommand=scrollbar2.set)
        scrollbar2.grid(row=0, column=1, sticky="ns")
        def start_thread():
            while not stop_adding:
                for _ in range(1000000):
                    if stop_adding:
                        break
                    lb.insert(END, (random.choices(string.ascii_lowercase, k=5)))
                    new_window.update()
        def cancel_thread():
            nonlocal stop_adding
            stop_adding = True
        btn = Button(new_window, text="Create 1 Million book entries", command=start_thread)
        btn.grid()
        btn2 = Button(new_window, text="Cancel", command=cancel_thread)
        btn2.grid()

    def start_search(self):
        title_to_find = self.e1.get().strip()
        author_to_find = self.e2.get().strip()
        year_to_find = self.e3.get().strip()
        filtered_books = self.library_manager.search_books(title_to_find, author_to_find, year_to_find)
        if filtered_books:
            self.library_manager.update_treeview(self.tree)
        else:
            messagebox.showinfo("Error", "Book was not found. Please check for spelling.")

    def not_show_column(self, show):
        exclusionlist = ["status"]
        displaycolumns = [col for col in self.tree["columns"] if show or col not in exclusionlist]
        self.tree["displaycolumns"] = displaycolumns

    def add_book(self):
        new_window = Toplevel(self.root)
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

        def add_new_book():
            title = f1.get().strip()
            author = f2.get().strip()
            year = f3.get().strip()
            if title and author and year:
                self.library_manager.add_book(title, author, year)
                self.library_manager.update_treeview(self.tree)
                new_window.destroy()

        save_btn = Button(new_window, text="Save", command=add_new_book)
        save_btn.grid(column=1)

    def change_status_to_delete(self):
        new_window = Toplevel(self.root)
        new_window.title("Delete book")
        new_window.geometry("200x200")
        Label(new_window, text='Title').grid(row=1, column=0)
        Label(new_window, text='Author').grid(row=2, column=0)
        f1 = tk.Entry(new_window)
        f2 = tk.Entry(new_window)
        f1.grid(row=1, column=1)
        f2.grid(row=2, column=1)

        def actual_change():
            title = f1.get().strip()
            author = f2.get().strip()
            self.library_manager.change_book_status(title, author, "deleted")
            self.library_manager.update_treeview(self.tree)
            new_window.destroy()

        delete_button = Button(new_window, text="Delete", command=actual_change)
        delete_button.grid(column=1)

    def item_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_data = self.tree.item(selected_item)
            current_status = item_data["values"][3]
            new_window2 = Toplevel(self.root)
            new_window2.geometry("200x200")
            new_window2.title("Book status")
            combo_box = ttk.Combobox(new_window2, values=["available", "lent out", "missing"])
            combo_box.grid()
            combo_box.set(current_status)
            def choose_status():
                selected_status = combo_box.get()
                self.library_manager.change_book_status(item_data["values"][0], item_data["values"][1], selected_status)
                self.library_manager.update_treeview(self.tree)
                new_window2.destroy()
            save_btn = Button(new_window2, text="Save", command=choose_status)
            save_btn.grid()


if __name__ == "__main__":
    root = tk.Tk()
    library_manager = LibraryManager()
    app = LibraryApp(root, library_manager)
    image_path = "image1.png"
    root.mainloop()
