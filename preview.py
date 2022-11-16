import tkinter as tk
from tkinter import ttk

import argparse
import os
import shutil
from tkinter import *
from PIL import Image, ImageTk
import json
import ndjson
import matplotlib.patches as patches
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(description='analyze annotation of pedestrian')
    parser.add_argument('ann_json', help='ex) ann_records/nuimages_ped_1017_v1.0-train.json')
    parser.add_argument('img_root', help='ex) img_ped/nuimages_ped/v1.0-train/img')
    parser.add_argument('save_dir', help='ex) ./output')
    _args = parser.parse_args()
    return _args


class Cell:
    def __init__(self, value):
        self.token = value[0]
        self.value = value[1]
        self.pos = 0
        self.next = None
        self.prev = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.len = 0

    def insert(self, value):
        new = Cell(value)
        self.tail = new
        self.len += 1
        new.pos = self.len
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
    def __init__(self, master, ann_json: str, img_root: str, save_dir: str):
        super().__init__(master)
        self.pack()

        self.master.geometry("2000x1500")
        self.master.title(os.path.basename(ann_json))
        self.img_width = 1600
        self.img_height = 900
        self.img_x_shift = 100
        self.img_y_shift = 100

        self.save_dir = save_dir
        self.create_save_dir()
        self.exported = []

        _tmp_records = self.read_json(ann_json)
        self.records = DoublyLinkedList()
        for _tmp_record in _tmp_records:
            self.records.insert(_tmp_record)

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
        self.img_save.grid(padx=20)
        self.img_save.configure(command=self.img_save_ex)
        self.ann_good_export = ttk.Button(self.export_frame)
        self.ann_good_export.configure(text='Ann Exp(Good)')
        self.ann_good_export.grid(column=2, row=0)
        self.ann_good_export.grid(pady=0)
        self.ann_good_export.configure(command=self.ann_good_export_ex)
        self.ann_bad_export = ttk.Button(self.export_frame)
        self.ann_bad_export.configure(text='Ann Exp(Bad)')
        self.ann_bad_export.grid(column=1, row=0)
        self.ann_bad_export.grid(pady=0)
        self.ann_bad_export.configure(command=self.ann_bad_export_ex)

        # ann frame
        self.ann_frame = ttk.LabelFrame(self)
        self.ann_frame.grid(column=0, row=1)
        self.ann_frame.grid(padx=50, pady=0)
        # ann canvas
        self.ann_canvas = tk.Canvas(self.ann_frame)
        self.ann_canvas.configure(width=self.img_width, height=100, bg='snow')
        self.ann_canvas.grid(column=0, row=0)
        self.ann_canvas.grid(padx=0, pady=0)
        self.ann_canvas.create_text(5, 5, text="1 -> ", font=("Ricty", 24), anchor="nw", tag="ann1")
        self.ann_canvas.create_text(505, 5, text="2 -> ", font=("Ricty", 24), anchor="nw", tag="ann2")
        self.ann_canvas.create_text(1005, 5, text="3 -> ", font=("Ricty", 24), anchor="nw", tag="ann3")
        self.ann_canvas.create_text(1400, 5, text="[x/x]", font=("Ricty", 24), anchor="nw", tag="progress")
        self.ann_canvas.create_text(5, 50, text="Image token: ", font=("Ricty", 20), anchor="nw", tag="imagetoken")
        self.ann_canvas.create_text(505, 50, text="Ped token: ", font=("Ricty", 20), anchor="nw", tag="pedtoken")
        self.ann_canvas.create_text(1005, 50, text="STDEV: ", font=("Ricty", 20), anchor="nw", tag="stdev")
        # info frame
        self.control_frame = ttk.LabelFrame(self)
        self.control_frame.grid(column=0, row=2)
        self.control_frame.grid(padx=50, pady=10)
        self.pos_input = ttk.Entry(self.control_frame, width=50)
        self.pos_input.grid(column=0, row=0)
        # load button
        self.load_button = ttk.Button(self.control_frame)
        self.load_button.configure(text='Load')
        self.load_button.grid(column=1, row=0)
        self.load_button.grid(padx=30)
        self.load_button.configure(command=self.load_button_ex)
        # next button
        self.next_button = ttk.Button(self.control_frame)
        self.next_button.configure(text='Next')
        self.next_button.grid(column=3, row=0)
        self.next_button.grid(pady=0)
        self.next_button.configure(command=self.next_button_ex)
        # preview button
        self.pre_button = ttk.Button(self.control_frame)
        self.pre_button.configure(text='Pre')
        self.pre_button.grid(column=2, row=0)
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

    def load_button_ex(self):
        _input = self.pos_input.get()
        if self.is_int(_input):
            self.search_record_by_pos(_input)
        else:
            self.search_record_by_pedtoken(_input)

    def is_int(self, input) -> bool:
        try:
            int(input)
        except ValueError:
            return False
        return True

    def search_record_by_pos(self, pos):
        pos = int(pos)
        if pos > self.records.len:
            raise IndexError("Out of records!")
        while self.record.pos != pos:
            self.record = self.record.next
        self.set_record()

    def search_record_by_pedtoken(self, token):
        _search_start = self.record
        while self.record.value['ped_token'] != token:
            self.record = self.record.next
            if self.record == _search_start:
                raise IndexError("ped token {"+token+"} is not found.")
        self.set_record()

    def next_button_ex(self):
        if self.record == self.records.tail and self.record.next == self.records.head:
            print("END OF RECORD")
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
        self.ann_canvas.delete("progress")
        self.ann_canvas.create_text(5, 5, text="1 -> "+str(_ann[0]), font=("Ricty", 24), anchor="nw", tag="ann1")
        self.ann_canvas.create_text(505, 5, text="2 -> "+str(_ann[1]), font=("Ricty", 24), anchor="nw", tag="ann2")
        self.ann_canvas.create_text(1005, 5, text="3 -> "+str(_ann[2]), font=("Ricty", 24), anchor="nw", tag="ann3")
        self.ann_canvas.create_text(1400, 5, text='['+str(self.record.pos)+'/'+str(self.records.len)+']', font=("Ricty", 24), anchor="nw", tag="progress")

    def drawImage(self):
        _img_path = self.img_root + '/' + self.imagetoken + '.jpg'
        self.render_check_image(_img_path, self.record.value['bbox'], self.ann_coords, self.ann_eyecontacts, self.ann_difficult)
        self._dst = ImageTk.PhotoImage(file="./.tmp.png")
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
            ax.scatter(x, y, c=c, s=300, alpha=0.3)

        ax.add_patch(patches.Rectangle(
            xy=(ped_bbox[0]+self.img_x_shift, ped_bbox[1]+self.img_y_shift),
            width=bbox_wid,
            height=bbox_hei,
            edgecolor='yellow',
            fill=False
        ))

        im_new = self.add_margin(im, self.img_y_shift, self.img_x_shift, self.img_y_shift, self.img_x_shift, 'black')
        ax.imshow(im_new)
        fig.subplots_adjust(left=0, right=1, bottom=0.05, top=0.95)
        fig.savefig('./.tmp.png')

    def create_save_dir(self):
        os.makedirs(self.save_dir, exist_ok=True)

    def img_save_ex(self):
        shutil.copy2('./.tmp.png', self.save_dir+'/'+self.record.token+'.png')
        print("Done copy as "+self.save_dir+'/'+self.record.token+'.png')

    def ann_good_export_ex(self):
        _dst = {}
        if self.record.token in self.exported:
            print("This record had already exported.")
            return
        self.exported.append(self.record.token)
        _dst[self.record.token] = self.record.value
        print(_dst)
        with open(self.save_dir+'/checked_ann_good.json', mode='a') as f:
            writer = ndjson.writer(f)
            writer.writerow(_dst)

    def ann_bad_export_ex(self):
        _dst = {}
        if self.record.token in self.exported:
            print("This record had already exported.")
            return
        self.exported.append(self.record.token)
        _dst[self.record.token] = self.record.value
        print(_dst)
        with open(self.save_dir+'/checked_ann_bad.json', mode='a') as f:
            writer = ndjson.writer(f)
            writer.writerow(_dst)


def main():
    _args = parse_args()
    root = tk.Tk()
    app = Application(master=root, ann_json=_args.ann_json, img_root=_args.img_root, save_dir=_args.save_dir)  # Inherit
    app.mainloop()


if __name__ == "__main__":
    main()
    os.remove('./.tmp.png')
