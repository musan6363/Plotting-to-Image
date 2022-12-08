'''
アノテーション位置の重心と，各点の重心からの距離について標準偏差を求める．
求めた標準偏差が大きい順にJSONに記録する．
'''

import argparse
import json
import ndjson
from os import path as osp
import numpy as np
from glob import glob
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser(description='analyze annotation of pedestrian')
    parser.add_argument('ann_root', help='ex) ./annotations')
    parser.add_argument('save_name', help='ex) ./output')
    _args = parser.parse_args()
    return _args


class JsonAnalyze:
    def __init__(self, json_path: str) -> None:
        self.json_path = json_path
        self.img_name = osp.splitext(osp.basename(json_path))[0]

    def read_records(self) -> dict:
        with open(self.json_path, 'r') as f:
            _ndj = ndjson.load(f)
            _tmp = json.dumps(_ndj)
            _data = json.loads(_tmp)

        _records = {}
        for d in _data:
            try:
                _token = d['token'] + '@' + self.img_name
                _look = d['look'].copy()
                self._check_look_over_zero(_look)
                _eyecontact = d['eyecontact']
                _difficult = d['difficult']
                _look = self._check_label(_look, _eyecontact)
                _look = self._check_label(_look, _difficult)
                _g = self._calc_barycenter(_look)  # tuple
                _dis = self._calc_distances(_g, _look)  # list
                _sum = np.sum(_dis)
            except Exception as e:
                print(e)
                print(osp.basename(self.json_path))
                print(d)
                continue

            _records[_token] = {
                'sum': _sum,
                'bbox': d['bbox'],
                'look': d['look'],  # eyecontactの計算上で0に書き換えているため，基の値を格納
                'eyecontact': _eyecontact,
                'difficult': _difficult,
                'img_name': self.img_name,
                'ped_token': d['token']
            }
        return _records

    def _check_look_over_zero(self, coords: list) -> None:
        for coord in coords:
            if coord[0] <= 0 or coord[1] <= 0:
                print(self.json_path, self.img_name)

    def _calc_barycenter(self, coords: list) -> tuple:
        _gx = (coords[0][0]+coords[1][0]+coords[2][0])/3
        _gy = (coords[0][1]+coords[1][1]+coords[2][1])/3
        return (_gx, _gy)

    def _calc_distances(self, g: list, coords: list) -> list:
        _dis = []
        for coord in coords:
            _dis.append(np.linalg.norm(np.array(g)-np.array(coord)))
        return _dis

    def _check_label(self, look: list, ann_label: list) -> list:
        for index, an in enumerate(ann_label):
            if an == 'true':
                look[index] = [0, 0]
        return look


def main():
    _args = parse_args()
    json_dict = {}

    for dataset_dir in glob(_args.ann_root+'/*'):
        _dataset = osp.basename(dataset_dir)
        for version_dir in glob(dataset_dir + '/*'):
            _version = osp.basename(version_dir)
            json_dict[version_dir] = [_dataset, _version]

    for json_dir, info in json_dict.items():
        _ann_datas = {}
        for j in tqdm(glob(json_dir + '/json/*.json')):
            ja = JsonAnalyze(j)
            _ann_datas.update(ja.read_records())

        with open(_args.save_name + '/' + info[0] + '_' + info[1] + '.json', 'w') as f:
            json.dump(_ann_datas, f, indent=2)


if __name__ == "__main__":
    main()
