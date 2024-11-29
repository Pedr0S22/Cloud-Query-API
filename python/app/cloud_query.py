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
        if token.startswith("Bearer "): #Tenho de trocar isto para JWT token ver chatgpt
            token = token[7:]

        payload = jwt.decode(token, password_token, algorithms=["HS256"])

        if payload["exp"] < time.time():
            return jsonify({"message": "Token expirado!"}), 401

        return payload

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expirado!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Token inválido!"}), 401

def verify_admin():
    payload = verify_token()
    if isinstance(payload, tuple):
        return payload
    conn = db_connection()
    cur = conn.cursor()
    id_admin = payload['id']
    cur.execute("SELECT * FROM admin_ WHERE  user__id_user= %s", (id_admin,))
    row = cur.fetchone()

    if row:
        return payload
    else:
        return jsonify({"message": f"Acesso restrito a admistrador!"}), 403
def verify_crew():
    payload = verify_token()
    if isinstance(payload, tuple):
        return payload
    conn = db_connection()
    cur = conn.cursor()
    id_admin = payload['id']
    cur.execute("SELECT * FROM crew_members WHERE  user__id_user= %s", (id_admin,))
    row = cur.fetchone()

    if row:
        return payload
    else:
        return jsonify({"message": f"Acesso restrito a admistrador!"}), 403
def verify_passenger():
    payload = verify_token()
    if isinstance(payload, tuple):
        return payload
    conn = db_connection()
    cur = conn.cursor()
    id_admin = payload['id']
    cur.execute("SELECT * FROM passenger WHERE  user__id_user= %s", (id_admin,))
    row = cur.fetchone()

    if row:
        return payload
    else:
        return jsonify({"message": f"Acesso restrito a admistrador!"}), 403
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

def add_users():
    logger.info("###              DEMO: POST /users              ###");
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- new user  ----")
    logger.debug(f'payload: {payload}')
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

@app.route('/cloud-query/passenger', methods=['POST'])
def add_passenger():
    logger.info("###              DEMO: POST /passenger              ###");

    conn = db_connection()
    cur = conn.cursor()
    add_users()
    payload = request.get_json()
    logger.info("---- new passenger  ----")
    logger.debug(f'payload: {payload}')

    cur.execute("SELECT * FROM user_ where username = %s", (payload['username'],))
    rows = cur.fetchall()
    if len(rows) == 0:
        return jsonify({'status': 401, 'errors': 'Username does not exist!'}), 401

    row = rows[0]
    statement = """
                  INSERT INTO passenger (user__id_user) 
                          VALUES ( %s )"""
    values = (row[0],)
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
@app.route('/cloud-query/admin', methods=['POST'])
def add_admin():
    logger.info("###              DEMO: POST /admin              ###");
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    conn = db_connection()
    cur = conn.cursor()
    add_users()
    payload = request.get_json()
    logger.info("---- new admin  ----")
    logger.debug(f'payload: {payload}')

    cur.execute("SELECT * FROM user_ where username = %s", (payload['username'],))
    rows = cur.fetchall()
    if len(rows) == 0:
        return jsonify({'status': 401, 'errors': 'Username does not exist!'}), 401

    row = rows[0]
    statement = """
                  INSERT INTO admin_ (user__id_user) 
                          VALUES ( %s )"""
    values = (row[0],)
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
#Adicionar crew_members
'''{
    "username": "mario.geraldes.admin",
    "email": "mario.geraldes.admin@admin.pt",
    "password": "123adminmario",
    "role": "pilot",
    "crew_id": 1
}'''#Exemplo de JSON
@app.route('/cloud-query/crew_member', methods=['POST'])
def add_crew_member():
    logger.info("###              DEMO: POST /crew_member              ###");
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    conn = db_connection()
    cur = conn.cursor()
    add_users()
    payload = request.get_json()
    logger.info("---- new crew_member  ----")
    logger.debug(f'payload: {payload}')

    cur.execute("SELECT * FROM user_ where username = %s", (payload['username'],))
    row = cur.fetchone()
    if len(row) == 0:
        return jsonify({'status': 401, 'errors': 'Username does not exist!'}), 401
    cur.execute("SELECT crew_id FROM crew where crew_id = %s", (payload['crew_id'],))
    crew_row = cur.fetchone()
    if crew_row:
        statement_1 = """
                          INSERT INTO crew_members (user__id_user) 
                                  VALUES ( %s )"""
        values_1 = (row[0],)
        if payload['role'] == 'pilot':
            statement_2 = """
            INSERT INTO pilot (crew_crew_id, crew_members_user__id_user) VALUES ( %s , %s)"""
            values_2 = (row[0], row[1])  # Vou ter de mudar a cena da crew
        elif payload['role'] == 'flight_attendante':
            statement_2 = """INSERT INTO flight_attendante (crew_crew_id, crew_members_user__id_user) VALUES ( %s , %s)"""
            values_2 = (row[0], row[1])  # Vou ter de mudar a cena da crew

        try:
            cur.execute(statement_1, values_1)
            cur.execute(statement_2, values_2)
            cur.execute("commit")
            result = 'Inserted!'
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            result = 'Failed!'
        finally:
            if conn is not None:
                conn.close()
        return jsonify(result)
    else:
        return jsonify({'status': 401, 'errors': 'Crew id does not exist!'}), 401

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



