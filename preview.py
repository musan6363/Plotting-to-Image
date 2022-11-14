import tkinter as tk
from tkinter import ttk

import os
import shutil
import sys
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import csv
import json
import ndjson


class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.master.geometry("2000x1500")
        self.master.title("Annotation Preview")
        self.img_width = 900
        self.img_height = 1600

        self.create_widgets()

    def create_widgets(self):
        # img frame
        self.img_frame = ttk.LabelFrame(self)
        self.img_frame.configure(text='Original Image')
        self.img_frame.grid(column=0, row=0)
        self.img_frame.grid(padx=50, pady=50)
        # Image
        self.img_area = tk.Canvas(self.img_frame)
        self.img_area.configure(width=self.img_width, height=self.img_height)
        self.img_area.grid(column=0, row=0)
        self.img_area.grid(padx=0, pady=0)

        # info frame
        self.info_frame = ttk.LabelFrame(self)
        self.info_frame.grid(column=1, row=0)
        self.info_frame.grid(padx=50, pady=50)
        # info canvas
        self.info_canvas = tk.Canvas(self.info_frame)
        self.info_canvas.configure(width=300, height=900, bg='snow')
        self.info_canvas.grid(column=0, row=0)
        self.info_canvas.grid(padx=0, pady=0)
        self.info_canvas.create_text(5, 5, text="Image token: ", font=("Ricty", 12), anchor="nw", tag="imagetoken")
        self.info_canvas.create_text(5, 230, text="Ped token: ", font=("Ricty", 12), anchor="nw", tag="pedtoken")
        self.info_canvas.create_text(5, 485, text="STDEV: ", font=("Ricty", 12), anchor="nw", tag="stdev")
        # Save Button
        self.img_save = ttk.Button(self.info_frame)
        self.img_save.configure(text='IMG Save')
        self.img_save.grid(column=0, row=1)
        self.img_save.grid(pady=0)
        self.img_save.configure(command=self.img_save)
        self.ann_export = ttk.Button(self.info_frame)
        self.ann_export.configure(text='Ann Exp')
        self.ann_export.grid(column=0, row=2)
        self.ann_export.grid(pady=0)
        self.ann_export.configure(command=self.ann_export)

        # ann frame
        self.ann_frame = ttk.LabelFrame(self)
        self.ann_frame.grid(column=0, row=1)
        self.ann_frame.grid(padx=50, pady=0)
        # ann canvas
        self.ann_canvas = tk.Canvas(self.ann_frame)
        self.ann_canvas.configure(width=1600, height=400, bg='snow')
        self.ann_canvas.grid(column=0, row=0)
        self.ann_canvas.grid(padx=0, pady=0)
        self.ann_canvas.create_text(5, 5, text="1 -> ", font=("Ricty", 24), anchor="nw", tag="ann1")
        self.ann_canvas.create_text(5, 505, text="2 -> ", font=("Ricty", 24), anchor="nw", tag="ann2")
        self.ann_canvas.create_text(5, 1005, text="3 -> ", font=("Ricty", 24), anchor="nw", tag="ann3")
        # next button
        self.next_button = ttk.Button(self.ann_frame)
        self.next_button.configure(text='Next')
        self.next_button.grid(column=1, row=0)
        self.next_button.grid(pady=0)
        self.next_button.configure(command=self.next_button_ex)

    # Event Call Back

    def next_button_ex(self):
        self.ann_token = next(self.token_list)
        self.ann_token_box.delete(0, tk.END)
        self.ann_token_box.insert(0, self.ann_token)
        self.drawImage()


def read_json(j_file):
    with open(j_file, 'r') as f:
        _records = json.load(f)
    _records = sorted(_records.items(), key=lambda r: r[1]['std'], reverse=True)
    return _records


def main():
    root = tk.Tk()
    app = Application(master=root)  # Inherit
    app.mainloop()


if __name__ == "__main__":
    # main()
    rec = read_json('./ann_records/nuimages_ped_1017_v1.0-train.json')
    for r in rec:
        print(r[1]['std'])
