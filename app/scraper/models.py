"""
Models module
This module stores and the classes the app will need
Classes:
    Course
    Classroom
"""
from typing import List  # for hints


class Course:
    """
    Course class. Indentified by its code (AAA0000)
    Contains the code, name, and a list of classes available
    """

    def __init__(self, code: str, name: str, cred: int, dept: str):
        self.code = code
        self.name = name
        self.credits = cred
        self.dept = dept

    def __str__(self):
        return '<Course %s [%s] >' % (self.code, self.name)


class Classroom:
    """
    Classroom class. Indentified by its code and the course
    """

    def __init__(self, course: Course, code: str,
                 professor: str, days_time: str,
                 dest: str, slots: int, shift: str,
                 online_hours: int, shf: int, pre: str):
        self.course = course
        self.code = code
        self.professor = professor
        self.days_time = days_time  # day,start,end;day,start,end...
        self.dest = dest
        self.slots = slots
        self.shift = shift
        self.shf = shf
        self.online_hours = online_hours
        self.pre = pre

    def __str__(self):
        return '<Classroom %s (%s) >' % (self.code, self.course)

    def __repr__(self):
        return '<Classroom %s (%s) >' % (self.code, self.course)


class Destino:
    def __init__(self, code, name):
        self.code = code
        self.name = name


class Schedule:
    """
    Schedule class. Has some courses
    """

    def __init__(self, classrooms: List[Classroom]):
        self.classrooms = classrooms if classrooms is not None else list()  # initial courses
        self.cred = 0
        for cr in self.classrooms:
            self.cred += cr.course.credits  # counting all the credits

    def __str__(self):
        return '<Schedule with %d courses>' % len(self.classrooms)

    def print(self):
        blank = '-------'
        sep = '  |  '
        days = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']

        print(self)
        print('|' + sep.join(days) + '|')
        for hour in range(7, 20):
            line = '|'
            for day in days:
                added_code = False
                for cr in self.classrooms:
                    for dt in cr.days_time:
                        dt_day, dt_start, dt_end = dt
                        if dt_day == day and dt_start <= hour <= dt_end:
                            line += cr.course
                            added_code = True
                            break
                if not added_code:
                    line += blank
                print(line, end='|')
        return
