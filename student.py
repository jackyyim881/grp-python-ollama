# student.py

class Student:
    def __init__(self, student_id=0, name="", gpa=0.00):
        self.ID = student_id
        self.Name = name
        self.GPA = gpa

    def set_data(self, student_id, name, gpa):
        self.ID = student_id
        self.Name = name
        self.GPA = gpa

    def get_name(self):
        return self.Name

    def get_gpa(self):
        return self.GPA

    def __str__(self):
        return f"{self.Name} has GPA = {self.GPA:.2f}"
