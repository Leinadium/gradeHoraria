from app import db


class Curso(db.Model):
    """
    Create a Course table
    """
    __tablename__ = 'cursos'

    code = db.Column(db.String(7), index=True, primary_key=True)
    name = db.Column(db.String(30))
    cred = db.Column(db.Integer)
    dept = db.Column(db.String(3))

    # turmas = db.relationship('Turma', backref='curso', lazy='dynamic')

    def __repr__(self):
        return self.code


class Turma(db.Model):
    """
    Create a Classroom table
    """
    __tablename__ = 'turmas'

    curso = db.Column(db.String(7), db.ForeignKey('cursos.code'), primary_key=True)
    code = db.Column(db.String(3), index=True, primary_key=True)
    prof = db.Column(db.String(50))
    time = db.Column(db.String(50))  # day,start,end;day,start,end...
    dest = db.Column(db.String(3), primary_key=True)
    slots = db.Column(db.Integer)
    shift = db.Column(db.String(1))
    shf = db.Column(db.Integer)
    online = db.Column(db.Integer)
    # pre is useless here

    def __repr__(self):
        return '<Turma %s [%s] (%s) >' % (self.code, self.curso, self.time)


class Destino(db.Model):
    """
    Create a Destino table
    """
    __tablename__ = 'destinos'

    code = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return '<Destino %s>' % self.code


class Grade(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.String(30), primary_key=True)
    grade = db.Column(db.String(100))

    def __repr__(self):
        return '<Grade %d>' % self.id
