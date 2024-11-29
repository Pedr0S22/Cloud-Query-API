/* 
	# 
	# Sistema de Gestão de Dados 2024/2025
	# Trabalho Prático
	#
*/


/* 
   Fazer copy-paste deste ficheiro
   para o Editor SQL e executar.
*/

/* 
Estes dois comandos drop (comentados) permitem remover as tabelas emp e dep da base de dados (se ja' tiverem sido criadas anteriormente)

drop table emp;
drop table dep;
*/

CREATE TABLE user_ (
	id_user	 BIGSERIAL,
	username VARCHAR(512) NOT NULL,
	email	 VARCHAR(512) NOT NULL,
	password VARCHAR(512) NOT NULL,
	PRIMARY KEY(id_user)
);

CREATE TABLE admin_ (
	user__id_user BIGINT,
	PRIMARY KEY(user__id_user)
);

CREATE TABLE airport_ (
	airport_code	 BIGSERIAL,
	city		 VARCHAR(512) NOT NULL,
	name		 VARCHAR(512) NOT NULL,
	country		 VARCHAR(512) NOT NULL,
	admin__user__id_user BIGINT NOT NULL,
	PRIMARY KEY(airport_code)
);

CREATE TABLE crew (
	crew_id			 BIGSERIAL,
	admin__user__id_user	 BIGINT NOT NULL,
	crew_members_user__id_user BIGINT NOT NULL,
	PRIMARY KEY(crew_id)
);

CREATE TABLE passenger (
	user__id_user BIGINT,
	PRIMARY KEY(user__id_user)
);

CREATE TABLE flight_ (
	flight_code		 BIGSERIAL,
	departure_time	 TIMESTAMP NOT NULL,
	arrival_time		 TIMESTAMP NOT NULL,
	existing_seats	 BIGINT NOT NULL,
	admin__user__id_user	 BIGINT NOT NULL,
	airport__airport_code	 BIGINT NOT NULL,
	airport__airport_code1 BIGINT NOT NULL,
	PRIMARY KEY(flight_code)
);

CREATE TABLE schedule_ (
	schedule_id		 BIGSERIAL,
	flight_date		 DATE NOT NULL,
	price_ticket	 DOUBLE PRECISION NOT NULL,
	admin__user__id_user BIGINT NOT NULL,
	crew_crew_id	 BIGINT NOT NULL,
	flight__flight_code	 BIGINT NOT NULL,
	PRIMARY KEY(schedule_id)
);

CREATE TABLE ticket_ (
	name			 VARCHAR(512) NOT NULL,
	vat			 VARCHAR(512),
	payment_booking_payment_id BIGINT,
	seat_schedule__schedule_id BIGINT NOT NULL,
	PRIMARY KEY(payment_booking_payment_id,vat)
);

CREATE TABLE payment_booking (
	payment_id		 BIGSERIAL,
	amount			 FLOAT(8) NOT NULL,
	payment_date		 TIMESTAMP NOT NULL,
	booking_booking_id	 BIGSERIAL NOT NULL,
	booking_ticket_quantity INTEGER NOT NULL,
	schedule__schedule_id	 BIGINT NOT NULL,
	PRIMARY KEY(payment_id)
);

CREATE TABLE payment_method (
	method			 VARCHAR(512) NOT NULL,
	percent			 INTEGER NOT NULL,
	payment_booking_payment_id BIGINT,
	PRIMARY KEY(payment_booking_payment_id,method)
);

CREATE TABLE seat (
	available		 BOOL NOT NULL,
	schedule__schedule_id BIGINT,
	PRIMARY KEY(schedule__schedule_id)
);

CREATE TABLE crew_members (
	user__id_user BIGINT,
	PRIMARY KEY(user__id_user)
);

CREATE TABLE flight_attendante (
	crew_crew_id		 BIGINT NOT NULL,
	crew_members_user__id_user BIGINT,
	PRIMARY KEY(crew_members_user__id_user)
);

CREATE TABLE pilot (
	crew_crew_id		 BIGINT NOT NULL,
	crew_members_user__id_user BIGINT,
	PRIMARY KEY(crew_members_user__id_user)
);

CREATE TABLE passenger_payment_booking (
	passenger_user__id_user	 BIGINT,
	payment_booking_payment_id BIGINT,
	PRIMARY KEY(passenger_user__id_user,payment_booking_payment_id)
);

ALTER TABLE user_ ADD UNIQUE (username, email);
ALTER TABLE admin_ ADD CONSTRAINT admin__fk1 FOREIGN KEY (user__id_user) REFERENCES user_(id_user);
ALTER TABLE airport_ ADD CONSTRAINT airport__fk1 FOREIGN KEY (admin__user__id_user) REFERENCES admin_(user__id_user);
ALTER TABLE crew ADD CONSTRAINT crew_fk1 FOREIGN KEY (admin__user__id_user) REFERENCES admin_(user__id_user);
ALTER TABLE crew ADD CONSTRAINT crew_fk2 FOREIGN KEY (crew_members_user__id_user) REFERENCES crew_members(user__id_user);
ALTER TABLE passenger ADD CONSTRAINT passenger_fk1 FOREIGN KEY (user__id_user) REFERENCES user_(id_user);
ALTER TABLE flight_ ADD CONSTRAINT flight__fk1 FOREIGN KEY (admin__user__id_user) REFERENCES admin_(user__id_user);
ALTER TABLE flight_ ADD CONSTRAINT flight__fk2 FOREIGN KEY (airport__airport_code) REFERENCES airport_(airport_code);
ALTER TABLE flight_ ADD CONSTRAINT flight__fk3 FOREIGN KEY (airport__airport_code1) REFERENCES airport_(airport_code);
ALTER TABLE schedule_ ADD CONSTRAINT schedule__fk1 FOREIGN KEY (admin__user__id_user) REFERENCES admin_(user__id_user);
ALTER TABLE schedule_ ADD CONSTRAINT schedule__fk2 FOREIGN KEY (crew_crew_id) REFERENCES crew(crew_id);
ALTER TABLE schedule_ ADD CONSTRAINT schedule__fk3 FOREIGN KEY (flight__flight_code) REFERENCES flight_(flight_code);
ALTER TABLE ticket_ ADD UNIQUE (seat_schedule__schedule_id);
ALTER TABLE ticket_ ADD CONSTRAINT ticket__fk1 FOREIGN KEY (payment_booking_payment_id) REFERENCES payment_booking(payment_id);
ALTER TABLE ticket_ ADD CONSTRAINT ticket__fk2 FOREIGN KEY (seat_schedule__schedule_id) REFERENCES seat(schedule__schedule_id);
ALTER TABLE ticket_ ADD CONSTRAINT constraint_0 CHECK (CHECK (LENGTH(vat) = 9));
ALTER TABLE payment_booking ADD UNIQUE (booking_booking_id);
ALTER TABLE payment_booking ADD CONSTRAINT payment_booking_fk1 FOREIGN KEY (schedule__schedule_id) REFERENCES schedule_(schedule_id);
ALTER TABLE payment_method ADD CONSTRAINT payment_method_fk1 FOREIGN KEY (payment_booking_payment_id) REFERENCES payment_booking(payment_id);
ALTER TABLE payment_method ADD CONSTRAINT constraint_0 CHECK (method in ("MBWay","Credit Card","Multibanco reference"));
ALTER TABLE seat ADD CONSTRAINT seat_fk1 FOREIGN KEY (schedule__schedule_id) REFERENCES schedule_(schedule_id);
ALTER TABLE crew_members ADD CONSTRAINT crew_members_fk1 FOREIGN KEY (user__id_user) REFERENCES user_(id_user);
ALTER TABLE flight_attendante ADD CONSTRAINT flight_attendante_fk1 FOREIGN KEY (crew_crew_id) REFERENCES crew(crew_id);
ALTER TABLE flight_attendante ADD CONSTRAINT flight_attendante_fk2 FOREIGN KEY (crew_members_user__id_user) REFERENCES crew_members(user__id_user);
ALTER TABLE pilot ADD CONSTRAINT pilot_fk1 FOREIGN KEY (crew_crew_id) REFERENCES crew(crew_id);
ALTER TABLE pilot ADD CONSTRAINT pilot_fk2 FOREIGN KEY (crew_members_user__id_user) REFERENCES crew_members(user__id_user);
ALTER TABLE passenger_payment_booking ADD CONSTRAINT passenger_payment_booking_fk1 FOREIGN KEY (passenger_user__id_user) REFERENCES passenger(user__id_user);
ALTER TABLE passenger_payment_booking ADD CONSTRAINT passenger_payment_booking_fk2 FOREIGN KEY (payment_booking_payment_id) REFERENCES payment_booking(payment_id);


/* 
   Fazer copy-paste deste ficheiro
   para o SQL Editor do PgAdmin e executar (F5).
*/

/* Insere os departamentos
 */
-- INSERT INTO dep VALUES (10, 'Contabilidade', 'Condeixa');
-- INSERT INTO dep VALUES (20, 'Investigacao',  'Mealhada');
-- INSERT INTO dep VALUES (30, 'Vendas',        'Coimbra');
-- INSERT INTO dep VALUES (40, 'Planeamento',   'Montemor');



/* Insere os empregrados
 * Note-se  que  como  existe a  restricao  de  o  numero
 * do encarregado ser uma chave estrangeira (que por acaso
 * aponta  para a  chave primaria  da  mesma  tabela)  os 
 * empregados  teem  que  ser  inseridos na  ordem certa.
 * Primeiro o presidente (que nao tem superiores)  depois
 * os empregados cujo encarregado e' o presidente e assim
 * sucessivamente.
 * 
 */
