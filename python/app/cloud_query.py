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
from _datetime import datetime

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

def seat_generator(num_seats):

    # Seat creation considerations:
    # letters are COLUMS and numbers are ROWS
    # Display of a plane:
    """
    [1A,1B,3C,4D,5E
     2A,2B,3C,4D,5E
          ...
     nA,nB,nC,nD,nE]
    """
    # For simplification, we consider that every plane has 5 colums
    # and not every row is completed.

    num_colums = 5
    num_rows = num_seats//num_colums
    # Number of seats without a complete row
    num_seat_inc = num_seats%num_colums

    seats = []
    Alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','W','X','Y','Z']

    for i in range(num_rows):
        for lseat1 in range(num_colums):
            letter = Alphabet[lseat1]
            seats.append(str(i+1)+letter)

    if num_seat_inc != 0:
        number = i + 2
        itr = 0
        while itr < num_seat_inc:
            letter = Alphabet[itr]
            seats.append(str(number)+letter)
            itr += 1

    return seats
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
                  INSERT INTO passanger (user__id_user) 
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
}'''
@app.route('/cloud-query/crew_member', methods=['POST'])
def add_crew_member():
    logger.info("###              DEMO: POST /crew_member              ###");
    payload_admin = verify_admin()
    if isinstance(payload_admin, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload_admin

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
                          INSERT INTO crew_members (user__id_user,admin__user__id_user) 
                                  VALUES ( %s , %s)"""
        values_1 = (row[0],payload_admin['id'])
        if payload['role'] == 'pilot':
            statement_2 = """
            INSERT INTO pilot (crew_crew_id, crew_members_user__id_user) VALUES ( %s , %s)"""
            values_2 = (crew_row[0], row[0])
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
    values = (payload['id'],airport_json['city'],airport_json['name'],airport_json['country'])
    statement2="""
    SELECT (airport_code) FROM airport_ WHERE  (city = %s AND name = %s AND country= %s )
    """
    values2 = (airport_json['city'],airport_json['name'],airport_json['country'])
    try:
        cur.execute(statement, values)
        cur.execute(statement2, values2)
        row = cur.fetchone()
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result': row[0]})

@app.route('/cloud-query/flight', methods=['POST'])
def add_flight():
    logger.info("###              DEMO: POST /flight             ###")
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload
    conn = db_connection()
    cur = conn.cursor()
    flight_json = request.get_json()
    logger.info("---- new flight  ----")
    logger.debug(f'payload: {payload}')
    statement = """
                                      INSERT INTO flight_(departure_time,arrival_time,existing_seats,admin__user__id_user,airport_dep,airport_arr) 
                                      VALUES (%s, %s, %s, %s, %s, %s )
                                      """
    values = (datetime.strptime(flight_json['departure_time'],"%H:%M").time(),datetime.strptime(flight_json['arrival_time'],"%H:%M").time(),flight_json['existing_seats'],payload['id'],flight_json['airport_dep'],flight_json['airport_arr'])
    statement2 = """
        SELECT (flight_code) FROM flight_ WHERE departure_time=%s AND arrival_time=%s AND existing_seats=%s AND airport_dep=%s AND airport_arr=%s
        """
    values2 = (datetime.strptime(flight_json['departure_time'],"%H:%M").time(),datetime.strptime(flight_json['arrival_time'],"%H:%M").time(),flight_json['existing_seats'],flight_json['airport_dep'],flight_json['airport_arr'])
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

@app.route('/cloud-query/schedule', methods=['POST'])
def add_schedule():
    logger.info("###              DEMO: POST /schedule             ###")
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    conn = db_connection()
    cur = conn.cursor()
    sch_json = request.get_json()
    logger.info("---- new schedule  ----")
    logger.debug(f'payload: {payload}')

    sta= '''
    SELECT flight_date 
    FROM schedule_
    WHERE flight_date= %s
    '''

    values = (datetime.strptime(sch_json['date'],"%Y-%m-%d"),)
    cur.execute(sta, values)
    if cur.rowcount == 0:
        sta='''
        INSERT INTO schedule_ (flight_date)
        VALUES (%s)
        '''
        data=datetime.strptime(sch_json['date'], "%Y-%m-%d").date()
        values = (data,)
        cur.execute(sta, values)

    sta='''
    INSERT INTO  flight__schedule_(flight__flight_code, schedule__flight_date, crew_crew_id, ticket_price, admin__user__id_user) 
            VALUES (%s, %s, %s, %s, %s)
    '''
    val=(sch_json['flight_code'],datetime.strptime(sch_json['date'], "%Y-%m-%d"),sch_json['crew_id'],sch_json['ticket_price'],payload['id'])

    query_seats='''
    SELECT existing_seats 
    FROM flight_
    WHERE flight_code= %s
    '''

    sta2='''
        INSERT INTO seat(available, seat_number, schedule__flight_date, flight__flight_code) 
        VALUES (%s,%s,%s,%s) 
    '''

    try:
        cur.execute(sta, val)
        cur.execute(query_seats,( sch_json['flight_code'],))
        seat_n = cur.fetchone()[0]
        for i in seat_generator(seat_n):
            val2=(bool(True),i,data,sch_json['flight_code'])
            cur.execute(sta2, val2)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result':'Inserido com sucesso!'})



@app.route('/cloud-query/all_routes', methods=['GET'])
def get_all_routes():
    logger.info("###              DEMO: GET /all_routes            ###")

    conn = db_connection()
    cur = conn.cursor()

    sta="""

SELECT 
    f.airport_dep AS origin_airport,
    f.airport_arr AS destination_airport,
    f.flight_code,
    s.flight_date AS schedule
    
FROM 
    flight_ f
JOIN 
    flight__schedule_ fs ON f.flight_code = fs.flight__flight_code
JOIN 
    schedule_ s ON fs.schedule__flight_date = s.flight_date
ORDER BY
    f.flight_code;


"""
    cur.execute(sta)
    rows = cur.fetchall()

    grouped_results = {}
    for row in rows:
        key = (row[0], row[1], row[2])
        if key not in grouped_results:
            grouped_results[key] = {"schedules": []}
        grouped_results[key]["schedules"].append(row[3].strftime("%d/%m/%Y"))

    # Convert to desired format
    formatted_results = []
    for key, value in grouped_results.items():
        formatted_results.append({
            "origin_airport": key[0],
            "destination_airport": key[1],
            "flight_code": key[2],
            "schedules": value["schedules"],
        })

    return jsonify({'status': 200, 'result': formatted_results})


@app.route('/cloud-query/all_routes/origin', methods=['GET'])
def get_all_routes_origin():
    logger.info("###              DEMO: GET /all_routes            ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    sta = """
SELECT 
    f.airport_dep AS origin_airport,
    f.airport_arr AS destination_airport,
    f.flight_code,
    s.flight_date AS schedule
FROM 
    flight_ f
JOIN 
    flight__schedule_ fs ON f.flight_code = fs.flight__flight_code
JOIN 
    schedule_ s ON fs.schedule__flight_date = s.flight_date
WHERE 
    f.airport_dep = %s
ORDER BY
    f.flight_code;

"""

    cur.execute(sta, (payload['origin_airport'],))
    rows = cur.fetchall()

    grouped_results = {}
    for row in rows:
        key = (row[0], row[1], row[2])
        if key not in grouped_results:
            grouped_results[key] = {"schedules": []}
        grouped_results[key]["schedules"].append(row[3].strftime("%d/%m/%Y"))

    # Convert to desired format
    formatted_results = []
    for key, value in grouped_results.items():
        formatted_results.append({
            "origin_airport": key[0],
            "destination_airport": key[1],
            "flight_code": key[2],
            "schedules": value["schedules"],
        })

    return jsonify({'status': 200, 'result': formatted_results})

@app.route('/cloud-query/all_routes/destination', methods=['GET'])
def get_all_routes_destination():
    logger.info("###              DEMO: GET /all_routes            ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    sta = """
SELECT 
    f.airport_dep AS origin_airport,
    f.airport_arr AS destination_airport,
    f.flight_code,
    s.flight_date AS schedule
FROM 
    flight_ f
JOIN 
    flight__schedule_ fs ON f.flight_code = fs.flight__flight_code
JOIN 
    schedule_ s ON fs.schedule__flight_date = s.flight_date
WHERE 
    f.airport_arr = %s
ORDER BY
    f.flight_code;

"""

    cur.execute(sta, (payload['destination_airport'],))
    rows = cur.fetchall()

    grouped_results = {}
    for row in rows:
        key = (row[0], row[1], row[2])
        if key not in grouped_results:
            grouped_results[key] = {"schedules": []}
        grouped_results[key]["schedules"].append(row[3].strftime("%d/%m/%Y"))

    # Convert to desired format
    formatted_results = []
    for key, value in grouped_results.items():
        formatted_results.append({
            "origin_airport": key[0],
            "destination_airport": key[1],
            "flight_code": key[2],
            "schedules": value["schedules"],
        })

    return jsonify({'status': 200, 'result': formatted_results})

@app.route('/cloud-query/all_routes/origin&destination', methods=['GET'])
def get_all_routes_origin_destination():
    logger.info("###              DEMO: GET /all_routes            ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    sta ="""
SELECT 
    f.airport_dep AS origin_airport,
    f.airport_arr AS destination_airport,
    f.flight_code,
    s.flight_date AS schedule
FROM 
    flight_ f
JOIN 
    flight__schedule_ fs ON f.flight_code = fs.flight__flight_code
JOIN 
    schedule_ s ON fs.schedule__flight_date = s.flight_date
WHERE 
    f.airport_dep = %s
    AND
    f.airport_arr = %
ORDER BY
    f.flight_code;

"""

    cur.execute(sta, (payload['origin_airport'],['destination_airport']))
    rows = cur.fetchall()

    grouped_results = {}
    for row in rows:
        key = (row[0], row[1], row[2])
        if key not in grouped_results:
            grouped_results[key] = {"schedules": []}
        grouped_results[key]["schedules"].append(row[3].strftime("%d/%m/%Y"))

    # Convert to desired format
    formatted_results = []
    for key, value in grouped_results.items():
        formatted_results.append({
            "origin_airport": key[0],
            "destination_airport": key[1],
            "flight_code": key[2],
            "schedules": value["schedules"],
        })

    return jsonify({'status': 200, 'result': formatted_results})



@app.route('/cloud-query/seats', methods=['GET'])
def check_seats():
    logger.info("###              DEMO: GET /check_seats           ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    sta ="""
SELECT 
    seat_number
FROM 
    seat
WHERE 
    flight__flight_code = %s
    AND schedule__flight_date = %s
    AND available = TRUE;

"""
    val=(payload['flight_code'],payload['date'])
    cur.execute(sta, val)

    rows = cur.fetchall()
    seat_numbers = [row[0] for row in rows]

    return jsonify({'status': 200, 'result': seat_numbers})

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



