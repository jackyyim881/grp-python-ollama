# student_manager.py

from student import Student


class StudentManager:
    def __init__(self):
        self.students = []

    def add_student(self, student):
        self.students.append(student)

    def list_students_iterator(self):
        for student in self.students:
            yield student

    def list_students_index(self):
        for i in range(len(self.students)):
            yield self.students[i]

    def search_student_by_name(self, name):
        for index, student in enumerate(self.students):
            if student.get_name() == name:
                return index
        return -1

    def get_specific_elements(self):
        if not self.students:
            return None, None, None
        first = self.students[0].get_name()
        last = self.students[-1].get_name()
        second = self.students[1].get_name() if len(
            self.students) > 1 else None
        return first, last, second

    def insert_student_at_position(self, index, student):
        if 0 <= index <= len(self.students):
            self.students.insert(index, student)
            return True
        return False

    def remove_last_student(self):
        if self.students:
            return self.students.pop()
        return None

    def remove_student_at_position(self, index):
        if 0 <= index < len(self.students):
            return self.students.pop(index)
        return None
