import json
import queue
import socket
import threading
import time
import tkinter as tk
from tkinter.colorchooser import askcolor
import tkinter.font as tkFont


the_queue = queue.Queue()

HOST = 'localhost'
PORT = 4816


class Commander():

    DEFAULT = {
        'width': 5.0,
        'color': '#000000',
        'background': '#ffffff',
        'mode': 'pen',
        'alpha': 80,
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DrawOnStream - Commander")

        # Some variables
        self.items = []
        self.font = tkFont.Font(family='Helvetica', size=20)
        self.text_input = tk.StringVar(self.root)

        # Build the interface
        self.pen_button = tk.Button(self.root, text='pen', command=self.use_pen)
        self.pen_button.grid(row=0, column=0)

        self.rectangle_button = tk.Button(self.root, text='rect', command=self.use_rect)
        self.rectangle_button.grid(row=0, column=1)

        self.ellipse_button = tk.Button(self.root, text='ellipse', command=self.use_ellipse)
        self.ellipse_button.grid(row=0, column=2)

        self.color_button = tk.Button(self.root, text='color', command=self.choose_color)
        self.color_button.grid(row=0, column=3)

        self.bg_color_button = tk.Button(self.root, text='background', command=self.choose_bg_color)
        self.bg_color_button.grid(row=0, column=4)

        self.eraser_button = tk.Button(self.root, text='eraser', command=self.use_eraser)
        self.eraser_button.grid(row=0, column=5)

        self.choose_size_button = tk.Scale(self.root, from_=1, to=10, orient=tk.HORIZONTAL, command=self.update_width)
        self.choose_size_button.set(self.DEFAULT['width'])
        self.choose_size_button.grid(row=0, column=6)

        self.choose_alpha_button = tk.Scale(self.root, from_=1, to=100, orient=tk.HORIZONTAL, command=self.update_alpha)
        self.choose_alpha_button.set(self.DEFAULT['alpha'])
        self.choose_alpha_button.grid(row=0, column=7)

        self.clean_button = tk.Button(self.root, text='clean', command=self.clean)
        self.clean_button.grid(row=0, column=8)

        self.undo_button = tk.Button(self.root, text='undo', command=self.undo)
        self.undo_button.grid(row=0, column=9)

        self.text_entry = tk.Entry(self.root, width=50, textvariable=self.text_input)
        self.text_entry.grid(row=1, columnspan=9)
        self.text_button = tk.Button(self.root, text='text', command=self.use_text)
        self.text_button.grid(row=1, column=9)

        # Initialize some stuff
        self.setup()

        self.root.mainloop()

    def setup(self):
        # Load json config
        try:
            config = json.load(open('config.json'))
        except FileNotFoundError:
            config = {}
        self.line_width = config.get('width', self.DEFAULT['width'])
        self.color = config.get('color', self.DEFAULT['color'])
        self.bg_color = config.get('background', self.DEFAULT['background'])
        self.mode = config.get('mode', self.DEFAULT['mode'])
        self.alpha = config.get('alpha', self.DEFAULT['alpha'])

        self.color_button.configure(background=self.color)
        self.bg_color_button.configure(background=self.bg_color)
        self.choose_size_button.set(self.line_width)
        self.choose_alpha_button.set(self.alpha)

        self.active_button = self.pen_button
        self.start_x = None
        self.start_y = None
        self.ghost = None
        self.text_input.set('')

    def use_pen(self):
        self.mode = 'pen'
        self.activate_button(self.pen_button)
        the_queue.put('mode {}'.format(self.mode).encode())

    def use_rect(self):
        self.mode = 'rectangle'
        self.activate_button(self.rectangle_button)
        the_queue.put('mode {}'.format(self.mode).encode())

    def use_ellipse(self):
        self.mode = 'ellipse'
        self.activate_button(self.ellipse_button)
        the_queue.put('mode {}'.format(self.mode).encode())

    def choose_color(self):
        color = askcolor(color=self.color)[1]
        if not color:
            return
        self.color = color
        self.color_button.configure(background=color)
        the_queue.put('color {}'.format(self.color).encode())

    def choose_bg_color(self):
        color = askcolor(color=self.bg_color)[1]
        if not color:
            return
        self.bg_color = color
        self.bg_color_button.configure(background=color)
        the_queue.put('background {}'.format(self.bg_color).encode())

    def use_eraser(self):
        self.mode = 'eraser'
        self.activate_button(self.eraser_button)
        the_queue.put('mode {}'.format(self.mode).encode())

    def use_text(self):
        self.mode = 'text'
        self.activate_button(self.text_button)
        the_queue.put('text {}'.format(self.text_input.get()).encode())
        the_queue.put('mode {}'.format(self.mode).encode())

    def activate_button(self, some_button):
        self.active_button.config(relief=tk.RAISED)
        some_button.config(relief=tk.SUNKEN)
        self.active_button = some_button

    def update_width(self, value):
        value = int(value)
        self.line_width = value
        self.font.configure(size=(value * 5))
        the_queue.put('width {}'.format(value).encode())

    def update_alpha(self, value):
        value = int(value)
        self.alpha = value
        the_queue.put('alpha {}'.format(value).encode())

    def clean(self):
        the_queue.put('clean'.encode())

    def undo(self):
        the_queue.put('undo'.encode())


class SocketThread(threading.Thread):

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.start()

    def run(self):
        while True:
            connected = False
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                i = 0
                while not connected:
                    i += 1
                    try:
                        s.connect((HOST, PORT))
                        connected = True
                        print('Commander socket online')
                    except socket.error as e:
                        print("Commander socket failed to connect (trial {})".format(i))
                        print(e)
                        time.sleep(2)

                while True:
                    while not the_queue.empty():
                        message = the_queue.get(block=False)
                        print('queue got:', message)
                        s.sendall(message)
            print('socket disconnected')


if __name__ == '__main__':
    SocketThread()
    Commander()
