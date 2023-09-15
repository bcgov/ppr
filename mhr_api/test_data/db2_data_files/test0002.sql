-- UT-0013 000912 MHREG EXEMPT.
-- UT-0014 000913 MHREG CANCELLED.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000017, '000912', 'E', 'UT000017', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000017', '000912', current timestamp, current timestamp, '101 ', '90499017', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0013                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0013')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000017, 1, 'A', 'UT000017', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000017, 1, 'A', 'UT000017', '1234', 'TEST-0013', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000017, 1, 0, 1, '3', 'UT000017', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000017, 1, 1, 1, ' ', 'B', 'TESTMHREGEXEMPT', '', 'V8R 3A5', 'TEST MHREG EXEMPT', '',
             '1234 TEST-0013                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000017, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0014 000913 MHREG CANCELLED.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000018, '000913', 'C', 'UT000018', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000018', '000913', current timestamp, current timestamp, '101 ', '90499018', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0014                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0014')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000018, 1, 'A', 'UT000018', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000018, 1, 'A', 'UT000018', '1234', 'TEST-0014', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000018, 1, 0, 1, '3', 'UT000018', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000018, 1, 1, 1, ' ', 'B', 'TESTMHREGCANCELLED', '', 'V8R 3A5', 'TEST MHREG CANCELLED', '',
             '1234 TEST-0014                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000018, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;


