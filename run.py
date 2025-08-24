from app import craete_app


app = craete_app()

if __name__ == '__main__':
    print('Сервер запущен.......')
    app.run(debug=True)