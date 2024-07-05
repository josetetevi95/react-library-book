from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
import json
import mysql.connector

# Configuration de la base de données
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'library'
}

# db_config = {
#     'user': 'root',
#     'password': '87ridfhkHgtebf$896Phd',
#     'host': 'localhost',
#     'database': 'library',
#     'port': '4306'
# }


def get_books():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM books ORDER BY id DESC')
        books = cursor.fetchall()
        cursor.close()
        conn.close()
        return 200, books
    except mysql.connector.Error as err:
        return 500, {'error': str(err)}

# Fonction pour récupérer un livre par ID
def get_book_by_id(book_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
        book = cursor.fetchone()
        cursor.close()
        conn.close()
        if book:
            return 200, book
        else:
            return 404, {'error': 'Book not found'}
    except mysql.connector.Error as err:
        return 500, {'error': str(err)}

# Fonction pour ajouter un livre dans la base de données
def add_book(post_data):
    try:
        book = json.loads(post_data)
        title = book.get('title')
        description = book.get('description')
        year = book.get('year')
        author = book.get('author')
        category = book.get('category')

        if not title or not author or not description or not year or not category:
            return 400, {'error': 'Title, description, year, author, and category are required'}

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO books (title, description, year, author, category) VALUES (%s, %s, %s, %s, %s)',
            (title, description, year, author, category)
        )
        conn.commit()
        book['id'] = cursor.lastrowid
        cursor.close()
        conn.close()
        return 201, book
    except json.JSONDecodeError:
        return 400, {'error': 'Invalid JSON data'}
    except mysql.connector.IntegrityError as err:
        return 400, {'error': 'Database integrity error: ' + str(err)}
    except mysql.connector.Error as err:
        return 500, {'error': 'Database error: ' + str(err)}
    except Exception as err:
        return 500, {'error': 'Internal server error: ' + str(err)}

# Fonction pour mettre à jour un livre
def update_book(book_id, post_data):
    try:
        book = json.loads(post_data)
        title = book.get('title')
        description = book.get('description')
        year = book.get('year')
        author = book.get('author')
        category = book.get('category')

        if not title or not author or not description or not year or not category:
            return 400, {'error': 'Title, description, year, author, and category are required'}

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE books SET title = %s, description = %s, year = %s, author = %s, category = %s WHERE id = %s',
            (title, description, year, author, category, book_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return 200, {'message': 'Book updated'}
    except json.JSONDecodeError:
        return 400, {'error': 'Invalid JSON data'}
    except mysql.connector.IntegrityError as err:
        return 400, {'error': 'Database integrity error: ' + str(err)}
    except mysql.connector.Error as err:
        return 500, {'error': 'Database error: ' + str(err)}
    except Exception as err:
        return 500, {'error': 'Internal server error: ' + str(err)}

# Fonction pour supprimer un livre
def delete_book(book_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return 200, {'message': 'Book deleted'}
    except mysql.connector.Error as err:
        return 500, {'error': str(err)}

# Fonction de gestion pour la route de test
def handle_test_route(request):
    static_data = {
        'message': 'This is a test route',
        'status': 'success',
        'data': [1, 2, 3, 4, 5]
    }
    return Response(json.dumps(static_data), status=200, mimetype='application/json')

# Routes GET
def handle_get_books(request):
    status, response = get_books()
    return Response(json.dumps(response), status=status, mimetype='application/json')

def handle_get_book(request, book_id):
    status, response = get_book_by_id(book_id)
    return Response(json.dumps(response), status=status, mimetype='application/json')

# Routes POST
def handle_add_book(request):
    post_data = request.get_data(as_text=True)
    print(post_data)
    status, response = add_book(post_data)
    return Response(json.dumps(response), status=status, mimetype='application/json')

def handle_update_book(request, book_id):
    post_data = request.get_data(as_text=True)
    status, response = update_book(book_id, post_data)
    return Response(json.dumps(response), status=status, mimetype='application/json')

# Routes DELETE
def handle_delete_book(request, book_id):
    status, response = delete_book(book_id)
    return Response(json.dumps(response), status=status, mimetype='application/json')

# Gestion des en-têtes CORS
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# URL Mapping
url_map = Map([
    Rule('/api/books', endpoint='get_books', methods=['GET']),
    Rule('/api/books', endpoint='add_book', methods=['POST']),
    Rule('/api/books/<int:book_id>', endpoint='get_book', methods=['GET']),
    Rule('/api/books/<int:book_id>', endpoint='update_book', methods=['POST']),
    Rule('/api/books/<int:book_id>', endpoint='delete_book', methods=['DELETE']),
    Rule('/api/books/<int:book_id>', endpoint='handle_options', methods=['OPTIONS']),  # Pour gérer les requêtes OPTIONS pour CORS
    Rule('/api/books', endpoint='handle_options', methods=['OPTIONS']),
    Rule('/api/test', endpoint='test_route', methods=['GET'])  # Nouvelle route de test
])

def application(environ, start_response):
    request = Request(environ)
    urls = url_map.bind_to_environ(environ)
    try:
        endpoint, args = urls.match()
        if endpoint == 'get_books':
            response = handle_get_books(request)
        elif endpoint == 'get_book':
            response = handle_get_book(request, args['book_id'])
        elif endpoint == 'add_book':
            response = handle_add_book(request)
        elif endpoint == 'update_book':
            response = handle_update_book(request, args['book_id'])
        elif endpoint == 'delete_book':
            response = handle_delete_book(request, args['book_id'])
        elif endpoint == 'handle_options':
            response = Response(status=204)  # No Content pour les OPTIONS
        elif endpoint == 'test_route':  # Nouvelle route de test
            response = handle_test_route(request)
        else:
            response = Response('Not Found', status=404)
    except HTTPException as e:
        response = e
    response = add_cors_headers(response)  # Ajouter les en-têtes CORS
    return response(environ, start_response)

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 7000, application)

