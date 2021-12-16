from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


# WTForm
class AddNewForm(FlaskForm):
    title = StringField("Titulo", validators=[DataRequired()])
    size = SelectField("Tipo de cuadro", choices=["Square", "Trip", "Wall"], validators=[DataRequired()])
    description = CKEditorField("Descripcion")
    url = StringField("Google Drive URL", validators=[DataRequired()])
    submit = SubmitField("Anadir Cuadro")


class UpdateForm(FlaskForm):
    title = StringField("Titulo", validators=[DataRequired()])
    description = CKEditorField("Descripcion")
    size = SelectField("Tipo de cuadro", choices=["Square", "Trip", "Wall"], validators=[DataRequired()])
    submit = SubmitField("Actualizar Cuadro")