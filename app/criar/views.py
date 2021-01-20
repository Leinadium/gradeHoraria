from flask import redirect, render_template, url_for, request

from . import criar
from .forms import CreatingForm, ConfigForm
from ..models import Curso, Turma, Destino
from .. import db

from json import dumps


@criar.route('/criar', methods=['GET', 'POST'])
def inicio():
    """
    Handle requests to the /criar route
    """

    all_cursos = Curso.query.order_by('code')
    dict_cursos = [{'label': '%s [%s]' % (x.code, x.name), 'value': x.code} for x in all_cursos]

    return render_template('criar/inicio.html', title='Criar', dict_cursos=dict_cursos)


@criar.route('/criar/<string:escolhas>', methods=['GET', 'POST'])
def configuracao(escolhas):
    """
    Handle the configurations of grade
    """
    # all courses
    escolhas = escolhas.split('-')

    # all classrooms
    all_turmas = []
    for e in escolhas:
        all_turmas.extend([x for x in Turma.query.filter_by(curso=e)])

    # finding all the professores
    professores = set()
    professores.update([x.prof for x in all_turmas])
    professores = [{'label': x, 'value': x} for x in professores]  # final dicts

    # finding all the possible times
    times = set()
    for t in all_turmas:
        if t.time == '':
            continue
        for tt in t.time.split(';'):
            print(tt)
            day, start, end = tt.split(',')
            times.update(list(range(int(start), int(end))))

    times = [{'value': str(x), 'label': '%02dh' % x} for x in times]  # final tuples

    # finding all the destinos
    destinos = set()
    for t in all_turmas:
        d = t.dest
        destinos.update(Destino.query.filter_by(code=d))

    destinos = [{'value': x.code, 'label': '%s - %s' % (x.code, x.name)} for x in destinos]  # final tuples

    '''    form = ConfigForm(professores, times, destinos)

    if form.validate_on_submit():
        return redirect(url_for('resultado.criar_resultado', cursos=escolhas, no_prof=form.professores.data,
                                no_hours=form.times.data, no_destinos=form.destinos.data,
                                max_aulas_dia=form.maximo_aulas_dia.data, min_aulas_dia=form.minimo_aulas_dia.data,
                                dia_vazio=form.dia_vazio.data, aulas_seguidas=form.aulas_seguidas.data))

    return render_template('criar/configuracao.html', form=form, title='Configuracao')
    '''
    return render_template('criar/configuracao.html', title='Configuracao', list_cursos=dumps(escolhas),
                           dict_professores=dumps(professores), dict_horas=dumps(times), dict_destinos=dumps(destinos))
