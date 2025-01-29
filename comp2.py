import difflib
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

def load_file(file_area):
    filename = filedialog.askopenfilename()
    if filename:
        with open(filename, 'r') as file:
            content = file.read()
        file_area.delete(1.0, END)
        file_area.insert(1.0, content)

def save_file(file_area):
    filename = filedialog.asksaveasfilename()
    if filename:
        with open(filename, 'w') as file:
            content = file_area.get(1.0, END)
            file.write(content)

def compare_files():
    content1 = text_area1.get(1.0, END).splitlines()
    content2 = text_area2.get(1.0, END).splitlines()
    diff = list(difflib.ndiff(content1, content2))

    text_area1.tag_config('match', background='green')
    text_area1.tag_config('diff', background='orange')
    text_area2.tag_config('match', background='green')
    text_area2.tag_config('diff', background='orange')

    text_area1.delete(1.0, END)
    text_area2.delete(1.0, END)

    for line in diff:
        if line.startswith('  '):  # Same text
            text_area1.insert(END, line[2:] + '\n', 'match')
            text_area2.insert(END, line[2:] + '\n', 'match')
        elif line.startswith('- '):  # Text in file1 not in file2
            text_area1.insert(END, line[2:] + '\n', 'diff')
        elif line.startswith('+ '):  # Text in file2 not in file1
            text_area2.insert(END, line[2:] + '\n', 'diff')

# GUI Setup
root = Tk()
root.title("File Comparison Tool")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(N, S, E, W))

text_area1 = Text(frame, width=80, height=20)
text_area2 = Text(frame, width=80, height=20)
load_button1 = Button(frame, text="Load File 1", command=lambda: load_file(text_area1))
load_button2 = Button(frame, text="Load File 2", command=lambda: load_file(text_area2))
save_button1 = Button(frame, text="Save File 1", command=lambda: save_file(text_area1))
save_button2 = Button(frame, text="Save File 2", command=lambda: save_file(text_area2))
compare_button = Button(frame, text="Compare", command=compare_files)

text_area1.grid(row=0, column=0, padx=5, pady=5)
text_area2.grid(row=0, column=1, padx=5, pady=5)
load_button1.grid(row=1, column=0, padx=5, pady=5)
load_button2.grid(row=1, column=1, padx=5, pady=5)
save_button1.grid(row=2, column=0, padx=5, pady=5)
save_button2.grid(row=2, column=1, padx=5, pady=5)
compare_button.grid(row=3, column=0, columnspan=2, pady=5)

root.mainloop()
