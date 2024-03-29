import sys
sys.dont_write_bytecode = True
from app.src import app
from app.src.models import employee

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8888
    app.run(host=host, port=port, debug=True)
