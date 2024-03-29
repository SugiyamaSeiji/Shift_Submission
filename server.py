import sys
sys.dont_write_bytecode = True
from src import app
from src.models import employee
from src import db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    host = '127.0.0.1'
    port = 8888
    app.run(host=host, port=port, debug=True)
