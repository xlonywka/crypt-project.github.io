from flask import *
from flask_restful import reqparse, abort, Api, Resource
from loginform import LoginForm
from signupform import SignUpForm
from add_news import AddNewsForm
from db_connect import *

db = DB()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

#WORK WITH API-------------------------------------------------------------
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('user_id', required=True, type=int)


class NewsApi(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        news = NewsModel(db.get_connection()).get(news_id)
        return jsonify({'news': news})
 
    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        NewsModel(db.get_connection()).delete(news_id)
        return jsonify({'success': 'OK'})

class NewsListApi(Resource):
    def get(self):
        news = NewsModel(db.get_connection()).get_all()
        return jsonify({'news': news})
 
    def post(self):
        args = parser.parse_args()
        news = NewsModel(db.get_connection())
        news.insert(args['title'], args['content'], args['user_id'])
        return jsonify({'success': 'OK'})

api.add_resource(NewsListApi, '/api/news') # для списка объектов
api.add_resource(NewsApi, '/api/news/<int:news_id>')

def abort_if_news_not_found(news_id):
    if not NewsModel(db.get_connection()).get(news_id):
        abort(404, message="News {} not found".format(news_id))
#WORK WITH API-------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return '<h1 align="center">Error 418</h1><hr width="100%"> <h3 align="center">I am a teapot.</h3>'

#WORK WITH LOGIN AND LOGOUT-------------------------------------------------

@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/login')
    news = NewsModel(db.get_connection()).get_all()
    return render_template('index.html', username=session['username'],
                           news=news)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UserModel(db.get_connection())
        user_model.init_table()
        exists = user_model.exists(user_name, password)
        if (not exists[0]):
            user_model.insert(user_name, password)
        return redirect("/index")
    return render_template('signup.html', title='Регистрация', form=form)    

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UserModel(db.get_connection())
        user_model.init_table()
        exists = user_model.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
        return redirect("/index")
    return render_template('login.html', title='Авторизация', form=form)

   
@app.route('/success', methods=['GET', 'POST'])
def success():
    return render_template('succes.html', title='Заработало')

@app.route('/logout')
def logout():
    session.pop('username',0)
    session.pop('user_id',0)
    return redirect('/login')

#WORK WITH LOGIN AND LOGOUT-------------------------------------------------


#WORK WITH NEWS-------------------------------------------------------------
@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        price = form.price.data
        place = form.place.data
        phonenumber = form.phonenumber.data
        nm = NewsModel(db.get_connection())
        nm.insert(session['user_id'], phonenumber, title, content, price, place)
        return redirect("/index")
    return render_template('add_news.html', title='Добавление новости',
                           form=form, username=session['username'])

@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news1(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    nm.delete(news_id)
    return redirect("/index")


@app.route('/news',  methods=['GET'])
def get_news():
    news = NewsModel(db.get_connection()).get_all()
    return jsonify({'news': news})

@app.route('/news/<int:news_id>',  methods=['GET'])
def get_one_news(news_id):
    news = NewsModel(db.get_connection()).get(news_id)
    if not news:
        return jsonify({'error': 'Not found this news'})
    return jsonify({'news': news})

@app.route('/news', methods=['POST'])
def create_news():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['user_id', 'content', 'title', 'phonenumber', 'price', 'place']):
        return jsonify({'error': 'Bad request'})
    news = NewsModel(db.get_connection())
    news.insert(request.json['user_id'], request.json['content'],
                request.json['title'], request.json['phonenumber'], request.json['price'], request.json['place'])
    return jsonify({'success': 'OK'})

@app.route('/news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    news = NewsModel(db.get_connection())
    if not news.get(news_id):
        return jsonify({'error': 'Not found'})
    news.delete(news_id)
    return jsonify({'success': 'OK'})

#WORK WITH NEWS-------------------------------------------------------------


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')

