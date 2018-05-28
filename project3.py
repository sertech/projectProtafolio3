from flask import Flask, render_template, request, redirect, jsonify, url_for

app = Flask(__name__)

@app.route('/')
@app.route('/CatalogApp')
def mainPage():
    return "this will display two columns Categories which will display all the available categories with each category as a link and Latest items which will display the latest items added in any category"



@app.route('/CatalogApp/<category_name>/items')
def catPage(category_name):
    return "this page will display all the categories in one panel and in the second panel it will display all the items in the selected category also it will display the number of items within a category"


@app.route('/CatalogApp/<category_name>/<item_name>')
def itemPage(category_name, item_name):
    return "this page will display the item complete description"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    