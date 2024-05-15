from app import app

# gunicorn grab 'app' and start directly

# the main is used for 'python wsgi.py' as the start
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)