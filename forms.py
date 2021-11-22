from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


# WTForm
class AddNewForm(FlaskForm):
    title = StringField("Titulo", validators=[DataRequired()])
    size = SelectField("Tipo de cuadro", choices=["Square", "Trip"], validators=[DataRequired()])
    description = StringField("Descripcion")
    url = StringField("Google Drive URL", validators=[DataRequired()])
    submit = SubmitField("Anadir Cuadro")


class UpdateForm(FlaskForm):
    title = StringField("Titulo", validators=[DataRequired()])
    description = StringField("Descripcion")
    submit = SubmitField("Actualizar Cuadro")