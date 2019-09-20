import json
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
        'width': 5.0,
        'color': '#000000',
        'background': '#ffffff',
        'mode': 'pen',
        'alpha': 80,
        'fill': None,
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DrawOnStream - Painter")

        # Some variables
        self.items = []
        self.font = tkFont.Font(family='Helvetica', size=20)
        self.text_input = tk.StringVar(self.root)
        self.fill_color = None

        # The canvas
        self.c = tk.Canvas(self.root)
        # self.c.grid(row=2, columnspan=6, sticky='nesw')
        self.c.pack(expand=True, fill=tk.BOTH)

        # Initialize some stuff
        self.setup()

        self.root.wait_visibility(self.root)
        self.root.wm_attributes('-alpha', self.alpha / 100.)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

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
        self.line_width = config.get('width', self.DEFAULT['width'])
        self.color = config.get('color', self.DEFAULT['color'])
        self.bg_color = config.get('background', self.DEFAULT['background'])
        self.mode = config.get('mode', self.DEFAULT['mode'])
        self.alpha = config.get('alpha', self.DEFAULT['alpha'])
        self.fill_color = config.get('fill', self.DEFAULT['fill'])
        geometry = config.get('geometry', None)
        if geometry:
            self.root.geometry(geometry)
        self.c.configure(bg=self.bg_color)

        self.text_input.set('')
        self.start_x = None
        self.start_y = None
        self.ghost = None
        self.c.bind('<Button-1>', self.draw_start)
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
            elif message[0] == 'background':
                self.bg_color = message[1]
                self.c.configure(bg=self.bg_color)
            elif message[0] == 'wipe':
                self.wipe_canvas()
            elif message[0] == 'undo':
                self.undo()
            elif message[0] == 'mode':
                self.mode = message[1]
                self.reset(None)
            elif message[0] == 'width':
                width = int(message[1])
                self.line_width = width
                self.font.configure(size=(width * 5))
            elif message[0] == 'alpha':
                self.alpha = int(message[1])
                self.root.wm_attributes('-alpha', self.alpha / 100.)
            elif message[0] == 'text':
                self.text_input.set(message[1])
            elif message[0] == 'fill':
                self.fill_color = self.color if int(message[1]) else None
        # check again later
        self.root.after(100, self.check_queue)

    def key_up(self, event):
        ctrl = (event.state & 0x4) != 0
        # print(event)
        if ctrl:
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
        else:
            if event.char == 'r':
                the_queue.put('mode rectangle')
            if event.char == 'e':
                the_queue.put('mode ellipse')
            if event.char == 'p':
                the_queue.put('mode pen')
            if event.char == 'l':
                the_queue.put('mode line')
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
            self.ghost = self.c.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                                 outline=self.color, fill=self.fill_color, width=self.line_width)

        if self.mode == 'ellipse':
            if self.ghost:
                self.c.delete(self.ghost)
            self.ghost = self.c.create_oval(self.start_x, self.start_y, event.x, event.y,
                                            outline=self.color, fill=self.fill_color, width=self.line_width)

    def draw_release(self, event):
        if self.mode == 'rectangle':
            self.items.append(self.c.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                                      outline=self.color, fill=self.fill_color, width=self.line_width))
        if self.mode == 'ellipse':
            self.items.append(self.c.create_oval(self.start_x, self.start_y, event.x, event.y,
                                                 outline=self.color, fill=self.fill_color, width=self.line_width))
        if self.mode == 'text':
            self.mode = 'pen'
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
