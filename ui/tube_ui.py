from tkinter import messagebox

from tests.test_tube import test_multi_bend, Bend
import tkinter as tk
from tkinter import *
from typing import Optional, List, Tuple, Dict, Union, Set

#https://realpython.com/python-gui-tkinter/
#https://www.tutorialspoint.com/python/python_gui_programming.htm
# need to keep map of coordinates to canvas objects so they can be deleted after--nvm, just use find_closest

class Draft_Bend:
    """
    A Simple class structure for representing a draft bend
    """

    def __init__(self, position: int, bendiness: float, bend_dir: int):
        """
        :param position: where along the length of the snake the bend takes place
        :param bendiness: how tall the bend is in a number from 0 to 1
        :param bend_dir: which way the bend goes
        """
        self.position: int = position
        self.bendiness: float = bendiness
        self.bend_dir: int = bend_dir
        assert self.position is not None
        assert self.bendiness is not None
        assert self.bend_dir is not None
        assert bendiness >= 0
        assert bendiness <= 1


    def __str__(self):
        return f"bend {self.position} + {self.bendiness} + {self.bend_dir}"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self.position

    def __lt__(self, other):
        if isinstance(other, Draft_Bend):
            return self.position < other.position
        elif type(other) is int:
            return self.position < other
        else:
            raise AttributeError

    def __eq__(self, other):
        if isinstance(other, Draft_Bend):
            return self.position == other.position and self.bendiness == other.bendiness and self.bend_dir == other.bend_dir
        else:
            raise AttributeError


def open_menu(col: int, row: int, x: int, y: int, is_new: bool, circ, ring):
    menu = Toplevel(window)
    menu.grab_set() # stop any interaction until the menu box is closed
    menu.title("Edit bend")
    menu.geometry("200x200")
    Label(menu, text="Edit bend at column "+str(col)+" and row "+str(row)).pack()

    def close():
        #delete ring
        C.delete(ring)
        menu.destroy()

    def cancel():
        if is_new is True:
            C.delete(circ)
        close()

    cancel_button = Button(menu, text="Cancel", command=cancel)
    cancel_button.pack(pady=20)

    def remove():
        if is_new is False:
            # print("erase circle")
            C.delete(circ)
            del bends[(col, row)]# remove bend from array
            close()

    if is_new is True:
        remove_button = Button(menu, text="Remove Bend", command=remove, state=DISABLED)
    else:
        remove_button = Button(menu, text="Remove Bend", command=remove, bg="red")
    remove_button.pack(pady=20)

    def place():
        if is_new is True:
            #bends.append(Draft_Bend(y//10-1, bendiness.get(), x//10-1))
            bends[(col, row)] = Draft_Bend(y//10-1, bendiness.get(), x//10-1)
            print(bends)
        else:
            #bends.remove(???) make sure it's overriden
            #bends.append(Draft_Bend(y//10-1, bendiness.get(), x//10-1))
            bends[(col, row)] = Draft_Bend(y//10-1, bendiness.get(), x//10-1)
            print(bends)
        close()

    if is_new is True:
        place_button = Button(menu, text="Place", command=place, bg="green")
    else:
        place_button = Button(menu, text="Save", command=place, bg="green")
    place_button.pack(pady=20)

    def set_bendiness(e):
        print(bendiness.get())

    bendiness = DoubleVar()
    scale = Scale(menu, variable=bendiness, from_=0, to=1, resolution=0.01, length=150, orient=HORIZONTAL, label="Bendiness", command=set_bendiness)
    if is_new is False: # set default to be current val
        # scale.set(bends[(col, row)].bendiness) both work
        bendiness.set(bends[(col, row)].bendiness)
    scale.pack(side=TOP)

    menu.protocol('WM_DELETE_WINDOW', cancel)


def clicked_on_existing(row: int):
    #print(bends)
    for b in bends.values():
        #print(str(b.position) + "?" + str(row))
        if b.position == row:
            return b
    return None


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
    #print(rect.coords)
    #if 410 >= y >= 10 and 410 >= x >= 10:
    row = y//10-1
    existing = clicked_on_existing(row)
    #print(existing)
    col = x // 10 - 1
    if existing is not None:
        #print(str(existing.bend_dir)+"?"+str(col))
        if existing.bend_dir == col:
            # bring up height and delete menu
            print("edit")
            ring = C.create_oval(x - r, y - r, x + r, y + r, outline="pink", width="3")
            open_menu(col, row, x, y, False, C.find_closest(x, y), ring)
        """
        else:
            # just move the circle 
            print("move")
        """


    elif (h.get()*10+10) >= y >= 10 and (w.get()*10+10) >= x >= 10:
        circ = C.create_oval(x - r, y - r, x + r, y + r, fill="green")
        ring = C.create_oval(x - r, y - r, x + r, y + r, outline="pink", width="3")
        #diamond = C.create_polygon(, fill="gray") todo
        #print(x//10-1)
        #print(y//10-1)
        #bends.append(Draft_Bend(y//10-1, 1, x//10-1))
        open_menu(col, row, x, y, True, circ, ring)


def set_width(e):
    width = w.get()
    #print(width)
    x0, y0, x1, y1 = C.coords(rect)
    x1 = 10 + 10 * float(e)
    C.coords(rect, x0, y0, x1, y1)
    """
        for n in range(0, int(e)):
        C.create_line(10+n*10, 10, 10+n*10, 30)
    for m in range(0, (y1-10)//10):
        C.create_line(10, 10+m*10, 10+10*w.get(), 10+m*10)
    """
    # todo adjust bend diamond heights


def set_height(e):
    height = h.get()
    #print(height)
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
    #switch from draft_bends to bends here by calculating bendiness
    oob = []
    if len(bends.values()) > 0:
        #bends = bends.sort()
        processed_bends = []
        for b in bends.values():
            if b.bend_dir > w.get():
                oob.append(b)
            else:
                ht = round(b.bendiness*float(w.get()/4))
                processed_bends.append(Bend(b.position, ht, b.bend_dir))
        print(processed_bends)
        if len(oob) > 0: # warn if there are bends outside of width
            coords = ""
            for b in oob:
                d = str(b.bend_dir)
                p = str(b.position)
                coords+="("+d+", "+p+"), "

            messagebox.showinfo("Warning", "Bends at the following coordinates" + coords + "are outside of the tube's width and will be ignored")
        processed_bends.sort()
        end_len = h.get()-processed_bends[len(processed_bends)-1].position
        export_knitout(w.get() // 2, end_len, processed_bends, E1.get())
    else:
        export_tube()


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
    #bends: [Draft_Bend] = []
    bends = dict() # map from coordinates to Draft_Bends
    filename = "snek"
    #circles:

    window = tk.Tk()
    top = tk.Frame(master=window)
    top.pack()

    instructions = StringVar()
    label = Label(top, textvariable=instructions, justify=LEFT)
    instructions.set("Welcome to Snake Designer!\nPick your height and width.\nClick on the tube to place bends. There can be at most one bend per row.\nPretend that the left and right edges of the rectangle are connected to form a tube.\nClick KNIT to generate the Knitout file for your snake!\n")
    label.pack()

    tube = tk.Frame(master=window)
    tube.pack()

    w = IntVar()
    scale = Scale(tube, variable=w, from_=8, to=40, length=400, resolution=2, orient=HORIZONTAL, label="circumference", command=set_width)
    scale.pack(side=TOP)

    h = IntVar()
    scale = Scale(tube, variable=h, from_=2, to=40, length=400, resolution=1, orient=VERTICAL, label="num of rows", command=set_height)
    scale.pack(side=LEFT)

    C = tk.Canvas(tube, bg="blue", height=420, width=420)
    coord = 10, 50, 240, 210
    rect = C.create_rectangle(10, 10, 90, 30, fill="yellow")
    for n in range(0, 41):
        C.create_line(10+n*10, 10, 10+n*10, 410)
    for m in range(0, 41):
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

    btn = Button(btm, text="KNIT", command=adjust_params)
    btn.pack(side=RIGHT)

    window.mainloop()


