import json
import ndjson

class NoUseDict:
    def __init__(self) -> None:
        self.d = {}

    def add_frame(self, dataset_name, version_name) -> None:
        try:
            _ = self.d[dataset_name]
        except KeyError:
            self.d[dataset_name] = {}
        self.d[dataset_name][version_name] = {}

    def add_ped(self, dataset_name, version_name, img_token, ped_token) -> None:
        try:
            _ = self.d[dataset_name][version_name][img_token]
        except KeyError:
            self.d[dataset_name][version_name][img_token] = []
        self.d[dataset_name][version_name][img_token].append(ped_token)

    def show(self) -> None:
        print("{")
        for dataset_name, version_dict in self.d.items():
            print("  "+dataset_name+" : {", end="\n    ")
            for version_name, img_dict in version_dict.items():
                print(version_name+" : {", end="\n     ")
                for img_name, ped_list in img_dict.items():
                    print(" "+img_name+" : {", end="\n       ")
                    for ped in ped_list:
                        print(ped+",", end=' ')
                    print("\n      },", end="")
                print("\n  },", end="\n  ")
            print("  },")
        print("}")

def copy_no_use_dict(original: NoUseDict) -> NoUseDict:
    new_d = NoUseDict()
    for dataset_name, version_dict in original.d.items():
        for version_name in version_dict.keys():
            new_d.add_frame(dataset_name, version_name)
    return new_d


def load_json(file_name: str) -> list:
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data

def load_ndjson(file_name: str) -> list:
    with open(file_name, 'r') as f:
        ndj = ndjson.load(f)
        tmp = json.dumps(ndj)
        data = json.loads(tmp)
    return data

def get_file_name(path: str) -> tuple:
    dataset_name = path.split('\\')[0]
    version_name = path.split('\\')[1]
    # パスから拡張子を除いたファイル名を取得する
    file_name = path.split('\\')[-1].split('.')[0]
    return dataset_name, version_name, file_name

def get_dataset_version(path: str) -> tuple:
    dataset_name = path.split('/')[-3]
    version_name = path.split('/')[-2]
    return dataset_name, version_name

def analyze_gw_records(gw: NoUseDict, file_name: str) -> list:
    data = load_ndjson(file_name)
    for record in data:
        dataset, version, img_token = get_file_name(record['json_path'])
        ped_token = record['Token']
        gw.add_ped(dataset, version, img_token, ped_token)
    return gw

def analyze_us_records(nud, file_name) -> NoUseDict:
    data = load_json(file_name)
    dataset, version = get_dataset_version(file_name)
    nud.add_frame(dataset, version)
    for record in data:
        img_token = record['img_token']
        ped_token = record['ped_token']
        nud.add_ped(dataset, version, img_token, ped_token)
    return nud

us = NoUseDict()
us = analyze_us_records(us, "reannotate/nuimages_ped_1017/v1.0-train/notuse.json")
us = analyze_us_records(us, "reannotate/nuimages_ped_1017/v1.0-val/notuse.json")
us = analyze_us_records(us, "reannotate/waymo-ped/train/notuse.json")
us = analyze_us_records(us, "reannotate/waymo-ped/validation/notuse.json")
us.show()

gw = NoUseDict()
gw = copy_no_use_dict(us)
gw.add_frame('nuscenes_ped', 'v1.0-trainval')
gw = analyze_gw_records(gw, "ann/no_annotation_list.json")
gw.show()