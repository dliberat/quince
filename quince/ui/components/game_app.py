"""
Root tkinter window.
"""
import tkinter as tk


class GameApp(tk.Tk):
    """Root tkinter window hosting the entire app.
    """
    def __init__(self, AboutFactory, TopMenuFactory):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Quince")
        self.minsize(800, 600)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        self.about_factory = AboutFactory
        self.frames['TopMenu'] = TopMenuFactory.generate(self.container,
                                                         self._start_new_game)
        self.frames['TopMenu'].grid(row=0, column=0, sticky="nsew")

        self._build_menus()
        self.show_frame('TopMenu')

    def _start_new_game(self, game_frame_factory):
        previous_game = self.frames.get("GameFrame", None)

        if previous_game is not None:
            previous_game.destroy()

        frame = game_frame_factory.generate(self.container)
        self.frames['GameFrame'] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame('GameFrame')

    def show_frame(self, controller):
        """
            Raises a frame to the top of the view.

        Args:
            controller - tk frame to raise to the top of the view
        """
        frame = self.frames[controller]
        frame.tkraise()

    def _build_menus(self):
        """
            Generates the file menu, etc.
        """
        menubar = tk.Menu(self)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New Game",
                             command=lambda: self.show_frame("TopMenu"))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # probably unnecessary, but here for legacy compatibility
        self.option_add('*tearOff', tk.FALSE)
        self.config(menu=menubar)

    def _show_about(self):
        self.about_factory.generate(self)
