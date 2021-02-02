from ..models import Turma
from itertools import product


def _carregar_turmas_possiveis(cursos,no_destinos):
    """
    Get all turmas within the following restrictions
    :param cursos: list of cursos code
    :param no_destinos: list of destinos to ignore
    :return: dict Curso.code -> Turma
    """

    r = Turma.query.filter(Turma.curso.in_(cursos), ~Turma.dest.in_(no_destinos)).all()
    # parsing the times

    d = dict()
    for turma in r:
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


def _validate_and_score_grade(grade, prof, no_hours, max_aulas_dia, min_aulas_dia, dia_vazio, aulas_seguidas, turno, shf):
    """
    Checks if grade if valid, and then gives a score
    :return: False if not valid, a score if valid
    """
    days = dict()
    aulas_day = dict()
    turma_day = dict()
    score = 0

    for t in grade:

        # PONTUACAO PROF
        if t.prof in prof:
            score += 20

        for time in t.time.split(';'):
            
            # PONTUACAO SHF
            if time == '':  
                if not shf:
                    score -= 20
                break

            day, start, end = time.split(',')

            # PONTUACAO HORA
            for hora in no_hours:
                if int(start) <= int(hora) <= int(end):
                    score -= 7

            # PONTUACAO TURNO
            if turno == 'T':
                score += 5 if int(start) >= 13 else -5

            elif turno == 'M':
                score += 5 if int(end) <= 13 else -5

            if day not in days:
                days[day] = list(range(int(start), int(end)))
                aulas_day[day] = 1
                turma_day[day] = [t]
            else:
                for i in range(int(start), int(end)):
                    if i in days[day]:
                        return None   # INVALID GRADE
                    days[day].append(i)
                aulas_day[day] += 1
                turma_day[day].append(t)


    for x in aulas_day.values():

        # PONTUACAO DIA VAZIO
        if x == 0:
            score += 15 if dia_vazio else -15

        # PONTUACAO MAX DE AULAS
        elif x > max_aulas_dia:
            score -= 10 * (x - max_aulas_dia)
        
        # PONTUACAO MIN DE AULAS
        elif x < min_aulas_dia:
            score -= 10 * (min_aulas_dia - x)

    # PONTUACAO AULAS SEQUENCIA
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
            score -= 10 * (seq - aulas_seguidas)
        else:
            score += 5 * seq

    return score


def run(cursos, prof, no_hours, no_destinos, max_aulas_dia, min_aulas_dia, dia_vazio, aulas_seguidas, turno, shf):
    """
    Run the generator, return the best possible Grade
    :param cursos: list of cursos code
    :param prof: list of professors names to reward
    :param no_hours: list of hours to punish
    :param no_destinos: list of destinos to ignore
    :param max_aulas_dia: integer of max class each day
    :param min_aulas_dia: integer of min class each day
    :param dia_vazio: bool "is having an empty day good?"
    :param aulas_seguidas: integer of max sequencial classes
    :param turno: 'M', 'T', 'A'
    :param shf: bool "want to have a shf"?

    :return: (erro, cursos),
             (sucesso, grade, len(grades), len(grades_validas))
    """

    turmas = _carregar_turmas_possiveis(cursos, no_destinos)
    x = _checa_turmas(turmas, cursos)
    if x:  # there is a curso with no turmas left
        return 'erro', x

    iterator = _criar_combinacoes_possiveis(turmas)

    max_score = None
    best_grade = None
    total_grades = 0
    total_grades_validas = 0
    for i in iterator:
        total_grades += 1
        x = _validate_and_score_grade(i, prof, no_hours, max_aulas_dia, min_aulas_dia, dia_vazio, 
                                        aulas_seguidas, turno, shf)

        if x is not None:
            total_grades_validas += 1
            if max_score is None or x > max_score:
                max_score = x
                best_grade = i

    if max_score is None:
        return 'erro', []

    print("pontuacao:", max_score)
    return ('sucesso', best_grade, total_grades, total_grades_validas)
