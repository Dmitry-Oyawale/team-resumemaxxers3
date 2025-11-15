from config import Config

from app import create_app, db
from app.main.models import *
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

app = create_app(Config)
app.config['SECRET_KEY'] = 'REPLACE_LATER'

@app.shell_context_processor
def make_shell_context():
    return {'sqla': sqla, 'sqlo': sqlo, 'db': db, 'Major': Major}

majors = ["CS", "RBE", "ME", "ECE", "AE", "DS", "MATH"]

@app.before_request
def initDB(*args, **kwargs):
    if app._got_first_request:
        db.create_all()

# fill in db with some things

@sqla.event.listens_for(Major.__table__, 'after_create')
def add_majors(*args, **kwargs):
    query = sqla.select(Major)
    if db.session.scalars(query).first() is None:
        majorsDict = [{"name":majors[i]} for i in range(len(majors))]
        # print(majorsDict)  # debugging
    for t in majorsDict:
        db.session.add(Major(name=t["name"]))
    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)