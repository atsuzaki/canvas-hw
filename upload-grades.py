import argparse, csv
from pathlib import Path
import canvasgrader

parser = argparse.ArgumentParser(
    prog='upload-grades',
    description='Upload project grades to Canvas',
)
parser.add_argument('--test', action='store_true')
parser.add_argument('--debug', action='store_true')
parser.add_argument('--baseurl', default="canvas.pdx.edu")
parser.add_argument('courseid', nargs='?')
parser.add_argument('asgid', nargs='?')
args = parser.parse_args()

grades = dict()
comments = dict()
projects = list(Path("graded").iterdir())
for project in projects:
    fids = project / ".ids"
    with fids.open() as f:
        sids = [line.strip().split("=")[1] for line in f.read().splitlines()]

    fgrading = project / "GRADING.txt"
    with fgrading.open() as f:
        grading = f.read()
    sgrading = grading.splitlines()
    title = sgrading[0]
    name = sgrading[1]
    score = int(sgrading[2])
    assert sgrading[3] == "", f"bad GRADING: {fgrading}"
    body = "\n".join(sgrading[4:]) + "\n"
    for s in sids:
        grades[s] = score
        comments[s] = body

assert args.courseid and args.asgid, "need course and assignment ids"

grader = canvasgrader.CanvasGrader(
    args.baseurl,
    args.courseid,
)

if args.debug:
    for sid in grades.keys():
        print(sid, grades[sid], comments[sid].strip().replace('\n', '')[:20])
    exit(0)

if args.test:
    sid = list(grades.keys())[0]
    grades = {sid : grades[sid]}
    comments = {sid : comments[sid]}
    grader.grade_assignment(
        args.asgid,
        grades=grades,
        comments=comments,
    )
    exit(0)

grader.grade_assignment(
    args.asgid,
    grades=grades,
    comments=comments,
)
