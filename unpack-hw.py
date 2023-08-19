# Unpack Canvas HW for grading.
# Bart Massey 2023

import argparse, re, json, subprocess, sys, zipfile
from pathlib import Path

parser = argparse.ArgumentParser(
    prog='unpack-hw',
    description='Unpack a student homework archive for grading',
)
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

filename_re = re.compile(r"([a-z]+)_(LATE_)?([0-9]+)_.*$")
project_archive = zipfile.ZipFile(args.filename)
projects = []
for zipinfo in project_archive.infolist():
    fields = filename_re.search(zipinfo.filename)
    if fields is None:
        print(f"warning: filename not parsed: {zipinfo.filename}", file=sys.stderr)
        continue
    slug, student_id = fields[1], fields[3]
    name = student_names[student_id]

    path = sdest / slug
    had_dir = path.is_dir()
    if not had_dir:
        path.mkdir(mode=0o700)
        
    if Path(zipinfo.filename).suffix in ("ZIP", "zip"):
        zip = project_archive.open(zipinfo)
        with zipfile.ZipFile(zip) as zip:
            zip.extractall(path=path)
    else:
        project_archive.extract(zipinfo, path=path)

    if had_dir:
        continue

    grading = path / "GRADING.txt"
    with open(grading, "w") as gr:
        print(args.hw, file=gr)
        print(name, file=gr)
        print("-", file=gr)
        print(file=gr)

    info = path / ".student_id"
    with open(info, "w") as i:
        print(f"{student_id}", file=i)
