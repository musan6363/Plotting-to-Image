import json
import ndjson
from glob import glob
import os
from os import path as osp

ORI_ANN_DIR = "ann"
NOT_USE_ANN_DIR = "not-use"
OUTPUT_DIR = "ann_export"

def read_ndjson(json_path: str) -> list:
    try:
        with open(json_path, 'r') as f:
            _ndj = ndjson.load(f)
            _tmp = json.dumps(_ndj)
            _data = json.loads(_tmp)
        return _data
    except FileNotFoundError as e:
        print("FILE NOT FOUND", e)
        return -1

def read_json(json_path: str) -> list:
    with open(json_path, 'r') as f:
        _data = json.load(f)
    return _data

def export_json(json_path: str, dst: dict):
    os.makedirs(osp.dirname(json_path), exist_ok=True)
    with open(json_path, mode='w') as f:
        json.dump(dst, f, indent=2)

def reject_notuse():
    not_use_dict = {}
    for dataset_path in glob(f"{NOT_USE_ANN_DIR}/*"):
        dataset = osp.basename(dataset_path)
        not_use_dict[dataset] = {}
        for version_path in glob(f"{dataset_path}/*"):
            version = osp.basename(version_path)
            record_path = version_path + "/checked_ann_not_use.json"
            not_use = read_ndjson(record_path)
            if not_use == -1:
                continue
            not_use_dict[dataset][version] = []
            for rec in not_use:
                not_use_dict[dataset][version].append(list(rec.keys())[0])

    for dataset_path in glob(f"{ORI_ANN_DIR}/*"):
        dataset = osp.basename(dataset_path)
        for version_path in glob(f"{dataset_path}/*"):
            version = osp.basename(version_path)
            for record_path in glob(f"{version_path}/json/*.json"):
                record = osp.splitext(osp.basename(record_path))[0]
                ori_ann = read_ndjson(record_path)
                output_dict = {}
                for rec in ori_ann:
                    token = rec['token'] + "@" + record
                    try:
                        if token in not_use_dict[dataset][version]:
                            continue
                        output_dict[rec['token']] = rec
                        output_dict[rec['token']].pop('token')
                    except KeyError as e:
                        print("NO DICT ", e)
                        output_dict[rec['token']] = rec
                        output_dict[rec['token']].pop('token')
                if output_dict:
                    export_json(f"{OUTPUT_DIR}/{dataset}/{version}/{record}.json", output_dict)
    
    return not_use_dict

def check(nud: dict):
    cnt_reject = 0
    for dataset_path in glob(f"{NOT_USE_ANN_DIR}/*"):
        for version_path in glob(f"{dataset_path}/*"):
            record_path = version_path + "/checked_ann_not_use.json"
            not_use = read_ndjson(record_path)
            if not_use == -1:
                continue
            for _ in not_use:
                cnt_reject += 1
    cnt_original = 0
    cnt_pop_nud = 0
    for dataset_path in glob(f"{ORI_ANN_DIR}/*"):
        dataset = osp.basename(dataset_path)
        for version_path in glob(f"{dataset_path}/*"):
            version = osp.basename(version_path)
            for record_path in glob(f"{version_path}/json/*.json"):
                record = osp.splitext(osp.basename(record_path))[0]
                ori_ann = read_ndjson(record_path)
                for rec in ori_ann:
                    cnt_original += 1
                    token = rec['token'] + "@" + record
                    try:
                        if token in nud[dataset][version]:
                            cnt_pop_nud += 1
                    except KeyError as e:
                        print("NO DICT ", e)
    print(cnt_original, cnt_reject, cnt_original-cnt_reject)
    print(cnt_original-cnt_pop_nud)

    cnt_rejected = 0
    for dataset_path in glob(f"{OUTPUT_DIR}/*"):
        for version_path in glob(f"{dataset_path}/*"):
            for record_path in glob(f"{version_path}/*.json"):
                rej_ann = read_json(record_path)
                for _ in rej_ann:
                    cnt_rejected += 1
    print(cnt_rejected)

if __name__ == "__main__":
    nud = reject_notuse()
    check(nud)