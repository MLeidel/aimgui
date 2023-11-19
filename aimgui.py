'''
code file: aimgui.py (AI Image GUI)
date: July 2023
AI Image GUI
Generate Images based on text prompts or other images
See: https://platform.openai.com/docs/api-reference/images
Requires ENV variable GPTKEY set to YOUR OpenAI key
date: November 2023
    modified to current OpenAI v1.3.3 API specs
    manual (read-only) aimgui.ini file to include:
        browser = 0|1
        File = 0|1
        output = images/Image.png
        cmodel = dall-e-2|dall-e-3
        vmodel = dall-e-2
        theme = darkly
        size = 1024x1024
        number = 1
'''
import os
import sys
from tkinter import filedialog
from tkinter import messagebox
from tkinter.font import Font
import configparser
import webbrowser
from ttkbootstrap import *
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
import requests
from openai import OpenAI
import datetime

class Application(Frame):
    ''' main class docstring '''
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.pack(fill=BOTH, expand=True, padx=4, pady=4)

        config = configparser.ConfigParser()
        config.read('aimgui.ini')
        self.MyBrowser = config['Main']['browser']
        self.MyFile = config['Main']['file']
        self.MyOutput = config['Main']['output']
        self.MyCmodel = config['Main']['cmodel']  # no set in GUI
        self.MyVmodel = config['Main']['vmodel']  # no set in GUI
        self.MyTheme = config['Main']['theme']  # no set in GUI
        self.MySize = config['Main']['size']
        self.MyNumber = config['Main']['number']

        self.create_widgets()

    def create_widgets(self):
        ''' creates GUI for app '''

        self.vlbl1 = StringVar()
        lbl1 = Label(self, textvariable=self.vlbl1)
        lbl1.grid(row=1, column=1, sticky='e')
        self.vlbl1.set('Output Destination')
        ToolTip(lbl1, "Open generated images in browser\nor write to files or both")

        self.vlbl2 = StringVar()
        lbl = Label(self, textvariable=self.vlbl2)
        lbl.grid(row=2, column=1, sticky='e')
        self.vlbl2.set('Output Path/File')

        self.vlbl3 = StringVar()
        lbl = Label(self, textvariable=self.vlbl3)
        lbl.grid(row=3, column=1, sticky='e')
        self.vlbl3.set('Number of Images')

        self.vlbl4 = StringVar()
        lbl = Label(self, textvariable=self.vlbl4)
        lbl.grid(row=4, column=1, sticky='e')
        self.vlbl4.set('Image Size')

        self.vlbl5 = StringVar()
        lbl5 = Label(self, textvariable=self.vlbl5)
        lbl5.grid(row=5, column=1, sticky='e')
        self.vlbl5.set('Input Image for Variation')
        ToolTip(lbl5, "Image must be png, square,\n256x256, 512x512, or 1024x1024")

        self.vlbl6 = StringVar()
        lbl = Label(self, textvariable=self.vlbl6)
        lbl.grid(row=6, column=1, sticky='e')
        self.vlbl6.set('Text Prompt for Image Creation')


        self.vchkwww = IntVar()
        chkwww = Checkbutton(self, variable=self.vchkwww, text='Browser')
        chkwww.grid(row=1, column=2, sticky='e', padx=4, pady=4)
        self.vchkwww.set(int(self.MyBrowser))  # from aimgui.ini

        self.vchkfile = IntVar()
        chkfile = Checkbutton(self, variable=self.vchkfile, text='File')
        chkfile.grid(row=1, column=3, sticky='w', padx=4, pady=4)
        self.vchkfile.set(int(self.MyFile))  # from aimgui.ini

        self.vout_file = StringVar()
        # self.vout_file.trace("w", self.eventHandler)
        self.out_file = Entry(self, textvariable=self.vout_file, justify="right")
        self.out_file.grid(row=2, column=2, sticky='w', padx=4, pady=4)
        self.vout_file.set(self.MyOutput)  # from aimgui.ini

        btn_out_file = Button(self, text='Open',
                              command=self.btn_out_file_click, bootstyle='outline')
        btn_out_file.grid(row=2, column=3, sticky='w', padx=4, pady=4)

        self.vspn = StringVar(value=0)
        spn = Spinbox(self, textvariable=self.vspn, from_=0, to=10, width=4)
        spn.grid(row=3, column=2, sticky='w', padx=4, pady=4)
        self.vspn.set(int(self.MyNumber))  # from aimgui.ini

        optionlist = ('', '1024x1024', '512x512', '256x256')
        self.vopt_size = StringVar()
        self.vopt_size.set(optionlist[int(self.MySize)])  # from aimgui.ini
        opt_size = OptionMenu(self, self.vopt_size, *optionlist, bootstyle='outline')
        opt_size.grid(row=4, column=2, sticky='w', padx=4, pady=4)

        self.vvar_file = StringVar()
        # self.vvar_file.trace("w", self.eventHandler)
        self.var_file = Entry(self, textvariable=self.vvar_file)
        self.var_file.grid(row=5, column=2, sticky='w', padx=4, pady=4)

        btn_var_file = Button(self, text='Open',
                              command=self.btn_out_var_click, bootstyle='outline')
        btn_var_file.grid(row=5, column=3, sticky='w', padx=4, pady=4)

        self.prompt = Text(self)
        self.prompt.grid(row=7, column=1, columnspan=3, sticky='ew', padx=4, pady=4)
        efont = Font(family="Arial", size=14)
        self.prompt.configure(font=efont)
        self.prompt.config(wrap="word", # wrap=NONE
                           undo=True, # Tk 8.4
                           width=30,
                           height=5,
                           padx=5, # inner margin
                           insertbackground='#fff',   # cursor color
                           tabs=(efont.measure(' ' * 4),))

        btn_create = Button(self, text='Create', command=self.btn_create_click)
        btn_create.grid(row=8, column=1, columnspan=2, sticky='ew', padx=4, pady=4)

        btn_close = Button(self, text='Close',
                           command=self.btn_close_click, bootstyle='outline')
        btn_close.grid(row=8, column=3, sticky='ew', padx=4, pady=4)

    #    _   _                 _ _
    #   | | | | __ _ _ __   __| | | ___ _ __ ___
    #   | |_| |/ _` | '_ \ / _` | |/ _ \ '__/ __|
    #   |  _  | (_| | | | | (_| | |  __/ |  \__ \
    #   |_| |_|\__,_|_| |_|\__,_|_|\___|_|  |___/
    #

    def btn_out_file_click(self):
        ''' Select a directory/file other than the default (./images) '''
        filename = filedialog.asksaveasfilename(initialdir="images",
                    title = "Save Generated Image",
                    filetypes = (("png files", "*.png"), ("all files", "*.*")))
        if filename is not None:
            self.vout_file.set(filename)
            self.out_file.xview_moveto(1)  # scrolls to end of text in Entry

    def btn_out_var_click(self):
        ''' Select an image file to generate a variation on.
        "images" is a subdirectory of the application directory '''
        filename =  filedialog.askopenfilename(initialdir="images",
                    title = "Open Image File for Variation",
                    filetypes = (("png files", "*.png"),("all files", "*.*")))
        if filename is not None:
            self.vvar_file.set(filename)
            self.var_file.xview_moveto(1)  # scrolls to end of text in Entry


    def btn_create_click(self):
        ''' Generate the Prompted Image or Image Variation '''
        # self.vchkwww      Browser CHECKBUTTON
        # self.vchkfile     File CHECKBUTTON
        # self.vspn         number of images SPINBOX
        # self.vout_file    Image file name ENTRY
        # self.vopt_size    Image File Size OPTIONMENU
        # self.vvar_file    Image file name ENTRY (input image)
        # self.prompt       Prompt TEXT

        # See if user checked one or more Output destinations
        if self.vchkwww.get() == 0 and self.vchkfile.get() == 0:
            messagebox.showerror("AimGUI", "Select Output Destination(s)")
            return

        try:
            client = OpenAI(
            api_key = os.getenv("GPTKEY")  # openai API
            )
        except Exception as e:
            messagebox.showerror("Could Not Read Key file",
                       "Did you enter your Gpt Key?")
            return

        try:
            # VARIATION
            if self.vvar_file.get() != "":  # generate variation of an image

                filein = self.vvar_file.get()
                if self.image_metrics(filein) is False:
                    return  # input image did not meet requirements

                response = client.images.create_variation(
                    # model = "dall-e-2" # default (Nov 2023) n=1-10
                    model=self.MyVmodel,
                    image=open(filein, "rb"),
                    n=int(self.vspn.get()),
                    size=self.vopt_size.get()
                )
                self.log_variation()

            else:
                # CREATE FROM PROMPT
                prompt_text = self.prompt.get("1.0", END)
                if len(prompt_text) < 4:
                    messagebox.showerror("AimGUI", "Missing Text Prompt")
                    return

                response = client.images.generate(
                    # model="dall-e-1"  # n=1
                    # model="dall-e-2" # n=1-10
                    model=self.MyCmodel,
                    prompt=prompt_text,
                    n=int(self.vspn.get()),
                    size=self.vopt_size.get()
                )
                self.log_prompt()

            if self.vchkwww.get() == 1:  # view in browser
                for x in range(0, int(self.vspn.get())):
                    webbrowser.open(response.data[x].url)

            if self.vchkfile.get() == 1:  # create image file output
                lstFile = os.path.splitext(self.vout_file.get())  # separate file.extention
                for x in range(0, int(self.vspn.get())):
                    image_url = response.data[x].url
                    image_data = requests.get(image_url).content
                    filename = lstFile[0] + str(x) + ".png"  # path/baseN.png
                    with open(filename, 'wb') as image_file:
                        image_file.write(image_data)
                messagebox.showinfo("AimGUI", "Image File(s) Created")

        except Exception as e:
            messagebox.showerror("Problems", e)


    def image_metrics(self, image_path):
        ''' validate the input image for create_variation '''
        # Get the file size
        try:
            file_size = os.path.getsize(image_path)  # in bytes
        except Exception as e:
            print("Invalid File path/name", image_path)
            sys.exit()
        # Open the image file
        image = Image.open(image_path)
        # Get the dimensions of the image
        width, height = image.size
        # Print the file size and dimensions
        print("File Size:", file_size, "bytes")
        print("Dimensions:", width, "x", height)
        if width != height or file_size > 4000000:
            messagebox.showerror("AimGUI", "Image: " + image_path + " is unacceptable")
            return False
        image.close()
        return True

    def log_prompt(self):
        with open("aimgui.log", "a") as fout:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n")
            prompt_text = self.prompt.get("1.0", END)
            outfile = self.vout_file.get()
            fout.write("-> " + current_time)
            fout.write("   " + outfile + "\n")
            fout.write("   " + prompt_text + "\n")

    def log_variation(self):
        with open("aimgui.log", "a") as fout:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n")
            outfile = self.vout_file.get()
            infile = self.vvar_file.get()
            fout.write("-> " + current_time)
            fout.write("   infile: " + infile + "\n")
            fout.write("   outfile: " + outfile + "\n")

    def btn_close_click(self):
        ''' Close the Application '''
        save_location()


# change working directory to path for this file
p = os.path.realpath(__file__)
os.chdir(os.path.dirname(p))

# get options that go into the window creation and title
config = configparser.ConfigParser()
config.read('aimgui.ini')
MyTheme = config['Main']['theme']

root = Window("AI Image Generator V1.3.3", MyTheme)

def save_location(e=None):
    ''' executes at WM_DELETE_WINDOW event - see below '''
    with open("winfi", "w") as fout:
        fout.write(root.geometry())
    root.destroy()

if os.path.isfile("winfi"):
    with open("winfi") as f:
        lcoor = f.read()
    root.geometry(lcoor.strip())
else:
    root.geometry("475x412") # WxH+left+top

root.protocol("WM_DELETE_WINDOW", save_location)  # UNCOMMENT TO SAVE GEOMETRY INFO
root.resizable(0, 0) # no resize & removes maximize button
Application(root)
root.mainloop()
