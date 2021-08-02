# Nathan John Giose
from email.mime import application
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

class POS:
    def __init__(self, window):
        self.window = window
        self.window.title("Nathan Point of Sales")
        self.window.configure(background="Black")
        self.window.geometry("1350x750+0+0")
        # self.window.resizable(False, False)

        MainFrame = Frame(self.window, background="Green")
        MainFrame.grid(padx=8, pady=5)

        ButtonFrame = Frame(MainFrame, background="blue", bd=4, width=1348, height=160, padx=4, pady=4, relief=RIDGE)
        ButtonFrame.pack(side=BOTTOM)

        DataFrame = Frame(MainFrame, background="blue", bd=4, width=800, height=300, padx=4, pady=4, relief=RIDGE)
        DataFrame.pack(side=BOTTOM)

        DataFrameLEFTCOVER = LabelFrame(DataFrame, background="blue", bd=4, width=800, height=300, padx=4, pady=4,
                                        relief=RIDGE, font=("arial",12, 'bold'))
        DataFrameLEFTCOVER.pack(side=BOTTOM)


if __name__ == "__main__":
    window = Tk()
    application = POS(window)
    window.mainloop()