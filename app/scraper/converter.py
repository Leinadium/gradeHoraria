"""
Generator module
This module is used to generate
"""

from .models import Course, Classroom, Destino
from .scraper import PATH_TO_DATA_JSON, PATH_TO_DATA_DESTINO, PATH_TO_CREDENTIALS

import json
import re
import MySQLdb

all_courses = dict()
all_classrooms = list()
all_destinos = dict()


def load_credentials():
    with open(PATH_TO_CREDENTIALS, 'r') as f:
        j = json.load(f)
    return j


def load_all():
    """
    Load all classrooms into a list
    """
    global all_courses
    global all_classrooms
    global all_destinos

    with open(PATH_TO_DATA_JSON, 'r', encoding='utf8') as f:
        x = json.load(f)

    ret = list()
    for c in x:
        class_code = c['class_code']
        className = c['className'].strip()
        cred = int(c['credits'])
        dept = c['dept']

        if class_code not in all_courses:  # creating a new course
            course = Course(class_code, className, cred, dept)
            all_courses[class_code] = course
        else:
            course = all_courses[class_code]  # loading a course

        professor = c['professor']
        classroom_code = c['classroom_code']
        dest = c['destiny']
        slots = int(c['slots_left'])
        shift = c['shift']
        tr = c['time_room']  # DAY HOUR-HOUR

        r = re.match('([A-Z]+)([ ]*)([0-9][0-9]-[0-9][0-9])', tr)
        if r is not None:  # no defined timeroom
            dt = list()
            for new_dt in re.findall('([A-Z]+)([ ]*)([0-9][0-9])-([0-9][0-9])', tr):
                day = new_dt[0]
                start = new_dt[2]
                end = new_dt[3]
                dt.append((day, start, end))
            dt = ';'.join([','.join(x) for x in dt])
        else:
            dt = ''

        online = int(c['online_hours'])
        shf = int(c['SHF'])
        pre = c['pre']

        classroom = Classroom(course, classroom_code, professor, dt, dest, slots, shift, online, shf, pre)
        all_classrooms.append(classroom)

    with open(PATH_TO_DATA_DESTINO, 'r', encoding='utf8') as f:
        all_destinos = json.load(f)

    return


def save_all():

    credentials = load_credentials()

    connection = MySQLdb.connect(user=credentials['user'],
                                 passwd=credentials['passwd'],
                                 db=credentials['db'])

    cursor = connection.cursor()

    # removing previous data
    query_cleaning = """DELETE FROM turmas"""
    cursor.execute(query_cleaning)
    connection.commit()

    # removing previous data
    query_cleaning = """DELETE FROM cursos"""
    cursor.execute(query_cleaning)
    connection.commit()

    # removing previous data
    query_cleaning = """DELETE FROM destinos"""
    cursor.execute(query_cleaning)
    connection.commit()

    # adding the new data
    query_cursos = """INSERT INTO cursos (code, name, cred, dept) VALUES (%s, %s, %s, %s)"""
    to_insert = [(c.code, c.name, c.credits, c.dept) for c in all_courses.values()]
    cursor.executemany(query_cursos, to_insert)
    connection.commit()
    print("Sucessful insert", cursor.rowcount)

    # adding the new data
    to_insert = [(t.course.code, t.code, t.professor, t.days_time, t.dest, t.slots, t.shift, t.shf, t.online_hours)
                 for t in all_classrooms]

    for value in to_insert:
        query_turmas = """INSERT INTO turmas (curso, code, prof, time, dest, slots, shift, shf, online)
                          VALUES ('%s', '%s', '%s', '%s', '%s', %s, '%s', %s, %s)""" % value
        cursor.execute(query_turmas)

    connection.commit()
    print("Sucessful insert", len(to_insert))

    # adding the new data
    for code in all_destinos:
        name = all_destinos[code]
        query_destinos = """INSERT INTO destinos (code, name) VALUES ('%s', '%s')""" % (code, name)
        cursor.execute(query_destinos)

    connection.commit()
    print("Sucessul insert", len(all_destinos))

    cursor.close()
    connection.close()


def update_database():
    print("Loading the downloaded files")
    load_all()
    print("Storing in the database")
    save_all()
