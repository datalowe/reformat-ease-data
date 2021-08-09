# python built-in packages
import tkinter as tk
from tkinter import (
    filedialog, 
    messagebox,
    ttk,
)

# local
import reformat_exp_data
from custom_errors import (
    MissingFilesException, 
    CorruptHDF5Exception,
    MissingColumnException,
)

CHECK_EXCEPTIONS = (
    MissingFilesException, 
    CorruptHDF5Exception, 
    MissingColumnException
)

class Application(tk.Frame):
    BUTTON_PADY = 10
    LABEL_PADY = 5

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.place(relx=0.1, rely=0.1, relheight=0.8, relwidth=0.8)
        self.create_interface()
        self.sel_input_dir = ''
        self.sel_output_dir = ''

    def create_interface(self):
        # data input specification
        self.sel_inp_label = ttk.Label(
            self,
            text="Specify experiment raw output data directory ('data')"
        )
        self.sel_inp_label.pack(
            side='top',
            pady=self.LABEL_PADY
        )
        self.sel_inp_btn = ttk.Button(self)
        self.sel_inp_btn["text"] = "Select directory"
        self.sel_inp_btn["command"] = self.select_input_dir
        self.sel_inp_btn.pack(
            side='top',
            pady=self.BUTTON_PADY
        )

        # data output specification
        self.sel_out_label = ttk.Label(
            self, 
            text="Specify directory to save reformatted data to"
        )
        self.sel_out_label.pack(
            side='top',
            pady=self.LABEL_PADY
        )
        self.sel_out_btn = ttk.Button(self)
        self.sel_out_btn["text"] = "Select directory"
        self.sel_out_btn["command"] = self.select_output_dir
        self.sel_out_btn.pack(
            side="top",
            pady=self.BUTTON_PADY
        )

        # run reformatting
        self.desc_txt = tk.StringVar()
        self.desc_txt.set("Please select directories as instructed above.")
        self.desc_cmd = ttk.Label(
            self, 
            textvariable=self.desc_txt
        )
        self.desc_cmd.pack(
            side='top',
            pady=self.LABEL_PADY+10
        )
        self.run_reformat_btn = ttk.Button(self)
        self.run_reformat_btn["text"] = "Reformat data"
        self.run_reformat_btn["command"] = self.reformat_data
        self.run_reformat_btn.pack(
            side='top',
            pady=self.BUTTON_PADY - 10
        )

        # reformatting process message
        self.status_txt = tk.StringVar()
        self.status_txt.set("")
        self.status_label = ttk.Label(
            self, 
            textvariable=self.status_txt
        )
        self.status_label.pack(
            side='top',
            pady=self.LABEL_PADY
        )

        # quit application button
        self.quit = ttk.Button(
            self, 
            text="QUIT",
            command=self.master.destroy
        )
        self.quit.pack(
            side="bottom"
        )


    def select_input_dir(self):
        self.sel_input_dir = filedialog.askdirectory(
            title="Specify experiment raw output data directory ('data')",
        )
        self.update_desc()
    
    def select_output_dir(self):
        self.sel_output_dir = filedialog.askdirectory(
            title="Specify directory to save reformatted data to",
        )
        self.update_desc()
    
    def update_desc(self):
        if self.sel_input_dir and self.sel_output_dir:
            self.desc_txt.set((
                f'Using data from: {self.sel_input_dir}\n'
                f'Exporting reformatted data to: {self.sel_output_dir}'
            ))

    def reformat_data(self):
        self.status_txt.set("Reformatting, please wait...")
        if not (self.sel_input_dir and self.sel_output_dir):
            messagebox.showwarning(
                title='Directories not specified', 
                message=(
                    'You must specify valid directories before running '
                    'the script. Please use the top buttons to specify '
                    'directories.'
                )
            )
            self.status_txt.set("")
            return
        try:
            reformat_exp_data.reformat_data(
                self.sel_input_dir,
                self.sel_output_dir,
            )
        except CHECK_EXCEPTIONS as e:
            messagebox.showwarning(
                title='Error during processing', 
                message=(
                    str(e)
                )
            )
            self.status_txt.set("")
            return
        self.status_txt.set("Reformatting done!")

root = tk.Tk()

# define general layout
root.title('REFORMAT EASE ET data')

window_width = 600
window_height = 400

# get the screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# find the center point
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

# set the position of the window to the center of the screen
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')


app = Application(master=root)
app.mainloop()
