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


class Cell:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None

    def insert(self, value):
        new = Cell(value)
        tmp = self.head
        if not tmp:
            new.next = new
            new.prev = new
            self.head = new
            return
        while not tmp == self.head:
            tmp = tmp.next
        tmp.prev.next = new
        new.prev = tmp.prev
        new.next = tmp
        tmp.prev = new


class Application(tk.Frame):
    def __init__(self, master, ann_json: str, img_root: str):
        super().__init__(master)
        self.pack()

        self.master.geometry("2000x1500")
        self.master.title("Annotation Preview")
        self.img_width = 1600
        self.img_height = 900

        _tmp_records = self.read_json(ann_json)
        self.records = DoublyLinkedList()
        for _tmp_record in _tmp_records:
            self.records.insert(_tmp_record[1])

        self.img_root = img_root
        self.create_widgets()
        self.record = self.records.head
        self.set_record()

    def create_widgets(self):
        # img frame
        self.img_frame = ttk.LabelFrame(self)
        self.img_frame.configure(text='Preview Image')
        self.img_frame.grid(column=0, row=0)
        self.img_frame.grid(padx=50, pady=50)
        # Image
        self.img_area = tk.Canvas(self.img_frame)
        self.img_area.configure(width=self.img_width, height=self.img_height)
        self.img_area.grid(column=0, row=0)
        self.img_area.grid(padx=0, pady=0)

        # export frame
        self.export_frame = ttk.LabelFrame(self)
        self.export_frame.grid(column=0, row=3)
        self.export_frame.grid(padx=50, pady=10)
        # Save Button
        self.img_save = ttk.Button(self.export_frame)
        self.img_save.configure(text='IMG Save')
        self.img_save.grid(column=0, row=0)
        self.img_save.grid(pady=0)
        self.img_save.configure(command=self.img_save_ex)
        self.ann_export = ttk.Button(self.export_frame)
        self.ann_export.configure(text='Ann Exp')
        self.ann_export.grid(column=1, row=0)
        self.ann_export.grid(pady=0)
        self.ann_export.configure(command=self.ann_export_ex)

        # ann frame
        self.ann_frame = ttk.LabelFrame(self)
        self.ann_frame.grid(column=0, row=1)
        self.ann_frame.grid(padx=50, pady=0)
        # ann canvas
        self.ann_canvas = tk.Canvas(self.ann_frame)
        self.ann_canvas.configure(width=1600, height=100, bg='snow')
        self.ann_canvas.grid(column=0, row=0)
        self.ann_canvas.grid(padx=0, pady=0)
        self.ann_canvas.create_text(5, 5, text="1 -> ", font=("Ricty", 24), anchor="nw", tag="ann1")
        self.ann_canvas.create_text(505, 5, text="2 -> ", font=("Ricty", 24), anchor="nw", tag="ann2")
        self.ann_canvas.create_text(1005, 5, text="3 -> ", font=("Ricty", 24), anchor="nw", tag="ann3")
        self.ann_canvas.create_text(5, 50, text="Image token: ", font=("Ricty", 20), anchor="nw", tag="imagetoken")
        self.ann_canvas.create_text(505, 50, text="Ped token: ", font=("Ricty", 20), anchor="nw", tag="pedtoken")
        self.ann_canvas.create_text(1005, 50, text="STDEV: ", font=("Ricty", 20), anchor="nw", tag="stdev")
        # info frame
        self.control_frame = ttk.LabelFrame(self)
        self.control_frame.grid(column=0, row=2)
        self.control_frame.grid(padx=50, pady=10)
        # next button
        self.next_button = ttk.Button(self.control_frame)
        self.next_button.configure(text='Next')
        self.next_button.grid(column=1, row=0)
        self.next_button.grid(pady=0)
        self.next_button.configure(command=self.next_button_ex)
        # preview button
        self.pre_button = ttk.Button(self.control_frame)
        self.pre_button.configure(text='Pre')
        self.pre_button.grid(column=0, row=0)
        self.pre_button.grid(pady=0)
        self.pre_button.configure(command=self.pre_button_ex)

    # Event Call Back
    def set_record(self):
        self.imagetoken = self.record.value['img_name']
        self.pedtoken = self.record.value['ped_token']
        self.stdev = self.record.value['std']
        self.ann_coords = self.record.value['look']
        self.ann_eyecontacts = self.record.value['eyecontact']
        self.ann_difficult = self.record.value['difficult']
        self.update_info_area()
        self.update_ann_area()
        self.drawImage()

    def next_button_ex(self):
        self.record = self.record.next
        self.set_record()

    def pre_button_ex(self):
        self.record = self.record.prev
        self.set_record()

    def update_info_area(self):
        self.ann_canvas.delete("imagetoken")
        self.ann_canvas.delete("pedtoken")
        self.ann_canvas.delete("stdev")
        self.ann_canvas.create_text(5, 50, text="Image token: "+self.imagetoken, font=("Ricty", 20), anchor="nw", tag="imagetoken")
        self.ann_canvas.create_text(505, 50, text="Ped token: "+self.pedtoken, font=("Ricty", 20), anchor="nw", tag="pedtoken")
        self.ann_canvas.create_text(1005, 50, text="STDEV: "+str(self.stdev), font=("Ricty", 20), anchor="nw", tag="stdev")

    def update_ann_area(self):
        _ann = [None, None, None]
        for index, coord in enumerate(self.ann_coords):
            if self.ann_eyecontacts[index] == 'true':
                _ann[index] = "EC"
            elif self.ann_difficult[index] == 'true':
                _ann[index] = "DF"
            else:
                _ann[index] = coord

        self.ann_canvas.delete("ann1")
        self.ann_canvas.delete("ann2")
        self.ann_canvas.delete("ann3")
        self.ann_canvas.create_text(5, 5, text="1 -> "+str(_ann[0]), font=("Ricty", 24), anchor="nw", tag="ann1")
        self.ann_canvas.create_text(505, 5, text="2 -> "+str(_ann[1]), font=("Ricty", 24), anchor="nw", tag="ann2")
        self.ann_canvas.create_text(1005, 5, text="3 -> "+str(_ann[2]), font=("Ricty", 24), anchor="nw", tag="ann3")

    def drawImage(self):
        _img_path = self.img_root + '/' + self.imagetoken + '.jpg'
        self.render_check_image(_img_path, self.record.value['bbox'], self.ann_coords, self.ann_eyecontacts, self.ann_difficult)
        self._dst = ImageTk.PhotoImage(file="./tmp.png")
        self.img_area.create_image(self.img_width/2, self.img_height/2, image=self._dst)

    def read_json(self, j_file):
        with open(j_file, 'r') as f:
            _records = json.load(f)
        _records = sorted(_records.items(), key=lambda r: r[1]['std'], reverse=True)
        return _records

    def add_margin(self, pil_img, top, right, bottom, left, color):
        width, height = pil_img.size
        new_width = width + right + left
        new_height = height + top + bottom
        result = Image.new(pil_img.mode, (new_width, new_height), color)
        result.paste(pil_img, (left, top))
        return result

    def render_check_image(self, image_path: str, ped_bbox: list, ann_coords: list, ann_eyecontact: list, ann_difficult: list):
        im = Image.open(image_path)
        fig = plt.figure(figsize=(im.size[0]/100, im.size[1]/100))
        ax = fig.add_subplot(1, 1, 1)

        bbox_wid = ped_bbox[2] - ped_bbox[0]
        bbox_hei = ped_bbox[3] - ped_bbox[1]

        for i in range(len(ann_coords)):
            if ann_eyecontact[i] == 'true':
                c = 'plum'
            elif ann_difficult[i] == 'true':
                c = 'purple'
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

        im_new = self.add_margin(im, 0, 200, 200, 0, 'black')
        ax.imshow(im_new)
        fig.subplots_adjust(left=0, right=1, bottom=0.05, top=0.95)
        fig.savefig('./tmp.png')

    def img_save_ex(self):
        pass

    def ann_export_ex(self):
        pass


def main():
    root = tk.Tk()
    app = Application(master=root, ann_json='ann_records/nuimages_ped_1017_v1.0-train.json', img_root='img_ped/nuimages_ped/v1.0-train/img')  # Inherit
    app.mainloop()


if __name__ == "__main__":
    main()
