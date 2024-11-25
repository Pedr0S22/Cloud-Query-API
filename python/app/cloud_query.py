##
## =============================================
## ======== Sistema de Gestão de Dados =========
## ============== LECD  2024/2025 ==============
## =============================================
## =================== Demo ====================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors: 
##   José D'Abruzzo Pereira <josep@dei.uc.pt>
##   Gonçalo Carvalho <gcarvalho@dei.uc.pt>
##   University of Coimbra


'''
How to run?
$ python3 -m venv cloud_query
$ source cloud_query/bin/activate
$ pip3 install flask
$ pip3 install jwt
$ pip3 install psycopg2-binary
$ python3 cloud_query.py
--> Ctrl+C to stop
$ deactivate
'''
import bcrypt
import jwt
from flask import Flask, jsonify, request
import logging
import psycopg2
import time

app = Flask(__name__) 
password_token="cloud_query123"

def generate_token(user_id):
    payload = {
        'id': user_id,
        'exp': time.time() + 3600 #1 hora de acesso por este token
    }
    token=jwt.encode(payload, password_token,algorithm='HS256') #HS256 (HMAC-SHA256) is a commonly used symmetric algorithm. It means the same secret key is used for both signing and verifying the token.
    return token
def verify_token():
    token= request.headers.get('Authorization') #Temos de explicar isto
    if not token:
        return jsonify({'error':'Token is missing'}), 401
    try:
        if token.startswith("Bearer "):
            token = token[7:]

        payload = jwt.decode(token, password_token, algorithms=["HS256"])

        if payload["exp"] < time.time():
            return jsonify({"message": "Token expirado!"}), 401

        return payload

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expirado!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Token inválido!"}), 401

@app.route('/cloud-query/')
def hello(): 
    return """

    Cloud Query!  <br/>
    <br/>
    Trabalho realizado por:<br/>
    Francisca<br/>
    Pedro <br/>
    Ramyad<br/>
    """

#Registo do user

@app.route('/cloud-query/user', methods=['POST'])
def add_users():
    logger.info("###              DEMO: POST /users              ###");
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- new user  ----")
    logger.debug(f'payload: {payload}')

    # parameterized queries, good for security and performance
    statement = """
                  INSERT INTO user_ (username, email, password) 
                          VALUES ( %s,   %s ,   %s )"""
    has_password=bcrypt.hashpw(payload['password'].encode('utf-8'), bcrypt.gensalt())
    values = (payload['username'], payload['email'], has_password.decode('utf-8'))


    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'Inserted!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)

#Login user
@app.route('/cloud-query/user', methods=['PUT'])
def login():
    logger.info("###              DEMO: PUT /users              ###")

    conn = db_connection()
    cur = conn.cursor()

    payload = request.get_json()
    username = payload.get('username')
    password = payload.get('password')

    cur.execute("SELECT * FROM user_ where username = %s", (username,))
    rows = cur.fetchall()

    if len(rows) == 0:
        return jsonify({'status':401,'errors': 'Username or password incorrect!'})

    row = rows[0]

    try:
        if bcrypt.checkpw(password.encode('utf-8'), row[3].encode('utf-8')):
            token = generate_token(row[0])
            return jsonify({'status': 200, 'result': token.decode('utf-8')}), 200
        else:
            return jsonify({'status': 401, 'errors': 'Username or password incorrect!'}), 401
    except ValueError:
        return jsonify({'status': 500, 'errors': 'Hash de senha inválido no banco de dados!'}), 500










##      Demo GET
##
## Obtain all departments, in JSON format
##
## To use it, access: 
## 
##   http://localhost:8080/departments/
##

@app.route("/cloud-query/departments/", methods=['GET'], strict_slashes=True)
def get_all_departments():
    logger.info("###              DEMO: GET /departments              ###");

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT ndep, nome, local FROM dep")
    rows = cur.fetchall()

    payload = []
    logger.debug("---- departments  ----")
    for row in rows:
        logger.debug(row)
        content = {'ndep': int(row[0]), 'nome': row[1], 'localidade': row[2]}
        payload.append(content) # appending to the payload to be returned

    conn.close()
    return jsonify(payload)



##
##      Demo GET
##
## Obtain department with ndep <ndep>
##
## To use it, access: 
## 
##   http://localhost:8080/departments/10
##

@app.route("/departments/<ndep>", methods=['GET'])
def get_department(ndep):
    logger.info("###              DEMO: GET /departments/<ndep>              ###");   

    logger.debug(f'ndep: {ndep}')

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT ndep, nome, local FROM dep where ndep = %s", (ndep,) )
    rows = cur.fetchall()

    row = rows[0]

    logger.debug("---- selected department  ----")
    logger.debug(row)
    content = {'ndep': int(row[0]), 'nome': row[1], 'localidade': row[2]}

    conn.close ()
    return jsonify(content)



##
##      Demo POST
##
## Add a new department in a JSON payload
##
## To use it, you need to use postman or curl: 
##
##   curl -X POST http://localhost:8080/departments/ -H "Content-Type: application/json" -d '{"localidade": "Polo II", "ndep": 69, "nome": "Seguranca"}'
##


def execute_query(query):
    conn = db_connection()
    cur = conn.cursor()

    cur.execute(query)
    # cur.execute("SELECT id_user, username, email, password FROM user_ where username like :username", {"search": "%" + username + "%"})
    rows = cur.fetchall()

    row = rows[0]

    logger.debug("---- selected user  ----")
    logger.debug(row)

    result = []
    content ={'id': row[0],'username': row[1], 'email': row[2], 'password': row[3]}
    # for x in rows:
    #     result.append()

    conn.close ()

@app.route("/users/<username>", methods=['GET'])
def get_user(username):
    logger.info("###              DEMO: GET /users/<username>              ###");   

    logger.debug(f'ndep: {username}')

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id_user, username, email, password FROM user_ where username = %s", (username,) )
    # cur.execute("SELECT id_user, username, email, password FROM user_ where username like :username", {"search": "%" + username + "%"})
    rows = cur.fetchall()

    row = rows[0]

    logger.debug("---- selected user  ----")
    logger.debug(row)

    result = []
    content ={'id': row[0],'username': row[1], 'email': row[2], 'password': row[3]}
    # for x in rows:
    #     result.append()

    conn.close ()
    return jsonify(content)


@app.route("/departments/", methods=['POST'])
# def add_departments():
#     logger.info("###              DEMO: POST /departments              ###");
#     payload = request.get_json()

#     conn = db_connection()
#     cur = conn.cursor()

#     logger.info("---- new department  ----")
#     logger.debug(f'payload: {payload}')

#     # parameterized queries, good for security and performance
#     statement = """
#                   INSERT INTO dep (ndep, nome, local) 
#                           VALUES ( %s,   %s ,   %s )"""

#     values = (payload["ndep"], payload["localidade"], payload["nome"])

#     try:
#         cur.execute(statement, values)
#         cur.execute("commit")
#         result = 'Inserted!'
#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(error)
#         result = 'Failed!'
#     finally:
#         if conn is not None:
#             conn.close()

#     return jsonify(result)




##
##      Demo PUT
##
## Update a department based on the a JSON payload
##
## To use it, you need to use postman or curl: 
##
##   curl -X PUT http://localhost:8080/departments/ -H "Content-Type: application/json" -d '{"ndep": 69, "localidade": "Porto"}'
##

@app.route("/departments/", methods=['PUT'])
def update_departments():
    logger.info("###              DEMO: PUT /departments              ###");   
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()


    #if content["ndep"] is None or content["nome"] is None :
    #    return 'ndep and nome are required to update'

    if "ndep" not in content or "localidade" not in content:
        return 'ndep and localidade are required to update'


    logger.info("---- update department  ----")
    logger.info(f'content: {content}')

    # parameterized queries, good for security and performance
    statement ="""
                UPDATE dep 
                  SET local = %s
                WHERE ndep = %s"""


    values = (content["localidade"], content["ndep"])

    try:
        res = cur.execute(statement, values)
        result = f'Updated: {cur.rowcount}'
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)







##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    # NOTE: change the host to "db" if you are running as a Docker container
    db = psycopg2.connect(user = "SGD_project",
                            password = "5432",
                            host = "localhost", #"db",
                            port = "5433",
                            database = "cloud_query")
    return db


##########################################################
## MAIN
##########################################################
if __name__ == "__main__":

    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
                              '%H:%M:%S')
                              # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    time.sleep(1) # just to let the DB start before this print :-)


    logger.info("\n---------------------------------------------------------------\n" + 
                  "API v1.0 online: http://localhost:8080/cloud-query/\n\n")


    
    # NOTE: change to 5000 or remove the port parameter if you are running as a Docker container
    app.run(host="0.0.0.0", port=8080, debug=True, threaded=True)



