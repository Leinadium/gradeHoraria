from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField, IntegerField, BooleanField, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from ..models import Turma, Curso


class CreatingForm(FlaskForm):
    """
    Form for users to create their grade
    """
    cursos = QuerySelectMultipleField("Disciplinas", query_factory=lambda: Curso.query.order_by('name'),
                                      get_label=lambda x: '%s - %s' % (x.code, x.name))
    submit = SubmitField("Avançar")

    def validate_cursos(self, field):
        x = sum([x.cred for x in field.data])
        if x > 30:
            raise ValidationError("A soma dos créditos das disciplinas é maior que o permitido (30 créditos): %d" % x)


class ConfigForm(FlaskForm):
    """
    Form for preconfiguration of their grade
    """

    professores = SelectMultipleField('Selecione o(s) professor(es) a ser(em) retirado(s)', validate_choice=False)
    times = SelectMultipleField('Selecione a(s) hora(s) do dia a ser(em) retirada(s)', validate_choice=False)
    destinos = SelectMultipleField('Selecione o(s) destino(s) da(s) turma(s) que não podem ser frequentadas',
                                   validate_choice=False)
    maximo_aulas_dia = IntegerField("Qual o máximo de aulas que é aceitável ter em um só dia", default=5)
    minimo_aulas_dia = IntegerField("Qual o mínimo de aulas que é aceitável ter em um só dia"
                                    "(um dia sem aulas não é considerado)", default=0)
    dia_vazio = BooleanField("Se possível, deixar um dia sem aulas", default=True)
    aulas_seguidas = IntegerField("Se possível, até quantas aulas em sequência "
                                  "(0 caso não queira ter aulas em sequência)", default=3)

    submit = SubmitField("Avançar")

    def __init__(self, professores, times, destinos, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)
        self.professores.choices = professores
        self.times.choices = times
        self.destinos.choices = destinos

