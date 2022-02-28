
# Usage

---

## Setup

### Configuration

Before starting this script, some parameters need to be specified.
All the parameters, that can be configured, are found in `Config.py`.
The configuration of these constants is outlined in 
[Configuration](https://github.com/3nol/correction/blob/master/docs/Configuration.md).  

### Initializing the database and folder structure 

Optionally, but recommended, is to use a database table to store all the points.
For that, the table is assumed to have the following format:

|student_name|ass_01|ass_02|ass_03|...|total_points|
|------------|------|------|------|---|------------|
|name1       |5     |3     |8     |...|16          |
|...

For this, you don't need to pull out your SQL skills, `DatabaseConnector#initialize_table()` does that for you.
Provided, you entered database credentials in the `Config.py`, see above.
To fill the student names automatically in the database, use `Correction#init_names()` with a given list of names.

Now, you have the database set up and your students' submission folders ready to go.
These folders now need somewhere the resulting feedback files are placed in (configurable under "feedback_folder"),
as well as a folder where the script can dump concatenated solutions (configurable under "concat_folder").
The latter is required because after finding all submitted files, their content is bundled and can be reused from the
concatenated version, found in this folder.

Obviously, these folders can be generated automatically. `Correction#init_folders()` is your friend.

## Correction process

### Starting the thing

Finally, you are ready to start the process using the CLI.
```shell
python Start.py XX [-s | --solution-only] [-o | --offline-mode]
```
The assignment number **XX** has to passed as an argument always!
Optionally, two flags can be specified:
- Solution-Only-Mode: the script only considers students that actually handed in something 
- Offline-Mode: syncing with the database is disabled

### Selecting solutions

Depending on your situation, different things might happen:
1. The *feedbacks.dict* file either is not present, or used with another assignment number: \
   In this case, you are prompted whether the file should be overwritten. "y" continues, "n" exits the program.
2. The feedback file is present but no submission filepaths were selected previously: \
   Now, the script tries to autodetect the correct files. 
   If it does find multiple possibilities (ambiguous), you are prompted to select one by index.
   If it doesn't find anything, you are prompted to, either accept no solution (enter)
   or specify the full relative path(s) to the file(s).
3. The filepaths were selected previously: \
   You can re-use them by accepting, or re-select them (like above) by denying.

After that is completed, the concatenated submission files and the feedback file templates are generated.
If the script detects changes between the new concatenated file and an already present one,
it will display previous feedback and ask you whether it is still valid.

### Mid-correction actions

Submissions are cycled through sequentially, in the following order:
1. On the outer level, the main tasks are cycled through.
2. Then, individual students are considered.
3. Per student (within a main task), the subtasks are iterated through.

Per submission, the relevant text is displayed and the correcting person is asked to write a feedback comment.
If a task cannot be found within a submission, the script asks you whether it is present.
Accepting opens the comment prompt, denying writes "No solution." and 0 points to the feedback.

After the comment, points can be given: full (solution correct), partly to none (solution incorrect).
A given comment and points are saved. Here comes the *feedbacks.dict* into play.
Having opened this file, you will notice that each line has this format:
```
maintask.subtask_id :: points, comment
```
Now, if you are prompted to give feedback, instead of writing a comment, you can use the following shortcut: `>id`.
This will retrieve the corresponding entry with points and feedback and write it to the student's feedback.
Very handy for common mistakes.

Another shortcut, while prompted to enter a comment, is: `>s`.
This just prints the submission content again.

### Exiting the program 

A regular exit would be to finish giving feedback to all students.
The program then rescans all feedback files, recalculates points, syncs everything to the database and exists.
Alternatively you can just kill it, if you feel like it. \
(Actually that's fine, was developed with robustness in mind.) 
