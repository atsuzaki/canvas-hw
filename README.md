# canvas-hw: tools for offline homework grading in Canvas LMS
Bart Massey 2023

These are janky half-finished tools for downloading an
assignment from Canvas that is presumed to be one ZIP
file per submission, unpacking that locally, then allowing
local grading. At the end, the grade results are uploaded to 
Canvas.

Thus is SpeedGrader avoided.

## Instructions

### One-Time Setup

* https://canvas.pdx.edu/profile/settings to generate Canvas
  API token
* Store Canvas API token in ~/.canvasgrader
* Clone `canvasgrader` fork
  http://github.com/BartMassey-upstream/canvasgrader (for
  now) and run `pip install .`


### Download

* Go to `https://canvas.pdx.edu/courses/<course-id>/students` and
  copy-paste the JSON found there into `students.json`
  (gross, will fix later)

* Download a zipball of the HW from Canvas.

* Run `unpack-hw.py --hw <assignment name> <zipball>`

### Grading

* For each directory in `staged/`:

  * Edit `GRADING.txt`. Make sure to replace the `-` with a
    score.
  * Move directory from `staged/` to `graded/`

### Upload

* Find course ID in course URL
* Find assignment ID in assignment URL
* Run `upload-grades.py <courseid> <asgid>`

## Acknowledgments

Thanks to the authors of the Python `canvasgrader` package
for making this all possible.

## License

This work is licensed under the "MIT License". Please see the file
`LICENSE.txt` in this distribution for license terms.
