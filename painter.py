import json
import math
import queue
import socket
import threading
import time
import tkinter as tk
import tkinter.font as tkFont

from functools import partial
from tkinter.colorchooser import askcolor


the_queue = queue.Queue()

HOST = 'localhost'
PORT = 4816

DEFAULT = {
    'width': 5.0,
    'color': '#000000',
    'background': '#ffffff',
    'mode': 'pen',
    'alpha': 80,
    'fill': None,
}


class StatusBar(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.strings = {}
        self.strings['color'] = tk.StringVar()
        self.strings['bg_color'] = tk.StringVar()
        self.strings['mode'] = tk.StringVar()
        self.strings['fill'] = tk.StringVar()
        self.strings['width'] = tk.StringVar()
        self.strings['alpha'] = tk.StringVar()
        self.strings['win_position'] = tk.StringVar()
        self.strings['win_size'] = tk.StringVar()
        self.labels = {}
        for idx, var in enumerate(self.strings):
            label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                             textvariable=self.strings[var],
                             font=('arial', 10, 'normal'),
                             padx=5)
            # label.pack(fill=tk.X)
            label.grid(row=0, column=idx)
            self.labels[var] = label
        self.pack()

    def update_status(self, **kwargs):
        if 'color' in kwargs.keys():
            self.strings['color'].set('color: {}'.format(kwargs['color']))
            self.labels['color'].configure(bg=kwargs['color'])
        if 'bg_color' in kwargs.keys():
            self.strings['bg_color'].set('bg_color: {}'.format(kwargs['bg_color']))
            self.labels['bg_color'].configure(bg=kwargs['bg_color'])
        if 'mode' in kwargs.keys():
            self.strings['mode'].set('mode: {}'.format(kwargs['mode']))
        if 'fill' in kwargs.keys():
            self.strings['fill'].set('fill: {}'.format('on' if kwargs['fill'] else 'off'))
        if 'width' in kwargs.keys():
            self.strings['width'].set('width: {}'.format(kwargs['width']))
        if 'alpha' in kwargs.keys():
            self.strings['alpha'].set('opacity: {}'.format(kwargs['alpha']))
        if 'win_position' in kwargs.keys():
            self.strings['win_position'].set('({}, {})'.format(kwargs['win_position'][0], kwargs['win_position'][1]))
        if 'win_size' in kwargs.keys():
            self.strings['win_size'].set('({}, {})'.format(kwargs['win_size'][0], kwargs['win_size'][1]))


class MenuBar(tk.Frame):

    QUICK_COLORS = [
        '#FFFFFF',
        '#000000',
        '#1abc9c',
        '#2ecc71',
        '#3498db',
        '#9b59b6',
        '#34495e',
        '#f1c40f',
        '#e67e22',
        '#e74c3c',
        '#ecf0f1',
        '#95a5a6',
    ]

    def __init__(self, master):
        super().__init__(master)

        # Some variables
        self.text_input = tk.StringVar(self)
        self.fill_status = tk.IntVar(self)

        self.buttons = {}

        # Build the interface
        self.buttons['pen'] = tk.Button(self, text='pen', command=self.use_pen)
        self.buttons['pen'].grid(row=0, column=0)

        self.buttons['rectangle'] = tk.Button(self, text='rect', command=self.use_rect)
        self.buttons['rectangle'].grid(row=0, column=1)

        self.buttons['ellipse'] = tk.Button(self, text='ellipse', command=self.use_ellipse)
        self.buttons['ellipse'].grid(row=0, column=2)

        self.buttons['color'] = tk.Button(self, text='color', command=self.choose_color)
        self.buttons['color'].grid(row=0, column=3)

        self.buttons['bg_color'] = tk.Button(self, text='background', command=self.choose_bg_color)
        self.buttons['bg_color'].grid(row=0, column=4)

        self.buttons['eraser'] = tk.Button(self, text='eraser', command=self.use_eraser)
        self.buttons['eraser'].grid(row=0, column=5)

        self.choose_size_button = tk.Scale(self, from_=1, to=10, orient=tk.HORIZONTAL, command=self.update_width)
        self.choose_size_button.set(DEFAULT['width'])
        self.choose_size_button.grid(row=0, column=6)

        self.choose_alpha_button = tk.Scale(self, from_=1, to=100, orient=tk.HORIZONTAL, command=self.update_alpha)
        self.choose_alpha_button.set(DEFAULT['alpha'])
        self.choose_alpha_button.grid(row=0, column=7)

        self.wipe_button = tk.Button(self, text='wipe', command=self.wipe)
        self.wipe_button.grid(row=0, column=8)

        self.undo_button = tk.Button(self, text='undo', command=self.undo)
        self.undo_button.grid(row=0, column=9)

        self.buttons['fill'] = tk.Checkbutton(self, text='fill shapes', variable=self.fill_status, command=self.fill)
        self.buttons['fill'].grid(row=0, column=10)

        self.frame_quick_colors = tk.Frame(self)
        self.frame_quick_colors.grid(row=0, column=11)

        for color in self.QUICK_COLORS:
            btn = tk.Button(self.frame_quick_colors, relief='ridge', overrelief='ridge', bg=color,
                            command=partial(self.quick_color, color), activebackground=color)
            btn.pack(side=tk.LEFT)

        self.text_entry = tk.Entry(self, width=75, textvariable=self.text_input)
        self.text_entry.grid(row=0, column=12)
        self.buttons['text'] = tk.Button(self, text='text', command=self.use_text)
        self.buttons['text'].grid(row=0, column=13)

        self.active_button = self.buttons['pen']

    def update_status(self, **kwargs):
        if 'color' in kwargs.keys():
            self.buttons['color'].configure(background=kwargs['color'])
        if 'bg_color' in kwargs.keys():
            self.buttons['bg_color'].configure(background=kwargs['bg_color'])
        if 'mode' in kwargs.keys():
            self.activate_button(self.buttons[kwargs['mode']])
        if 'fill' in kwargs.keys():
            self.fill_status.set(1 if kwargs['fill'] else 0)
        if 'width' in kwargs.keys():
            self.choose_size_button.set(kwargs['width'])
        if 'alpha' in kwargs.keys():
            self.choose_alpha_button.set(kwargs['alpha'])

    def use_pen(self):
        self.activate_button(self.buttons['pen'])
        the_queue.put('mode pen')

    def use_rect(self):
        self.activate_button(self.buttons['rectangle'])
        the_queue.put('mode rectangle')

    def use_ellipse(self):
        self.activate_button(self.buttons['ellipse'])
        the_queue.put('mode ellipse')

    def choose_color(self):
        color = self.buttons['color'].configure()['background'][4]
        color = askcolor(color=color)[1]
        if not color:
            return
        self.buttons['color'].configure(background=color)
        the_queue.put('color {}'.format(color))

    def choose_bg_color(self):
        color = self.buttons['bg_color'].configure()['background'][4]
        color = askcolor(color=color)[1]
        if not color:
            return
        self.buttons['bg_color'].configure(background=color)
        the_queue.put('background {}'.format(color))

    def use_eraser(self):
        self.activate_button(self.buttons['eraser'])
        the_queue.put('mode eraser')

    def use_text(self):
        self.activate_button(self.buttons['text'])
        the_queue.put('text {}'.format(self.text_input.get()))
        the_queue.put('mode text')

    def activate_button(self, some_button):
        self.active_button.config(relief=tk.RAISED)
        some_button.config(relief=tk.SUNKEN)
        self.active_button = some_button

    def update_width(self, value):
        value = int(value)
        the_queue.put('width {}'.format(value))

    def update_alpha(self, value):
        value = int(value)
        the_queue.put('alpha {}'.format(value))

    def wipe(self):
        the_queue.put('wipe')

    def undo(self):
        the_queue.put('undo')

    def fill(self):
        the_queue.put('fill {}'.format(self.fill_status.get()))

    def quick_color(self, color):
        self.buttons['color'].configure(background=color)
        the_queue.put('color {}'.format(color))


class Painter():

    WIN_TITLE = 'DrawOnStream - Painter'

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self.WIN_TITLE)

        # Some variables
        self.items = []
        self.font = tkFont.Font(family='Helvetica', size=20)
        self.text_input = tk.StringVar(self.root)
        self.fill_color = None
        self.letter_capture = False
        self.shift_pressed = False
        self.alt_pressed = False

        # The canvas
        self.menu_bar = MenuBar(self.root)
        self.menu_bar.pack(side=tk.TOP, fill=tk.X)

        self.c = tk.Canvas(self.root)
        self.c.pack(expand=True, fill=tk.BOTH)

        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize some stuff
        self.setup()
        self.status_bar.update_status(
            width=self.line_width,
            color=self.color,
            bg_color=self.bg_color,
            mode=self.mode,
            alpha=self.alpha,
            fill=self.fill_color
        )
        self.menu_bar.update_status(
            width=self.line_width,
            color=self.color,
            bg_color=self.bg_color,
            mode=self.mode,
            alpha=self.alpha,
            fill=self.fill_color
        )

        self.root.wait_visibility(self.root)
        self.root.wm_attributes('-alpha', self.alpha / 100.)

        self.root.bind("<Configure>", self.on_configure)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_configure(self, event):
        geometry = self.root.geometry()
        geometry = geometry.replace('x', '#')
        geometry = geometry.replace('+', '#')
        geometry = geometry.split('#')
        self.status_bar.update_status(win_position=(geometry[2], geometry[3]))
        self.status_bar.update_status(win_size=(geometry[0], geometry[1]))

    def on_closing(self):
        # dump position/size/parameters to a json file
        config = {
            'width': self.line_width,
            'color': self.color,
            'background': self.bg_color,
            'mode': self.mode,
            'alpha': self.alpha,
            'fill': self.fill_color,
            'geometry': self.root.geometry()
        }
        print(config)
        json.dump(config, open('config.json', 'w'), indent=2)
        self.root.destroy()

    def setup(self):
        # Load json config
        try:
            config = json.load(open('config.json'))
        except FileNotFoundError:
            config = {}
        self.line_width = int(config.get('width', DEFAULT['width']))
        self.font.configure(size=(self.line_width * 5))
        self.color = config.get('color', DEFAULT['color'])
        self.bg_color = config.get('background', DEFAULT['background'])
        self.mode = config.get('mode', DEFAULT['mode'])
        self.alpha = int(config.get('alpha', DEFAULT['alpha']))
        self.fill_color = config.get('fill', DEFAULT['fill'])
        geometry = config.get('geometry', None)
        if geometry:
            self.root.geometry(geometry)
        self.c.configure(bg=self.bg_color)

        self.text_input.set('')
        self.start_x = None
        self.start_y = None
        self.ghost = None
        self.c.bind('<Button-1>', self.draw_start)
        self.c.bind('<Shift-Button-1>', self.draw_start_with_shift)
        self.c.bind('<Alt-Button-1>', self.draw_start_with_alt)
        self.c.bind('<B1-Motion>', self.draw_motion)
        self.c.bind('<ButtonRelease-1>', self.draw_release)
        self.c.bind('<Button-3>', self.draw_line_start)
        self.c.bind('<B3-Motion>', self.draw_line_motion)
        self.c.bind('<ButtonRelease-3>', self.draw_line_release)
        self.c.bind('<Motion>', self.motion)
        self.c.bind('<Leave>', self.reset)
        self.root.bind('<Key>', self.key_up)
        self.root.after(100, self.check_queue)

    def check_queue(self):
        while not the_queue.empty():
            message = the_queue.get(block=False).split(' ', 1)
            # print('queue got', message)
            # process message
            if message[0] == 'color':
                self.color = message[1]
                self.status_bar.update_status(color=self.color)
                self.menu_bar.update_status(color=self.color)
            elif message[0] == 'background':
                self.bg_color = message[1]
                self.c.configure(bg=self.bg_color)
                self.status_bar.update_status(bg_color=self.bg_color)
                self.menu_bar.update_status(bg_color=self.bg_color)
            elif message[0] == 'wipe':
                self.wipe_canvas()
            elif message[0] == 'undo':
                self.undo()
            elif message[0] == 'mode':
                self.mode = message[1]
                self.reset(None)
                self.status_bar.update_status(mode=self.mode)
                self.menu_bar.update_status(mode=self.mode)
            elif message[0] == 'width':
                width = int(message[1])
                self.line_width = width
                self.font.configure(size=(width * 5))
                self.status_bar.update_status(width=self.line_width)
                self.menu_bar.update_status(width=self.line_width)
            elif message[0] == 'alpha':
                self.alpha = int(message[1])
                self.root.wm_attributes('-alpha', self.alpha / 100.)
                self.status_bar.update_status(alpha=self.alpha)
                self.menu_bar.update_status(alpha=self.alpha)
            elif message[0] == 'text':
                self.text_input.set(message[1])
                self.status_bar.update_status(text=message[1])
                self.menu_bar.update_status(text=message[1])
            elif message[0] == 'fill':
                self.fill_color = self.color if int(message[1]) else None
                self.status_bar.update_status(fill=self.fill_color)
                self.menu_bar.update_status(fill=self.fill_color)
        # check again later
        self.root.after(100, self.check_queue)

    def key_up(self, event):
        ctrl = (event.state & 0x4) != 0
        # print(event, '---', self.letter_capture)
        if event.keysym == 'Escape':
            self.letter_capture = False
            the_queue.put('mode pen')
            return
        if self.letter_capture:
            if event.char and event.char.isprintable():
                the_queue.put('text {}'.format(event.char))
        if ctrl:
            if event.keysym == 'l':
                self.letter_capture = True
                the_queue.put('mode text')
            if event.keysym == 'z':
                the_queue.put('undo')
            if event.keysym == 'w':
                the_queue.put('wipe')
            if event.char == '+':
                value = int(min(100, self.alpha + 5))
                the_queue.put('alpha {}'.format(value))
            if event.char == '-':
                value = int(max(1, self.alpha - 5))
                the_queue.put('alpha {}'.format(value))
            if event.keysym == 'r':
                the_queue.put('alpha {}'.format(DEFAULT['alpha']))
        else:
            if event.char == 'r':
                the_queue.put('mode rectangle')
            if event.char == 'e':
                the_queue.put('mode ellipse')
            if event.char == 'p':
                the_queue.put('mode pen')
            if event.char == 'f':
                the_queue.put('fill {}'.format(0 if self.fill_color else 1))
            if event.char == '+':
                value = int(min(10, self.line_width + 1))
                the_queue.put('width {}'.format(value))
            if event.char == '-':
                value = int(max(1, self.line_width - 1))
                the_queue.put('width {}'.format(value))

    def undo(self):
        if len(self.items):
            item = self.items[-1]
            self.c.delete(item)
            self.items.pop()

    def wipe_canvas(self):
        self.items.clear()
        self.c.delete("all")

    def reset(self, event):
        if self.ghost:
            self.c.delete(self.ghost)
            self.ghost = None
        self.start_x = None
        self.start_y = None
        self.shift_pressed = False
        self.alt_pressed = False

    def motion(self, event):
        if self.mode in ['pen', 'eraser']:
            if self.ghost:
                self.c.delete(self.ghost)
            width = self.line_width / 2
            self.ghost = self.c.create_oval(event.x - width, event.y - width, event.x + width, event.y + width,
                                            outline='black', width=1)
        if self.mode == 'text':
            if self.ghost:
                self.c.delete(self.ghost)
            self.ghost = self.c.create_text(event.x, event.y,
                                            text=self.text_input.get(), fill=self.color, font=self.font)

    def draw_start_with_shift(self, event):
        self.shift_pressed = True
        self.draw_start(event)

    def draw_start_with_alt(self, event):
        self.alt_pressed = True
        self.draw_start(event)

    def draw_start(self, event):
        self.start_x = event.x
        self.start_y = event.y

        if self.mode in ['pen', 'eraser']:
            paint_color = self.color if self.mode == 'pen' else self.bg_color
            self.items.append(self.c.create_line(self.start_x, self.start_y, event.x, event.y,
                                                 width=self.line_width, fill=paint_color,
                                                 capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36))
        if self.mode == 'text':
            self.items.append(self.c.create_text(event.x, event.y,
                                                 text=self.text_input.get(), fill=self.color, font=self.font))

    def draw_motion(self, event):
        if self.mode in ['pen', 'eraser']:
            paint_color = self.color if self.mode == 'pen' else self.bg_color
            self.items.append(self.c.create_line(self.start_x, self.start_y, event.x, event.y,
                                                 width=self.line_width, fill=paint_color,
                                                 capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36))
            self.start_x = event.x
            self.start_y = event.y

        if self.mode == 'rectangle':
            if self.ghost:
                self.c.delete(self.ghost)
            if self.shift_pressed:
                rect_x = event.x
                rect_y = self.start_y - (self.start_x - event.x)
                self.ghost = self.c.create_rectangle(self.start_x, self.start_y, rect_x, rect_y,
                                                     outline=self.color, fill=self.fill_color, width=self.line_width)
            elif self.alt_pressed:
                radius = min(self.start_x - event.x, self.start_y - event.y)
                rect_x = self.start_x + radius
                rect_y = self.start_y + radius
                start_x = self.start_x - radius
                start_y = self.start_y - radius
                self.ghost = self.c.create_rectangle(start_x, start_y, rect_x, rect_y,
                                                     outline=self.color, fill=self.fill_color, width=self.line_width)
            else:
                self.ghost = self.c.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                                     outline=self.color, fill=self.fill_color, width=self.line_width)

        if self.mode == 'ellipse':
            if self.ghost:
                self.c.delete(self.ghost)
            if self.shift_pressed:
                rect_x = event.x
                rect_y = self.start_y - (self.start_x - event.x)
                self.ghost = self.c.create_oval(self.start_x, self.start_y, rect_x, rect_y,
                                                outline=self.color, fill=self.fill_color, width=self.line_width)
            elif self.alt_pressed:
                radius = math.sqrt(((self.start_x - event.x)**2) + ((self.start_y - event.y)**2))
                rect_x = self.start_x + radius
                rect_y = self.start_y + radius
                start_x = self.start_x - radius
                start_y = self.start_y - radius
                self.ghost = self.c.create_oval(start_x, start_y, rect_x, rect_y,
                                                outline=self.color, fill=self.fill_color, width=self.line_width)
            else:
                self.ghost = self.c.create_oval(self.start_x, self.start_y, event.x, event.y,
                                                outline=self.color, fill=self.fill_color, width=self.line_width)

    def draw_release(self, event):
        if self.mode == 'rectangle':
            if self.shift_pressed:
                rect_x = event.x
                rect_y = self.start_y - (self.start_x - event.x)
                self.items.append(self.c.create_rectangle(self.start_x, self.start_y, rect_x, rect_y,
                                                          outline=self.color, fill=self.fill_color, width=self.line_width))
            elif self.alt_pressed:
                radius = min(self.start_x - event.x, self.start_y - event.y)
                rect_x = self.start_x + radius
                rect_y = self.start_y + radius
                start_x = self.start_x - radius
                start_y = self.start_y - radius
                self.items.append(self.c.create_rectangle(start_x, start_y, rect_x, rect_y,
                                                          outline=self.color, fill=self.fill_color, width=self.line_width))
            else:
                self.items.append(self.c.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                                          outline=self.color, fill=self.fill_color, width=self.line_width))

        if self.mode == 'ellipse':
            if self.shift_pressed:
                rect_x = event.x
                rect_y = self.start_y - (self.start_x - event.x)
                self.items.append(self.c.create_oval(self.start_x, self.start_y, rect_x, rect_y,
                                                     outline=self.color, fill=self.fill_color, width=self.line_width))
            elif self.alt_pressed:
                radius = math.sqrt(((self.start_x - event.x)**2) + ((self.start_y - event.y)**2))
                rect_x = self.start_x + radius
                rect_y = self.start_y + radius
                start_x = self.start_x - radius
                start_y = self.start_y - radius
                self.items.append(self.c.create_oval(start_x, start_y, rect_x, rect_y,
                                                     outline=self.color, fill=self.fill_color, width=self.line_width))
            else:
                self.items.append(self.c.create_oval(self.start_x, self.start_y, event.x, event.y,
                                                     outline=self.color, fill=self.fill_color, width=self.line_width))

        if self.mode == 'text' and not self.letter_capture:
            self.mode = 'pen'
            self.status_bar.update_status(mode=self.mode)
            self.menu_bar.update_status(mode=self.mode)

        self.reset(None)

    def draw_line_start(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def draw_line_motion(self, event):
        if self.ghost:
            self.c.delete(self.ghost)
        self.ghost = self.c.create_line(self.start_x, self.start_y, event.x, event.y,
                                        width=self.line_width, fill=self.color,
                                        capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)

    def draw_line_release(self, event):
        self.items.append(self.c.create_line(self.start_x, self.start_y, event.x, event.y,
                                             width=self.line_width, fill=self.color,
                                             capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36))
        self.reset(None)


class SocketThread(threading.Thread):

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.start()

    def run(self):

        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        time.sleep(0.1)
                        data = conn.recv(1024)
                        if not data:
                            break
                        data = data.decode()
                        lines = data.split('\n')
                        # print('received:', lines)
                        for line in lines:
                            if line:
                                the_queue.put(line)
            print('socket disconnected')


if __name__ == '__main__':
    SocketThread()
    Painter()
