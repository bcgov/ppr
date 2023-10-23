-- UT-0033 000932 MHREG EXEMPT with NCON, TAXN notes.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000047, '000932', 'E', 'UT000047', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000047', '000932', current timestamp, current timestamp, '101 ', '90499047', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0033                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TEST USER', 'UT-0033')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000047, 1, 'A', 'UT000047', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'MANUFACTURER', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE, MHDEALER, ADDDESC)
     VALUES (200000047, 1, 'A', 'UT000047', '1234', 'TEST-0033', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'), '', 'additional')
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000047, 1, 0, 1, '3', 'UT000047', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000047, 1, 1, 1, ' ', 'B', 'TESTEXRSACTIVE', '6041234567', 'V8R 3A5', 'TTEST EXRS ACTIVE', '',
             '1234 TEST-0033                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000047, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0033 000932 NCON note registration
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000048', '000932', current timestamp, current timestamp, 'NCON', '90499048', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0033                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TEST USER', 'UT-0033')
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000047, 1, 1, 'UT000048', '', 'NCON', 'A', '', TO_DATE('0001-01-01', 'YYYY-MM-DD'), '6041234567', 
             'PERSON GIVING NOTICE', 
             '1234 TEST-0033                                                                  CITY                                    BC CA                            V8R 3A5', 
             'NCON NOTE REMARKS')
;
-- UT-0033 000932 TAXN note registration
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000049', '000932', current timestamp, current timestamp, 'TAXN', '90499049', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0033                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TEST USER', 'UT-0033')
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000047, 2, 2, 'UT000049', '', 'TAXN', 'A', '', TO_DATE('0001-01-01', 'YYYY-MM-DD'), '6041234567', 
             'PERSON GIVING NOTICE', 
             '1234 TEST-0033                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TAXN NOTE REMARKS')
;
-- UT-0033 000932 EXRS registration
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000050', '000932', current timestamp, current timestamp, 'EXRS', '90499050', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0033                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TEST USER', 'UT-0033')
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000047, 3, 3, 'UT000050', '', 'EXRS', 'A', '', TO_DATE('0001-01-01', 'YYYY-MM-DD'), '6041234567', 
             'PERSON GIVING NOTICE', 
             '1234 TEST-0033                                                                  CITY                                    BC CA                            V8R 3A5', 
             'RESIDENTIAL REMARKS')
;

