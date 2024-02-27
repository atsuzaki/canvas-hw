# Unpack Canvas HW for grading.
# Bart Massey 2023

import argparse, json, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path

parser = argparse.ArgumentParser(
    prog='unpack-hw',
    description='Unpack a student homework archive for grading',
)
parser.add_argument("--rust", action="store_true")
parser.add_argument("--hw", required=True)
parser.add_argument("filename")
args = parser.parse_args()

def mkfdir(root):
    fdest = Path(root)
    if fdest.is_dir():
        print(f"directory {root} exists", file=sys.stderr)
        exit(1)
    fdest.mkdir(mode=0o700)
    return fdest

sdest = mkfdir("staged")
gdest = mkfdir("graded")

student_names = dict()
with open("students.json", "r") as s:
    s = json.load(s)
    for record in s:
        student_id = str(record["id"])
        student_names[student_id] = record["short_name"]


def prepare_cargo_project(sub_dir):
    # pull up cargo project to be top-level
    if not (sub_dir / Path("Cargo.toml")).is_file():
        if not pull_cargo_up(sub_dir):
            return

    # move top-level main.rs to src
    main_file_path = Path("main.rs")
    main_path = sub_dir / main_file_path
    if main_path.is_file():
        src_path = sub_dir / Path("src")
        if not src_path.is_dir():
            src_path.mkdir()
        main_path.rename(sub_dir / Path("src") / main_file_path)

# https://stackoverflow.com/a/1724723
def find_cargo(gpath):
    result = []
    for root, _, files in os.walk(gpath):
        if "Cargo.toml" in files:
            result.append(Path(root))
    return result


def pull_cargo_up(gpath):
    actuals = find_cargo(gpath)

    if len(actuals) != 1:
        print(f"{gpath}: cannot pull up ({actuals})", file=sys.stderr)
        return False

    actual = actuals[0]
    for obj in actual.iterdir():
        obj.rename(gpath / obj.name)

    deleteme = Path(".").joinpath(*actual.parts[:3])
    for _, _, files in os.walk(deleteme):
        if len(files) > 0:
            print(f"{gpath}: warning: files remaining", file=sys.stderr)
            return True
    shutil.rmtree(deleteme)

    return True

filename_re = re.compile(r"([a-z]+)_(LATE_)?([0-9]+)_([0-9]+).*$")
project_archive = zipfile.ZipFile(args.filename)
projects = []
for zipinfo in project_archive.infolist():
    fields = filename_re.search(zipinfo.filename)
    if fields is None:
        print(f"warning: filename not parsed: {zipinfo.filename}", file=sys.stderr)
        continue
    slug, student_id, asg_id = fields[1], fields[3], fields[4]
    name = student_names[student_id]

    path = mkfdir(sdest / slug)

    zip = project_archive.open(zipinfo)
    with zipfile.ZipFile(zip) as zip:
        zip.extractall(path=path)
    if args.rust:
        prepare_cargo_project(path)

    grading = path / "GRADING.txt"
    with open(grading, "w") as gr:
        print(args.hw, file=gr)
        print(name, file=gr)
        print("-", file=gr)
        print(file=gr)

    info = path / ".canvas_info"
    with open(info, "w") as i:
        print(f"{student_id},{asg_id}", file=i)
