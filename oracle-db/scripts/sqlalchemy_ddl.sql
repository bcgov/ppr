CREATE TABLE transaction (
    issued_at timestamp,
    id INTEGER NOT NULL,
    remote_addr VARCHAR2(50)
);

CREATE SEQUENCE transaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE;
