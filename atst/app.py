import tornado.web
from atst.handlers.main import MainHandler
from atst.home import home
from tornado.web import url

def make_app(**kwargs):
    app = tornado.web.Application([
            url( r"/",           MainHandler, {'page': 'home'},       name='home' ),
            url( r"/requests",   MainHandler, {'page': 'requests'},   name='requests' ),
            url( r"/users",      MainHandler, {'page': 'users'},      name='users' ),
            url( r"/reports",    MainHandler, {'page': 'reports'},    name='reports' ),
            url( r"/calculator", MainHandler, {'page': 'calculator'}, name='calculator' ),
        ],
        template_path = home.child('templates'),
        static_path   = home.child('static'),
        **kwargs
    )
    return app