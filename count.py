from glob import glob
import json
import ndjson
from os import path as osp

ann_records = glob('./annotation-check-result/ann_records/*.json')
cnt_ann = {}

for ann_record in ann_records:
    _tmp = osp.splitext(osp.basename(ann_record))[0].split('_')
    _dataset = _tmp[0]
    _version = _tmp[1]
    with open(ann_record, 'r') as f:
        _data = json.load(f)
    print(_dataset+'\t'+_version+'\t'+str(len(_data)))
