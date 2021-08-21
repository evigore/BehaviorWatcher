from api import config


connex_app = config.connex_app
connex_app.add_api('swagger.yml')  # uses ./api/swagger.yml


if __name__ == '__main__':
    connex_app.run(debug=True)
