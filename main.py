from flask import Flask
from mongoengine import connect

from views import cart
from views import catalog
from views import presentation
from views import tax
from views import oms

app = Flask(__name__)
connect('jetcart')

app.register_blueprint(catalog.blueprint)
app.register_blueprint(cart.blueprint)
app.register_blueprint(tax.blueprint)
app.register_blueprint(presentation.blueprint)
app.register_blueprint(oms.blueprint)


@app.before_request
def setup_request_func():
    pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(port=5000, debug=True)
