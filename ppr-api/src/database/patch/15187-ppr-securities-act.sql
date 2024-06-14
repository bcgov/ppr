-- 15178 begin release 1.2.5
INSERT INTO registration_types(registration_type, registration_type_cl, registration_desc, registration_act) VALUES
('SE', 'MISCLIEN', 'SECURITIES ORDER OR PROCEEDING', 'MISCELLANEOUS REGISTRATIONS ACT');

ALTER TABLE account_bcol_ids
  ADD COLUMN securities_act_ind VARCHAR(1) NULL CHECK (securities_act_ind IN ('Y', 'N'));

CREATE TYPE public.securities_act_type AS ENUM ('LIEN', 'PRESERVATION', 'PROCEEDINGS');
CREATE TABLE public.securities_act_types (
  securities_act_type public.securities_act_type PRIMARY KEY,
  securities_act_type_desc VARCHAR (100) NOT NULL
);
INSERT INTO securities_act_types(securities_act_type, securities_act_type_desc) VALUES
('LIEN', 'NOTICE OF LIEN AND CHARGE'),
('PRESERVATION', 'PRESERVATION ORDER'),
('PROCEEDINGS', 'NOTICE OF ORDER OR PROCEEDINGS')
;

CREATE SEQUENCE securities_act_notice_id_seq INCREMENT 1 START 1;
CREATE TABLE public.securities_act_notices (
  id INTEGER PRIMARY KEY,
  registration_id INTEGER NOT NULL,  
  registration_id_end INTEGER NULL,  
  securities_act_type public.securities_act_type NOT NULL,
  effective_ts TIMESTAMP NULL,
  detail_description VARCHAR (4000) NULL,
  previous_notice_id INTEGER NULL,
  FOREIGN KEY (securities_act_type)
      REFERENCES securities_act_types (securities_act_type),
  FOREIGN KEY (registration_id)
      REFERENCES registrations (id),
  FOREIGN KEY (registration_id_end)
      REFERENCES registrations (id)
);
CREATE INDEX ix_sec_notices_registration_id ON public.securities_act_notices USING btree (registration_id);
CREATE INDEX ix_sec_notices_change_registration_id ON public.securities_act_notices USING btree (registration_id_end);

CREATE SEQUENCE securities_act_order_id_seq INCREMENT 1 START 1;
CREATE TABLE public.securities_act_orders (
  id INTEGER PRIMARY KEY,
  registration_id INTEGER NOT NULL,  
  securities_act_notice_id INTEGER NOT NULL,  
  court_order_ind VARCHAR (1) NOT NULL CHECK (court_order_ind IN ('Y', 'N')),
  registration_id_end INTEGER NULL,  
  order_date TIMESTAMP NOT NULL,
  court_name VARCHAR (256) NULL,
  court_registry VARCHAR (64) NULL,
  file_number VARCHAR (20) NULL,
  effect_of_order VARCHAR (512) NULL,
  previous_order_id INTEGER NULL,
  FOREIGN KEY (securities_act_notice_id)
      REFERENCES securities_act_notices (id),
  FOREIGN KEY (registration_id)
      REFERENCES registrations (id),
  FOREIGN KEY (registration_id_end)
      REFERENCES registrations (id)
);
CREATE INDEX ix_sec_orders_sec_id ON public.securities_act_orders USING btree (securities_act_notice_id);
CREATE INDEX ix_sec_orders_registration_id ON public.securities_act_orders USING btree (registration_id);
CREATE INDEX ix_sec_orders_change_registration_id ON public.securities_act_orders USING btree (registration_id_end);

INSERT INTO registration_types(registration_type, registration_type_cl, registration_desc, registration_act) VALUES 
('A1', 'AMENDMENT', 'AMENDMENT - NOTICE ADDED', 'SECURITIES ACT'),
('A2', 'AMENDMENT', 'AMENDMENT - NOTICE REMOVED', 'SECURITIES ACT'),
('A3', 'AMENDMENT', 'AMENDMENT - NOTICE AMENDED', 'SECURITIES ACT')
;
-- 15178 end release 1.2.5
