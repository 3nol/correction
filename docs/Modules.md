
# Modules

---

## Starting up

### Config

Contains the `GlobalConstants` class whose only purpose is, to make configured constants available globally.
This is done with the static method `get(key)` which retrievs the entries.
A special key request is `points_XX` which maps to the correct point distribution for the assignment XX.
The only entry which can be set is `offline_mode`.

### Start

Handles the command-line arguments and passes them on to the `Correction` class.
Two optional flags are possible, *solution-only* and *offline-mode*.
If the former is true, a list of students, who handed in something for the assignment, is collected.
This list is then passed in to `Correction`. If this mode is not active, all students are considered.


## Special data structures

### ExercisePointer

Abstraction for saving the current state of correction. Kind of a fancy tuple of a main and subtask.
Has methods for incrementing and decrementing the pointer so that it jumps only between existing exercises. 

### FileDictionary

Solution we came up with for displaying already given feedbacks in a second window.
All feedbacks, together with their points, are stored in a file at `feedback_filepath`.
Data structure is actually a dictionary but kept in sync with a local file at runtime, i.e. changes with dict updates.
Allows for reusing existing feedbacks by using an id.

### PriorityGroups

Data structure containing hierarchically ordered groups of objects. In this case, the priorities are the exercise 
numbers, in an increasing order. This allows for correcting students' solutions that don't start of on the same level.
Using PriorityGroups, students, who solved a "lower" / smaller exercise, are corrected first and then moved up in the 
priority group hierarchy. That way, all students' solutions are collected on the way and no one is left out. \
Additionally, this has the benefit that no progress save is needed. The script can be killed at any time and 
PriorityGroups makes sure that everything restarts correctly and nothing is forgotten. 


## Feedback handler

### Correction

Contains the central `Correction` class which encapsulates a correction process for one assignment.
The class is instantiated with a string assignment number, in a two-digit format.
Additionally, a list of students can be passed for only considering a subset of students.
The process is started by calling `start()`. This method first initializes the `task_queue` (PriorityQueue).
After that, the all students are sequentially cycled through and the interactive correction takes place.
Afterwards, points are recalculated to minimize errors, and, if not in *offline-mode*, synced to the database. 

### DirectoryPreparation

This does most of the hard work. At the start of the correction process, `extract_solutions()` is called to pick out
all submissions the current assignment. Once all file paths to the associated files were found,
they are cached in the `XX_feedbacks.dict` file under the attribute `_solution_files`.
Because of the script's ability to be stopped at any time, the preparation was built to deal with updated submissions.
If this is the case, `compare_old_correction_to_new_solution()` (nice name) is called. Here, the correcting person can 
interactively decide whether already given feedback is still relevant.
Additionally, this module does the pre-generation of feedback file templates which are filled later on.

## Utilities

### DatabaseConnector

Does all the work considering the database. The most central method is `sql_query()` which just takes a string 
SQL query and passes it on to the database. Queried results are returned. \
With `initialize_table()` the needed database (named *points_table*) can be created.
Other methods are for writing points to the database and updating conditional attributes 
(`total_points` being the sum of all `ass_XX` fields).

### Utility

Random collection of helpful methods. The most important being `get_index()`.
This one finds tasks in submissions and points in feedback files. It works by using the collections of possible matches
('maintask_prefixes' and 'subtask_prefixes') to match against every line. \
Other methods are `get_solution()` (retrieves submission to be printed),
`load_feedback()` (deals with the input of feedback and points) and `insert_in_file()` which is used for the feedbacks.

### Tree

Very neat module that allows for pretty printing of file trees. May become a pip package at some time.  