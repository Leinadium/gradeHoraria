from flask import redirect, render_template, url_for, request

from . import resultado
from ..models import Curso, Turma, Grade
from . import grade_generator
from .. import db


@resultado.route('/gerar')
def gerar_resultado():
    """
    Create grade. Stores it on a database. Redirects to /g/xxxx
    Has args (cursos, no_prof, no_hours, no_destinos, max_aulas_dia, min_aulas_dia, aulas_seguidas, dia_vazio)
    """

    # getting the data
    cursos = request.args.getlist('cursos')
    no_prof = request.args.getlist('no_prof')
    if no_prof and no_prof[0] == '':  # selecting and deselecting results in ['']
        no_prof = []
    no_hours = request.args.getlist('no_hours')
    if no_hours and no_hours[0] == '':  # selecting and deselecting results in ['']
        no_hours = []
    no_destinos = request.args.getlist('no_destinos')
    if no_destinos and no_destinos[0] == '':  # selecting and deselecting results in ['']
        no_destinos = []
    max_aulas_dia = request.args.get('max_aulas_dia')
    min_aulas_dia = request.args.get('min_aulas_dia')
    dia_vazio = request.args.get('dia_vazio')
    aulas_seguidas = request.args.get('aulas_seguidas')

    print('cursos', cursos)
    print('no_prof', no_prof)
    print('no_hours', no_hours)
    print('no_destinos', no_destinos)
    print('max_aulas_dia', max_aulas_dia, type(max_aulas_dia))
    print('min_aulas_dia', min_aulas_dia, type(min_aulas_dia))
    print('dia_vazio', dia_vazio, type(dia_vazio))
    print('aulas_seguidas', aulas_seguidas)

    # generating the grade
    # best_grade = [turma1, turma2, turma3...] OR ['erro', error]
    best_grade = grade_generator(cursos, no_prof, no_hours, no_destinos, int(max_aulas_dia), int(min_aulas_dia),
                                 True if dia_vazio == 'True' else False, int(aulas_seguidas))

    # checking if it is invalid
    if best_grade[0] == 'erro':
        return redirect(url_for('resultado.erro', c=best_grade[1]))

    # creating the id of grade, and its string
    s = '_'.join([str(x.curso) + '-' + str(x.code) for x in best_grade])
    i = format(hash(s), 'x')
    print(i)

    # check if it has been generated before
    if Grade.query.filter_by(id=i).first() is None:
        # stores in the database
        nova_grade = Grade(id=i, grade=s)  # creating the new object
        db.session.add(nova_grade)  # storing in the database
        db.session.commit()  # saving

    # redirecting to the /g/
    return redirect(url_for('resultado.g', i=i))


@resultado.route('/erro')
def erro():
    """
    Handles the error page
    Has args (cursos)
    """
    cursos = request.args.getlist('c')

    return render_template('resultado/erro.html', cursos=cursos, title='Erro')


@resultado.route("/g/<string:i>")
def g(i):
    """
    Handles the final result page. Receives the id of grade.
    """
    s = Grade.query.filter_by(id=i).first_or_404().grade

    # parsing data
    # curso-turma_curso-turma_curso-turma....
    list_turmas_string = [x.split('-') for x in s.split('_')]

    # getting the data from db
    list_turmas = [Turma.query.filter_by(curso=x[0], code=x[1])[0] for x in list_turmas_string]

    # generate the result page with the turma objects
    escolhas = []
    for indice, x in enumerate(list_turmas):
        for t in x.time.split(';'):
            dia, inicio, fim = t.split(',')
            fim += ':00'
            inicio += ':00'
            escolhas.append({'dia': dia, 'inicio': inicio, 'fim': fim, 'curso': x.curso, 'turma': x.code,
                             'indice': indice + 1})

    # generate link
    link = 'localhost:5000/g/' + i

    return render_template('resultado/resultado.html', escolhas=escolhas, title='Resultado', link=link)


@resultado.route("/info/<string:curso_turma>")
def info(curso_turma):
    code_curso, code_turma = curso_turma.split('_')
    turma = Turma.query.filter_by(code=code_turma, curso=code_curso)[0]
    print('turma:', turma)
    curso = Curso.query.filter_by(code=code_curso)[0]
    print('curso:', curso)

    return render_template('resultado/info.html', turma=turma, curso=curso)
