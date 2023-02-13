--DROP INDEX ix_mail_reports_party_id;
--DROP INDEX ix_mail_reports_registration_id;
--DROP INDEX ix_mail_reports_create_ts;
--DROP TABLE public.mail_reports;
--DROP SEQUENCE mail_report_id_seq;
CREATE SEQUENCE mail_report_id_seq INCREMENT 1 START 1;
CREATE TABLE public.mail_reports (
  id INTEGER PRIMARY KEY,
  create_ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  registration_id INTEGER NOT NULL,
  party_id INTEGER NOT NULL,
  report_data JSON NOT NULL,
  doc_storage_url VARCHAR (1000) NULL,
  retry_count INTEGER NULL,
  status INTEGER NULL,
  message VARCHAR(2000) NULL,
  FOREIGN KEY (registration_id)
      REFERENCES registrations (id),
  FOREIGN KEY (party_id)
      REFERENCES parties (id)
);
CREATE INDEX ix_mail_reports_create_ts ON public.mail_reports USING btree (create_ts);
CREATE INDEX ix_mail_reports_registration_id ON public.mail_reports USING btree (registration_id);
CREATE INDEX ix_mail_reports_party_id ON public.mail_reports USING btree (party_id);
