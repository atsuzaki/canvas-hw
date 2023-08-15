## One-Time Setup

* https://canvas.pdx.edu/profile/settings to generate Canvas
  API token
* Store Canvas API token in ~/.canvastoken
* Clone `canvasgrader` fork
  http://github.com/BartMassey-upstream/canvasgrader (for
  now) and run `pip install .`


## Download

* Go to https://canvas.pdx.edu/<course-id>/students and
  copy-paste the JSON found there into `students.json`
  (gross, will fix later)

* Download a zipball of the HW from Canvas.

* Run `unpack-hw.py --hw <assignment name> <zipball>`

## Grading

* For each directory in `staged/`:

  * Edit `GRADING.txt`. Make sure to replace the `-` with a
    score.
  * Move directory from `staged/` to `graded/`

## Upload

* Find course ID in course URL
* Find assignment ID in assignment URL
* Run `upload-grades.py <courseid> <asgid>`
