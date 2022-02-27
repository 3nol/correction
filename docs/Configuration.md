
# Configuration

---

## Prerequisites

This script assumes that each of the people receiving feedback, hand in their solution in a folder, named by themselves.
This way, when going through the students' folders they can be identified and their points entered correctly.
The assignments, that will be corrected, should be divided into tasks and optionally into subtasks, e.g. 1, 2a, 2b. \
The points per student are stored inside a database. Points are assumed to be integers or half points (`.5`). \
Using a database tool, like *DataGrip* by *JetBrains*, the table can be exported into a more common *Excel* format.


## Configurable constants

The entire configuration can be entered in the file **Config.py** where the `__conf` dictionary stores all entries.
Python dictionaries have a JSON-like format, making configuration easy.

### Basic data

All the underlying specifications around the correction process.
- `corrector`: the correcting person's name which will be written in the feedback files
- `source_path`: directory wherein all students' folders lay
- `feedback_filepath`: filepath for the *feedback.dict* file, storing all given feedbacks
- `offline_mode`: disables syncing with the database, contents are only written locally

### Assignment point distribution

Description of maximum points for each exercise.
- `points_`: dictionary containing two-digit-numbered entries of the assignment number
  - `XX`: list of points for assignment XX, first sublist entry corresponds to first task and so on...

If a sublist entry has more than one number inside it, each number corresponds to a subtask. \
Example: `01: [[3,2], [4]]` means, exercise 1a gives 3, 1b gives 2, and exercise 2 gives 4 points.

### Database credentials

Specification of the database connection credentials.
- `db`: dictionary containing all database attributes
  - `user`: username in the database
  - `password`: password for the database
  - `host`: host domain
  - `port`: port number, default ports are: PostgreSQL - 5432, MySQL - 3306
  - `database`: name of the database

### Using and excluding names

Naming folders in which is operated and excluding unwanted things.
- `concat_folder`: all relevant files for an assignment are concatenated into one, these files are stored here
- `feedback_folder`: the generated feedback files with points are stored here
- `excluded_names`: (folder) names which are excluded when going through `source_path`
- `excluded_filetypes`: filetypes or matches which should not be picked up by the solution detection
- `excluded_folders`: folders inside a student's directory which should not considered, e.g. the .git folder

### Solution detection in assignments

When detecting individual exercise and task solutions, the following indicators are used.
- `maintask_prefixes`: list of words which indicate the start of a main task, e.g. 'Exercise', 'No.'
- `subtask_prefixes`: list of words which match for a subtask
