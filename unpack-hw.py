# Unpack Canvas HW for grading.
# Bart Massey 2023

import argparse, json, re, subprocess, sys, zipfile
from collections import defaultdict
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

def read_link(arch, member):
    linky = str(arch.read(member))
    linkinfo = link_re.search(linky)
    if not linkinfo:
        print(f"warning: link not parsed: {member.filename}", file=sys.stderr)
        return None
    return linkinfo[0]

sdest = mkfdir("staged")
gdest = mkfdir("graded")

student_names = dict()
with open("students.json", "r") as s:
    s = json.load(s)
    for record in s:
        student_id = str(record["id"])
        student_names[student_id] = record["short_name"]

filename_re = re.compile(r"([a-z]+)_(LATE_)?([0-9]+)_([0-9]+|link).*$")
link_re = re.compile(r'href="(https://git[^"/]*/[^"/]+/[^"/]+)(/[^"]*)?"')
project_archive = zipfile.ZipFile(args.filename)

groups = defaultdict(lambda: set())
for zipinfo in project_archive.infolist():
    fields = filename_re.search(zipinfo.filename)
    if fields is None:
        print(f"warning: filename not parsed: {zipinfo.filename}", file=sys.stderr)
        continue
    slug, student_id, tag = fields[1], fields[3], fields[4]
    if tag == "link":
        tag = read_link(project_archive, zipinfo)
        if tag is None:
            continue

    groups[tag].add((slug, student_id))

groups = set(frozenset(g) for g in groups.values())
students = set(s for g in groups for s in g)
for s in students:
    assert len(set(g for g in groups if s in g)) == 1

paths = dict()
for g in groups:
    slugs = sorted(list(m[0] for m in g))
    slug = '-'.join(slugs)
    path = sdest / slug
    for s in slugs:
        paths[s] = path

    path.mkdir(mode=0o700, exist_ok=True)

    ids = ''.join(sorted(list(f"{m[0]}={m[1]}\n" for m in g)))
    with open(path / ".ids", "w") as f:
        f.write(ids)

    names = ', '.join(sorted(list(student_names[m[1]] for m in g)))

    grading = path / "GRADING.txt"
    with open(grading, "w") as gr:
        print(args.hw, file=gr)
        print(names, file=gr)
        print("-", file=gr)
        print(file=gr)

seen = set()
for zipinfo in project_archive.infolist():
    fields = filename_re.search(zipinfo.filename)
    if fields is None:
        continue
    slug, student_id, tag = fields[1], fields[3], fields[4]
    link = tag == "link"
    if link:
        tag = read_link(project_archive, zipinfo)
        if tag is None:
            continue
    if tag in seen:
        continue
    seen.add(tag)

    path = paths[slug]

    if Path(zipinfo.filename).suffix in (".ZIP", ".zip"):
        zip = project_archive.open(zipinfo)
        with zipfile.ZipFile(zip) as zip:
            zip.extractall(path=path)
    else:
        project_archive.extract(zipinfo, path=path)
