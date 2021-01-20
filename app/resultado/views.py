from flask import redirect, render_template, url_for, request

from . import resultado
from ..models import Curso, Turma, Destino
from . import grade_generator


@resultado.route('/resultado')
def criar_resultado():
    """
    Handles the result page
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

    best_grade = grade_generator(cursos, no_prof, no_hours, no_destinos, int(max_aulas_dia), int(min_aulas_dia),
                                 True if dia_vazio == 'True' else False, int(aulas_seguidas))

    if best_grade[0] == 'erro':
        return redirect(url_for('resultado.erro', cursos=best_grade[1]))

    nome_cursos = [x.curso for x in best_grade]
    nome_turmas = [(x.code, x.prof, x.curso, x.time) for x in best_grade]
    return render_template('resultado/index.html', nome_cursos=nome_cursos, nome_turmas=nome_turmas, title='Resultado')


@resultado.route('/erro')
def erro():
    """
    Handles the error page
    Has args (cursos)
    """
    cursos = request.args.getlist('c')

    return render_template('resultado/erro.html', cursos=cursos)
