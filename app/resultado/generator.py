from ..models import Turma
from itertools import product


def _carregar_turmas_possiveis(cursos, no_prof, no_hours, no_destinos):
    """
    Get all turmas within the following restrictions
    :param cursos: list of cursos code
    :param no_prof: list of professors names to ignore
    :param no_hours: list of hours to ignore
    :param no_destinos: list of destinos to ignore
    :return: dict Curso.code -> Turma
    """

    r = Turma.query.filter(Turma.curso.in_(cursos), ~Turma.prof.in_(no_prof),
                           ~Turma.dest.in_(no_destinos)).all()
    # parsing the times
    new_r = []
    for turma in r:
        to_add = True
        for time in turma.time.split(';'):
            if time == '':
                break
            day, start, end = time.split(',')
            for h in no_hours:
                if int(start) <= int(h) <= int(end):
                    to_add = False
                    break

        if to_add:
            new_r.append(turma)

    d = dict()
    for turma in new_r:
        if turma.curso not in d:
            d[turma.curso] = [turma]
        else:
            d[turma.curso].append(turma)

    return d


def _criar_combinacoes_possiveis(dicionario_turmas):
    """
    Generate all permutations for the possible classrooms
    :param dicionario_turmas: dict Curso.code -> Turma
    :return: iterator to all possible permutations
    """
    turmas = dicionario_turmas.values()
    return [p for p in product(*turmas)]


def _checa_turmas(turmas_escolhidas, cursos):
    r = []
    if len(turmas_escolhidas) != len(cursos):
        for c in cursos:
            if c not in turmas_escolhidas:
                r.append(c)
    return r


def _validate_and_score_grade(grade, max_aulas_dia, min_aulas_dia, dia_vazio, aulas_seguidas):
    """
    Checks if grade if valid, and then gives a score
    :return: False if not valid, a score if valid
    """
    days = dict()
    aulas_day = dict()
    turma_day = dict()
    for t in grade:
        # if t.slots == 0:  # check slots
        #     return None

        for time in t.time.split(';'):
            if time == '':
                break
            day, start, end = time.split(',')
            if day not in days:
                days[day] = list(range(int(start), int(end)))
                aulas_day[day] = 1
                turma_day[day] = [t]
            else:
                for i in range(int(start), int(end)):
                    if i in days[day]:
                        return None
                    days[day].append(i)
                aulas_day[day] += 1
                turma_day[day].append(t)

    score = 0
    for x in aulas_day.values():
        if x == 0:
            score += 10 if dia_vazio else - 10

        elif x > max_aulas_dia:
            score -= 5
        elif x < min_aulas_dia:
            score -= 5

    for x in turma_day.values():
        seq = 1
        for turma in x:
            for t in turma.time.split(';'):
                if t == '':
                    break
                end = int(t.split(',')[2])
                for turma2 in x:
                    for tt in turma2.time.split(';'):
                        start = int(tt.split(',')[1])
                        if end + 1 == start:
                            seq += 1
        if seq > aulas_seguidas:
            score -= 5 * (seq - aulas_seguidas)
        else:
            score += 2 * seq

    return score


def run(cursos, no_prof, no_hours, no_destinos, max_aulas_dia, min_aulas_dia, dia_vazio, aulas_seguidas):
    """
    Run the generator, return the best possible Grade
    :param cursos: list of cursos code
    :param no_prof: list of professors names to ignore
    :param no_hours: list of hours to ignore
    :param no_destinos: list of destinos to ignore
    :param max_aulas_dia: integer of max class each day
    :param min_aulas_dia: integer of min class each day
    :param dia_vazio: bool "is having an empty day good?"
    :param aulas_seguidas: integer of max sequencial classes
    :return: list of best possible turmas to create a grade
    """

    turmas = _carregar_turmas_possiveis(cursos, no_prof, no_hours, no_destinos)
    # print('turmas', turmas)
    x = _checa_turmas(turmas, cursos)
    if x:  # there is a curso with no turmas left
        return 'erro', x

    for t in turmas:
        print(turmas[t])

    iterator = _criar_combinacoes_possiveis(turmas)
    print('tamanho do iter:', len(iterator))
    print('iter', iterator)

    max_score = None
    best_grade = None
    for i in iterator:
        x = _validate_and_score_grade(i, max_aulas_dia, min_aulas_dia, dia_vazio, aulas_seguidas)
        if x is not None:
            if max_score is None or x > max_score:
                max_score = x
                best_grade = i

    if max_score is None:
        print("nao achei")
        return 'erro', []

    print(best_grade)
    print('score', max_score)
    return best_grade
