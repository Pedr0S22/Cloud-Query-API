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
    id = payload['id']
    cur.execute("SELECT * FROM crew_members WHERE  user__id_user= %s", (id,))
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
    id = payload['id']
    cur.execute("SELECT * FROM passenger WHERE  user__id_user= %s", (id,))
    row = cur.fetchone()

    if row:
        return payload
    else:
        return jsonify({"message": f"Acesso restrito a passageiro!"}), 403
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
    logger.info("###              DEMO: POST /passenger              ###")

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
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result':row[0] })

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
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result':row[0] })
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
            values_2 = (row[0], crew_row[0])
        elif payload['role'] == 'flight_attendante':
            statement_2 = """INSERT INTO flight_attendante (crew_crew_id, crew_members_user__id_user) VALUES ( %s , %s)"""
            values_2 = (payload['crew_id'], crew_row[0])

        try:
            cur.execute(statement_1, values_1)
            cur.execute(statement_2, values_2)
            cur.execute("commit")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            if conn is not None:
                conn.close()
        return jsonify({'status': 200, 'result': row[0]})
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

@app.route('/cloud-query/crew', methods=['POST'])
def add_crew():
    logger.info("###              DEMO: POST /crew              ###")
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    conn = db_connection()
    cur = conn.cursor()
    logger.info("---- new crew  ----")
    logger.debug(f'payload: {payload}')
    statement = """
                              INSERT INTO crew (admin__user__id_user) 
                                      VALUES ( %s )"""
    values = (payload['id'],)
    try:
        cur.execute(statement, values)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result':'Inserido com sucesso!' })

@app.route('/cloud-query/crew', methods=['GET'])
def get_crews():
    logger.info("###              DEMO: GET /crew             ###")

    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM crew")
    rows = cur.fetchall()

    payload = []
    logger.debug("---- departments  ----")
    for row in rows:
        logger.debug(row)
        content = {'crew_id': int(row[0]), 'administrador_creater': row[1], 'crew_chief': row[2]}
        payload.append(content) # appending to the payload to be returned

    conn.close()
    return jsonify(payload)

@app.route('/cloud-query/airport', methods=['POST'])
def add_airport():
    logger.info("###              DEMO: POST /airport              ###")
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    conn = db_connection()
    cur = conn.cursor()
    airport_json = request.get_json()
    logger.info("---- new airport  ----")
    logger.debug(f'payload: {payload}')
    statement = """
                                  INSERT INTO airport_ (admin__user__id_user, city,name, country) 
                                          VALUES ( %s,%s,%s,%s)"""
    values = (payload['id'],airport_json['name'],airport_json['country'],airport_json['city'])
    statement2="""
    SELECT (airport_code) FROM airport WHERE admin__user__id_user = %s AND city = %s AND name = %s
    """
    values2 = (payload['id'],airport_json['name'],airport_json['country'])
    try:
        cur.execute(statement, values)
        cur.execute(statement2, values2)
        rows = cur.fetchone()
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result':rows[0]})

@app.route('/cloud-query/flight', methods=['POST'])
def add_flight():
    logger.info("###              DEMO: POST /flight             ###")
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload
    conn = db_connection()
    cur = conn.cursor()
    flight_json = request.get_json()
    logger.info("---- new airport  ----")
    logger.debug(f'payload: {payload}')
    statement = """
                                      INSERT INTO flight_ (admin__user__id_user, departu) 
                                              VALUES ( %s,%s,%s,%s)"""
    values = ()
    statement2 = """
        SELECT (airport_code) FROM airport WHERE admin__user__id_user = %s AND city = %s AND name = %s
        """
    values2 = ()
    try:
        cur.execute(statement, values)
        cur.execute(statement2, values2)
        rows = cur.fetchone()
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result': rows[0]})


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



