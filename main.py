from src.models import employee
import sys
sys.dont_write_bytecode = True
from src import app

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000
    app.run(host=host, port=port, debug=True)
