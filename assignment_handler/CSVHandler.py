import csv
import shutil
import datetime
import os


# TODO Workflow ??
# TODO Compare to Solution ??
# TODO Outputfile ??
# TODO AutoFeedback ??


def total_points(row: dict) -> tuple[int, int]:
    sum = 0
    ass_count = 0
    for i in row:
        if i[0] == "A":
            ass_count += 1
            if row[i] != '':
                sum += int(row[i])
    return sum, ass_count

def parse_points(feedback_path: str) -> tuple[list[str], int, int]:
    name = feedback_path.split(os.sep)[-1].rsplit(".", 1)[0].split("_")[0:2]
    with open(feedback_path, 'r') as f:
        ls = f.readlines()
        assignment_number = int(ls[0].split(" ")[-1])
        points = int(ls[1].replace("[", "").replace("]", "").split("/")[0])
    return name, points, assignment_number


class CSVHandler:
    """Handles editing on a .csv file with dependencies between columns (TotalPoints, CPass)"""

    def __init__(self, file_path: str, fieldnames: list):
        self.file_path = file_path
        self.fieldnames = fieldnames

    def init_csv(self):
        """Initializes the file with certain attributes (fieldnames), writes header"""
        with open(self.file_path, 'w', newline='') as f:
            w = csv.DictWriter(f, delimiter=',', quotechar='|', fieldnames=self.fieldnames)
            w.writeheader()

    def get_rows(self, file=None) -> list:
        """Returns all entries of the file"""
        if not file:
            with open(self.file_path, 'r', newline='') as f:
                r = csv.DictReader(f, delimiter=',', quotechar='|')
                return [{i.strip(): row[i].strip() for i in row} for row in r]
        else:
            r = csv.DictReader(file, delimiter=',', quotechar='|')
            return [{i.strip(): row[i].strip() for i in row} for row in r]

    def update(self, max_points: int = 10):
        """Updates columns that are dependent of each other"""
        rows = self.get_rows()
        for row in rows:
            s, total = total_points(row)
            row[self.fieldnames[2]] = s
            row[self.fieldnames[4]] = s >= (total * max_points) / 2

        with open(self.file_path, 'w', newline='') as f:
            w = csv.DictWriter(f, delimiter=',', quotechar='|', fieldnames=rows[0].keys())
            w.writeheader()
            if rows:
                w.writerows(rows)

    def add_exercise(self, name_point_list: list[tuple[str, str, int]]):
        """Manages adding a new exercise (header, values, dependencies)"""
        self.add_assignment()
        for i in name_point_list:
            self.add_entry_for_name(i[0], i[1], i[2])
        self.update()

    def add_assignment(self, number: int = -1):
        """Adds a new assignment column with the format AX"""
        self.create_backup()
        rows = self.get_rows()
        if number >= 0:
            for i in rows:
                i[f"A{number}"] = " "
        else:
            for i in rows:
                if list(i.keys())[-1][0] != 'A':
                    i["A1"] = " "
                else:
                    print()
                    i[f"A{int(list(i.keys())[-1][1::]) + 1}"] = ' '
        with open(self.file_path, 'w', newline='') as f:
            w = csv.DictWriter(f, delimiter=',', quotechar='|', fieldnames=rows[0].keys())
            w.writeheader()
            if rows:
                w.writerows(rows)

    def add_entry_for_name(self, name: str, lastname: str, entry: float, number: str = '-1') -> bool:
        """Edits a specific value identified by name and optionally by column (default last)"""
        self.create_backup()
        rows = self.get_rows()
        found = False
        for row in rows:
            if row['Name'] == name and row['LastName'] == lastname:
                if number not in list(row.keys()):
                    number = list(row.keys())[-1]
                row[number] = str(entry)
                found = True
                break
        if found:
            with open(self.file_path, 'w', newline='') as f:
                w = csv.DictWriter(f, delimiter=',', quotechar='|', fieldnames=rows[0].keys())
                w.writeheader()
                w.writerows(rows)
        return found

    def create_backup(self):
        """Backups the file because we are smart"""
        shutil.copyfile(self.file_path, f"""{'.'.join(self.file_path.split('.')[0:-1])}_{str(datetime.datetime.now()).replace(":", "_").replace("-", "_").split(".")[0]}.{self.file_path.split('.')[-1]}""".replace(" ", ''))
        # one has to admire this line of code above
