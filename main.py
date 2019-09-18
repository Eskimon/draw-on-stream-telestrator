import tkinter as tk
from tkinter.colorchooser import askcolor
import tkinter.font as tkFont


class Paint():

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'
    BG_COLOR = 'white'

    mode = 'pen'

    def __init__(self):
        self.root = tk.Tk()

        self.items = []

        self.font = tkFont.Font(family='Helvetica', size=20)

        self.text_input = tk.StringVar(self.root)

        self.pen_button = tk.Button(self.root, text='pen', command=self.use_pen)
        self.pen_button.grid(row=0, column=0)

        self.rectangle_button = tk.Button(self.root, text='rect', command=self.use_rect)
        self.rectangle_button.grid(row=0, column=1)

        self.ellipse_button = tk.Button(self.root, text='ellipse', command=self.use_ellipse)
        self.ellipse_button.grid(row=0, column=2)

        self.color_button = tk.Button(self.root, text='color', command=self.choose_color)
        self.color_button.grid(row=0, column=3)

        self.eraser_button = tk.Button(self.root, text='eraser', command=self.use_eraser)
        self.eraser_button.grid(row=0, column=4)

        self.choose_size_button = tk.Scale(self.root, from_=1, to=10, orient=tk.HORIZONTAL, command=self.update_width)
        self.choose_size_button.set(self.DEFAULT_PEN_SIZE)
        self.choose_size_button.grid(row=0, column=5)

        self.text_entry = tk.Entry(self.root, width=50, textvariable=self.text_input)
        self.text_entry.grid(row=1, columnspan=5)
        self.text_button = tk.Button(self.root, text='text', command=self.use_text)
        self.text_button.grid(row=1, column=5)

        self.c = tk.Canvas(self.root, bg=self.BG_COLOR, width=600, height=600)
        self.c.grid(row=2, columnspan=6)

        self.setup()

        # # create a toplevel menu
        # menubar = tk.Menu(self.root)

        # # create a pulldown menu, and add it to the menu bar
        # filemenu = tk.Menu(menubar, tearoff=0)
        # filemenu.add_command(label="Open", command=self.hello)
        # filemenu.add_command(label="Save", command=self.hello)
        # filemenu.add_separator()
        # filemenu.add_command(label="Exit", command=self.root.quit)
        # menubar.add_cascade(label="File", menu=filemenu)

        # # create more pulldown menus
        # editmenu = tk.Menu(menubar, tearoff=0)
        # editmenu.add_command(label="Cut", command=self.hello)
        # editmenu.add_command(label="Copy", command=self.hello)
        # editmenu.add_command(label="Paste", command=self.hello)
        # menubar.add_cascade(label="Edit", menu=editmenu)

        # helpmenu = tk.Menu(menubar, tearoff=0)
        # helpmenu.add_command(label="About", command=self.hello)
        # menubar.add_cascade(label="Help", menu=helpmenu)

        # # display the menu
        # self.root.config(menu=menubar)

        self.root.mainloop()

    def setup(self):
        self.start_x = None
        self.start_y = None
        self.ghost = None
        self.line_width = self.choose_size_button.get()
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.use_pen()
        self.c.bind('<Button-1>', self.draw_start)
        self.c.bind('<B1-Motion>', self.draw_motion)
        self.c.bind('<ButtonRelease-1>', self.draw_release)
        self.c.bind('<Motion>', self.motion)
        self.c.bind('<Leave>', self.reset)
        self.root.bind('<Key>', self.key_up)

    def hello(self):
        print("hello!")

    def use_pen(self):
        self.mode = 'pen'
        self.activate_button(self.pen_button)

    def use_rect(self):
        self.mode = 'rectangle'
        self.activate_button(self.rectangle_button)

    def use_ellipse(self):
        self.mode = 'ellipse'
        self.activate_button(self.ellipse_button)

    def choose_color(self):
        self.color = askcolor(color=self.color)[1]

    def use_eraser(self):
        self.mode = 'eraser'
        self.activate_button(self.eraser_button)

    def use_text(self):
        self.mode = 'text'
        self.activate_button(self.text_button)

    def activate_button(self, some_button):
        self.active_button.config(relief=tk.RAISED)
        some_button.config(relief=tk.SUNKEN)
        self.active_button = some_button

    def update_width(self, value):
        value = int(value)
        self.line_width = value
        self.font.configure(size=(value * 5))

    def key_up(self, event):
        ctrl = (event.state & 0x4) != 0
        if event.keysym == 'z' and ctrl:
            if len(self.items):
                item = self.items[-1]
                self.c.delete(item)
                self.items.pop()
        if event.keysym == 'w' and ctrl:
            self.items.clear()
            self.c.delete("all")

    def reset(self, event):
        if self.ghost:
            self.c.delete(self.ghost)
            self.ghost = None
        self.start_x = None
        self.start_y = None

    def motion(self, event):
        if self.mode in ['pen', 'eraser']:
            if self.ghost:
                self.c.delete(self.ghost)
            width = self.choose_size_button.get() / 2
            self.ghost = self.c.create_oval(event.x - width, event.y - width, event.x + width, event.y + width,
                                            outline='black', width=1)
        if self.mode == 'text':
            if self.ghost:
                self.c.delete(self.ghost)
            self.ghost = self.c.create_text(event.x, event.y,
                                            text=self.text_input.get(), fill=self.color, font=self.font)

    def draw_start(self, event):
        self.start_x = event.x
        self.start_y = event.y

        if self.mode in ['pen', 'eraser']:
            paint_color = self.color if self.mode == 'pen' else self.BG_COLOR
            self.items.append(self.c.create_line(self.start_x, self.start_y, event.x, event.y,
                                                 width=self.line_width, fill=paint_color,
                                                 capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36))
        if self.mode == 'text':
            self.items.append(self.c.create_text(event.x, event.y,
                                                 text=self.text_input.get(), fill=self.color, font=self.font))

    def draw_motion(self, event):
        if self.mode in ['pen', 'eraser']:
            paint_color = self.color if self.mode == 'pen' else self.BG_COLOR
            self.items.append(self.c.create_line(self.start_x, self.start_y, event.x, event.y,
                                                 width=self.line_width, fill=paint_color,
                                                 capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36))
            self.start_x = event.x
            self.start_y = event.y

        if self.mode == 'rectangle':
            if self.ghost:
                self.c.delete(self.ghost)
            self.ghost = self.c.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                                 outline=self.color, width=self.line_width)

        if self.mode == 'ellipse':
            if self.ghost:
                self.c.delete(self.ghost)
            self.ghost = self.c.create_oval(self.start_x, self.start_y, event.x, event.y,
                                            outline=self.color, width=self.line_width)

    def draw_release(self, event):
        if self.mode == 'rectangle':
            self.items.append(self.c.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                                      outline=self.color, width=self.line_width))
        if self.mode == 'ellipse':
            self.items.append(self.c.create_oval(self.start_x, self.start_y, event.x, event.y,
                                                 outline=self.color, width=self.line_width))
        if self.mode == 'text':
            self.use_pen()
        self.reset(None)


if __name__ == '__main__':
    Paint()
