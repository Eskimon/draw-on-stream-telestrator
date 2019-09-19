import socket
import queue
import threading
import tkinter as tk
import tkinter.font as tkFont


the_queue = queue.Queue()

HOST = 'localhost'
PORT = 4816


class Painter():

    DEFAULT = {
        'line': 5.0,
        'color': '#000000',
        'background': '#ffffff',
        'mode': 'pen',
    }

    def __init__(self):
        self.root = tk.Tk()

        # Load config.json
        # Place the window
        # self.root.geometry("1000x900+10+10")

        # Some variables
        self.items = []
        self.font = tkFont.Font(family='Helvetica', size=20)
        self.text_input = tk.StringVar(self.root)

        # The canvas
        self.c = tk.Canvas(self.root, bg=self.DEFAULT['background'])
        # self.c.grid(row=2, columnspan=6, sticky='nesw')
        self.c.pack(expand=True, fill=tk.BOTH)

        # Initialize some stuff
        self.setup()

        self.root.mainloop()

    def setup(self):
        self.line_width = self.DEFAULT['line']
        self.start_x = None
        self.start_y = None
        self.ghost = None
        self.color = self.DEFAULT['color']
        self.text_input.set('')
        self.mode = self.DEFAULT['mode']
        self.c.bind('<Button-1>', self.draw_start)
        self.c.bind('<B1-Motion>', self.draw_motion)
        self.c.bind('<ButtonRelease-1>', self.draw_release)
        self.c.bind('<Motion>', self.motion)
        self.c.bind('<Leave>', self.reset)
        self.root.bind('<Key>', self.key_up)
        self.root.after(100, self.check_queue)

    def check_queue(self):
        while not the_queue.empty():
            message = the_queue.get(block=False).split(' ', 1)
            print('queue got', message)
            # process message
            if message[0] == 'color':
                self.color = message[1]
            elif message[0] == 'clean':
                self.clean_canvas()
            elif message[0] == 'mode':
                self.mode = message[1]
                self.reset(None)
            elif message[0] == 'width':
                width = int(message[1])
                self.line_width = width
                self.font.configure(size=(width * 5))
            elif message[0] == 'text':
                self.text_input.set(message[1])
        # check again later
        self.root.after(100, self.check_queue)

    def key_up(self, event):
        ctrl = (event.state & 0x4) != 0
        if event.keysym == 'z' and ctrl:
            if len(self.items):
                item = self.items[-1]
                self.c.delete(item)
                self.items.pop()
        if event.keysym == 'w' and ctrl:
            the_queue.put('clean')
        if event.char == 'r':
            the_queue.put('mode rectangle')
        if event.char == 'e':
            the_queue.put('mode ellipse')
        if event.char == 'p':
            the_queue.put('mode pen')
        if event.char == 'l':
            the_queue.put('mode line')
        if event.char == '+':
            value = int(min(10, self.line_width + 1))
            the_queue.put('width {}'.format(value))
        if event.char == '-':
            value = int(max(1, self.line_width - 1))
            the_queue.put('width {}'.format(value))

    def clean_canvas(self):
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
            width = self.line_width / 2
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
            self.mode = 'pen'
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
                        data = conn.recv(1024)
                        if not data:
                            break
                        data = data.decode()
                        print('received:', data)
                        the_queue.put(data)
            print('socket disconnected')


if __name__ == '__main__':
    SocketThread()
    Painter()
