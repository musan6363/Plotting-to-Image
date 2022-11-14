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
import matplotlib.patches as patches
import matplotlib.pyplot as plt


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


def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def render_check_image(image_path: str, ped_bbox: list, ann_coords: list, ann_eyecontact: list, ann_difficult: list):
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(1, 1, 1)

    bbox_wid = ped_bbox[2] - ped_bbox[0]
    bbox_hei = ped_bbox[3] - ped_bbox[1]

    for i in range(len(ann_coords)):
        if ann_eyecontact[i] == 'true' or ann_difficult[i] == 'true':
            c = 'gray'
        else:
            c = 'red'
        x = ann_coords[i][0]
        y = ann_coords[i][1]
        ax.scatter(x, y, c=c, s=300)

    ax.add_patch(patches.Rectangle(
        xy=(ped_bbox[0], ped_bbox[1]),
        width=bbox_wid,
        height=bbox_hei,
        edgecolor='yellow',
        fill=False
    ))

    im = Image.open(image_path)
    im_new = add_margin(im, 0, 200, 200, 0, 'black')
    ax.imshow(im_new)
    return fig


def main():
    root = tk.Tk()
    app = Application(master=root)  # Inherit
    app.mainloop()


if __name__ == "__main__":
    # main()
    dst = render_check_image('./img_ped/nuimages_ped/v1.0-train/img/a0c0b6717bb542b9b13727ff05253501.jpg',
                             [49, 313, 140, 550], [[1731.9, 829.1], [1719.7, 531.3], [749.2, 526.1800000000001]], ['true', 'false', 'false'])
    dst.savefig('./test.png')
