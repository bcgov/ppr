-- Script to create PPR sequences.

-- registration number sequence
CREATE SEQUENCE registration_num_seq INCREMENT BY 1 START WITH 200000;
-- draft document number sequence
CREATE SEQUENCE document_num_seq INCREMENT BY 1 START WITH 100000;

-- draft table PK draft_id sequence
CREATE SEQUENCE draft_id_seq INCREMENT BY 1 START WITH 1;
-- registration table PK registration_id sequence
CREATE SEQUENCE registration_id_seq INCREMENT BY 1 START WITH 1;
-- financing_statement table PK financing_id Psequence
CREATE SEQUENCE financing_id_seq INCREMENT BY 1 START WITH 1;
-- address table PK address_id sequence
CREATE SEQUENCE address_id_seq INCREMENT BY 1 START WITH 1;
-- party table PK party_id Psequence
CREATE SEQUENCE party_id_seq INCREMENT BY 1 START WITH 1;
-- client_party table PK client_party_id sequence
CREATE SEQUENCE client_party_id_seq INCREMENT BY 1 START WITH 1;
-- serial_collateral table PK serial_collateral_id sequence
CREATE SEQUENCE serial_collateral_id_seq INCREMENT BY 1 START WITH 1;
-- general_collateral table PK general_collateral_id sequence
CREATE SEQUENCE general_collateral_id_seq INCREMENT BY 1 START WITH 1;
-- search_client, search_response table PK's search_id sequence
CREATE SEQUENCE search_id_seq INCREMENT BY 1 START WITH 1;
-- trust_indenture table PK trust_indenture_id sequence
CREATE SEQUENCE trust_indenture_id_seq INCREMENT BY 1 START WITH 1;
-- court_order table PK court_order_id sequence
CREATE SEQUENCE court_order_id_seq INCREMENT BY 1 START WITH 1;
