from tests.test_tube import test_multi_bend, Bend
import tkinter as tk
from tkinter import *
from typing import Optional, List, Tuple, Dict, Union, Set

#https://realpython.com/python-gui-tkinter/
#https://www.tutorialspoint.com/python/python_gui_programming.htm

def place_bend(e):
    r = 5
    #x, y = e.x, e.y
    if e.x % 10 < 5:
        x = (e.x//10)*10
    else:
        x = (e.x//10+1)*10
    if e.y % 10 < 5:
        y = (e.y//10)*10
    else:
        y = (e.y//10+1)*10
    circ = C.create_oval(x - r, y - r, x + r, y + r, fill="green")
    print(x//10-1)
    print(y//10-1)
    bends.append(Bend(x//10-1, y//10-1, 4))

def set_width(e):
    width = w.get()
    print(width)
    x0, y0, x1, y1 = C.coords(rect)
    x1 = 10 + 10 * float(e)
    C.coords(rect, x0, y0, x1, y1)
    """
        for n in range(0, int(e)):
        C.create_line(10+n*10, 10, 10+n*10, 30)
    for m in range(0, (y1-10)//10):
        C.create_line(10, 10+m*10, 10+10*w.get(), 10+m*10)
    """


def set_height(e):
    height = h.get()
    print(height)
    x0, y0, x1, y1 = C.coords(rect)
    y1 = 10 + 10 * float(e)
    C.coords(rect, x0, y0, x1, y1)
    """
        for n in range(0, 8):
        C.create_line(10+n*10, 10, 10+n*10, 30)
    for m in range(0, 2):
        C.create_line(10, 10+m*10, 90, 10+m*10)
    """



def write_slogan():
    print("Tkinter is easy to use!")

def adjust_params():
    if bends and len(bends) > 0:
        bends = bends.sort()
        end_len = h.get()-bends[len(bends)-1].position
    else:
        end_len = h.get()

    export_knitout(w.get()//2, end_len, bends, E1.get())

def export_tube():
    #print(h.get())
    test_multi_bend(w.get()//2, h.get(), [], E1.get(), 3)
    print("No bends")
    #print(E1.get())

def export_knitout(w: int, end_len: int, b: List[Bend], fn):
    test_multi_bend(w, end_len, b, fn, 3)
    print("Snek")
    print(fn)

if __name__ == "__main__":
    #width = 10
    #height = 2
    bends: [Bend] = []
    filename = "snek"

    window = tk.Tk()
    top = tk.Frame(master=window)
    top.pack()

    instructions = StringVar()
    label = Label(top, textvariable=instructions, justify=LEFT)
    instructions.set("Welcome to Snake Designer!\nPick your height and width.\nClick on the tube to place bends.\nPretend that the left and right edges of the rectangle are connected to form a tube.\nClick KNIT to generate the Knitout file for your snake!\n")
    label.pack()

    #text = Text(top, wrap=WORD, height=8)
    #text.insert(INSERT, "Welcome to Snake Designer! \n")
    #text.insert(END, "Pick your height and width. \n")
    #text.insert(END, "Click on the tube to place bends. \n")
    #text.insert(END, "Pretend that the left and right edges of the rectangle are connected to form a tube. \n")
    #text.insert(END, "Click KNIT to generate the Knitout file for your snake!\n")
    #text.pack()

    tube = tk.Frame(master=window)
    tube.pack()

    w = IntVar()
    scale = Scale(tube, variable=w, from_=8, to=40, length=400, resolution=2, orient=HORIZONTAL, label="circumference", command=set_width)
    scale.pack(side=TOP)

    h = IntVar()
    scale = Scale(tube, variable=h, from_=2, to=40, length=400, resolution=1, orient=VERTICAL, label="num of rows", command=set_height)
    scale.pack(side=LEFT)

    C = tk.Canvas(tube, bg="blue", height=500, width=500)
    coord = 10, 50, 240, 210
    arc = C.create_arc(coord, start=0, extent=150, fill="red")
    rect = C.create_rectangle(10, 10, 90, 30, fill="yellow")
    for n in range(0, 40):
        C.create_line(10+n*10, 10, 10+n*10, 410)
    for m in range(0, 40):
        C.create_line(10, 10+m*10, 410, 10+m*10)

    C.pack()

    C.bind('<Button-1>', place_bend)

    #tube.pack(fill=tk.Y, side=tk.LEFT)

    btm = tk.Frame(master=window)
    btm.pack()

    L1 = Label(btm, text="File Name")
    L1.pack(side=LEFT)
    E1 = Entry(btm, bd=5, textvariable=filename)
    E1.pack(side=LEFT)

    if len(bends) > 0:
        btn = Button(btm, text="KNIT", command=adjust_params)
    else:
        btn = Button(btm, text="KNIT", command=export_tube)

    btn.pack(side=RIGHT)

    window.mainloop()

    #test_multi_bend(10, 5, [Bend(6, 5, 0), Bend(11, 5, 6), Bend(16, 5, 0), Bend(21, 5, 6)], "largecentered4bends", 3)
    #test_multi_bend(10, 5, [Bend(11, 5, 0), Bend(16, 5, 6), Bend(26, 5, 4), Bend(31, 5, 9)], "largeshifted4bends", 3)


