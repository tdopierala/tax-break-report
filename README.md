# Tax break report generator

### Tax Break Script v1.6 (tax-report.py)

## Usage:

```
python tax-report.py -s YYYY-MM-DD -e YYYY-MM-DD -a USERNAME -d PROJECT_DIR -o OUTPUT_DIR -f -v
```

```
Options:
  -s START, --start=START       Start date. DEFAULT: First day of the current month.
  -e END, --end=END             End date. DEFAULT: Today.
  -a AUTHOR, --author=AUTHOR    Commit author's git username. DEFAULT: user.name from .gitconfig.
  -d DIR, --dir=DIR             Project directory (relative path). DEFAULT: DEFAULT_PROJECT_DIRECTORY global variable's value.
  -o OUT, --out=OUT             Output directory. DEFAULT: Today.
  -c COMMIT, --commit=COMMIT    SHA of a specific commit to be saved. DEFAULT: None.
  -b BRANCH, --branch=BRANCH    Name of the branch. DEFAULT: None (all branches are taken into account).
  -f, --full                    Save full paths to files. DEFAULT: False.
  -v, --verbose                 Print additional information.
  --debug                       Print additional information and debug messages.
```

## Example:

```
python tax-report.py -f -a tdopierala -d '../project' -o 'reports'
```
