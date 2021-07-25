from random import sample, shuffle
from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SubmitField, HiddenField, RadioField, SelectField
from wtforms.validators import InputRequired
from json_operations import open_json, add_info


app = Flask(__name__)
csrf = CSRFProtect(app)

SECRET_KEY = '1a0b329df51147t0a111335d2acbfd8'
app.config['SECRET_KEY'] = SECRET_KEY

goals = open_json('database/goals.json')
teachers = open_json('database/teachers.json')
days = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница", "sat": " Суббота",
        "sun": "Воскресенье"}
data_booking = []
data_request = []


class BookingForm(FlaskForm):
    clientWeekday = HiddenField()
    clientTime = HiddenField()
    clientTeacher = HiddenField()
    clientName = StringField('Вас зовут', [InputRequired(message="Введите что-нибудь")])
    clientPhone = StringField('Ваш телефон', [InputRequired(message="Введите что-нибудь")])
    submit = SubmitField("Записаться на пробный урок")


class RequestForm(FlaskForm):
    goals = RadioField('Какая цель занятий?', choices=[("travel", "Для путешествий"), ("study", "Для школы"),
                                                      ("work", "Для работы"), ("relocate", "Для переезда"),
                                                       ("programming", "Для программирования")],
                       default="Для путешествий")
    times = RadioField('Сколько времени есть?', choices=[("1-2", "1-2 часа в неделю"),
                                                         ("3-5", "3-5 часов в неделю"),
                                                        ("5-7", "5-7 часов в неделю"),
                                                         ("7-10", "7-10 часов в неделю")],
                       default="5-7 часов в неделю")
    clientName = StringField('Вас зовут', [InputRequired(message="Введите что-нибудь")])
    clientPhone = StringField('Ваш телефон', [InputRequired(message="Введите что-нибудь")])
    submit = SubmitField("Записаться на пробный урок")


class AllForm(FlaskForm):
    options = RadioField('options', choices=[('rand', 'В случайном порядке'),
                                                ('best_rat', 'Сначала лучшие по рейтингу'),
                                                ('more_price', 'Сначала дорогие'),('less_price', 'Сначала недорогие')])
    submit = SubmitField("Сортировать")


@app.errorhandler(500)
def render_server_error(error):
    return f'<h1>Что-то не так, но мы все починим</h1><p>{error}</p>'


@app.errorhandler(404)
def render_server_error(error):
    return f'<h1>Ничего не нашлось! Вот неудача, url некорректный:(</h1><p>{error}</p>'


@app.route("/")
def main_render():
    six_teachers = sample(teachers, 6)
    return render_template('index.html', goals=goals, teachers=six_teachers)


@app.route("/all", methods=["GET", "POST"])
def all_render():
    form = AllForm()
    teachers_shuffled = teachers.copy()
    shuffle(teachers_shuffled)
    if form.validate_on_submit() and request.method == "POST":
        target = form.options.data
    else:
        target = 'rand'
    return render_template("all.html", form=form, target=target, teachers=teachers_shuffled)


@app.route("/goals/<goal>/")
def goal_render(goal):
    goal_teachers = [teacher for teacher in teachers if goal in teacher["goals"]]
    return render_template('goal.html', teachers=goal_teachers, goal=goals[goal])


@app.route("/profiles/<int:id>/")
def profile_render(id):
    return render_template('profile.html', teacher=teachers[id], goals=goals, days=days)


@app.route("/request/")
def request_render():
    form = RequestForm()
    return render_template('request.html', form=form)


@app.route("/request_done/", methods=["GET", "POST"])
def request_done_render():
    form = RequestForm()
    if form.validate_on_submit() and request.method == "POST":
        data = {}
        data['goal'] = form.goals.data
        goals_choices = dict(form.goals.choices)
        goal_label = goals_choices[data['goal']]
        data['time'] = form.times.data
        times_choices = dict(form.times.choices)
        time_label = times_choices[data['time']]
        data['name'] = form.clientName.data
        data['phone'] = form.clientPhone.data
        data_request.append(data)
        add_info("database/request.json", data_request)
        return render_template('request_done.html', goal=goal_label, time=time_label,
                               name=data['name'], phone=data['phone'])
    else:
        redirect('/request/')


@app.route("/booking/<int:id>/<day>/<time>/")
def booking_render(id, day, time):
    form = BookingForm()
    return render_template('booking.html', form=form, teacher=teachers[id], day=day, time=time, days=days)


@app.route("/booking_done/", methods=["GET", "POST"])
def booking_done_render():
    form = BookingForm()
    if form.validate_on_submit() and request.method == "POST":
        data = {}
        data['day'] = form.clientWeekday.data
        data['time'] = form.clientTime.data
        data['name'] = form.clientName.data
        data['phone'] = form.clientPhone.data
        data['teacher'] = form.clientTeacher.data
        data_booking.append(data)
        add_info("database/booking.json", data_booking)
        return render_template('booking_done.html', day=data['day'], time=data['time'],
                               name=data['name'], phone=data['phone'], days=days)
    else:
        redirect('/')


if __name__ == "__main__":
    app.run()
