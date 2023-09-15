-- Miscellaneous transort Permit and exemption test registrations. 
-- UT-0027 000926 Manufacturer registration with existing transport permit registration.
-- UT-0028 000927 new MH registration for a manufacturer
-- UT-0029 000928 EXEMPT non-residential MH registration
-- UT-0030 000929 COMMON registration 1 ADMINISTRATOR.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000037, '000926', 'R', 'UT000037', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000037', '000926', current timestamp, current timestamp, '101 ', '90499037', 'N', 'PS12345 ', '6041234567', 
             'REAL ENGINEERED HOMES INC', 
             '1234 TEST-0027                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0027')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000037, 1, 'A', 'UT000037', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'REAL ENGINEERED HOMES INC', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE, MHDEALER)
     VALUES (200000037, 1, 'A', 'UT000037', '1234', 'TEST-0027', 'CITY', 'BC', '', '', '', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'), 'REAL ENGINEERED HOMES INC')
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000037, 1, 0, 1, '3', 'UT000037', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000037, 1, 1, 1, ' ', 'B', 'REALENGINEEREDHOMES', '6041234567', 'V8R 3A5', 'REAL ENGINEERED HOMES INC', '',
             '1234 TEST-0027                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000037, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- Transport permit registration
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000038', '000926', current timestamp, current timestamp, '103 ', '90499038', 'N', 'PS12345 ', '6041234567', 
             'REAL ENGINEERED HOMES INC', 
             '1234 TEST-0027                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0027')
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000037, 2, 'A', 'UT000038', '1234', 'TEST-0027', 'CITY', 'BC', 'PARK NAME', '1234', '', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000037, 1, 1, 'UT000038', '', '103 ', 'A', '', current date + 30 days, '6041234567', 
             'PERSON GIVING NOTICE', 
             '1234 TEST-0027                                                                  CITY                                    BC CA                            V8R 3A5', 
             '')
;
UPDATE amhrtdb.location
   SET status = 'H', candocid = 'UT000038'
 WHERE regdocid = 'UT000037'
;
-- UT-0028 000927 new MH registration for a manufacturer
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000039, '000927', 'R', 'UT000039', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000039', '000927', current timestamp, current timestamp, '101 ', '90499037', 'N', 'PS12345 ', '6041234567', 
             'REAL ENGINEERED HOMES INC', 
             '1234 TEST-0028                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0028')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000039, 1, 'A', 'UT000039', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'REAL ENGINEERED HOMES INC', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE, MHDEALER)
     VALUES (200000039, 1, 'A', 'UT000039', '1234', 'TEST-0028', 'CITY', 'BC', '', '', '', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'), 'REAL ENGINEERED HOMES INC')
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000039, 1, 0, 1, '3', 'UT000039', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000039, 1, 1, 1, ' ', 'B', 'REALENGINEEREDHOMES', '6041234567', 'V8R 3A5', 'REAL ENGINEERED HOMES INC', '',
             '1234 TEST-0028                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000039, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0029 000928 EXEMPT non-residential MH registration
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000040, '000928', 'E', 'UT000040', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000040', '000928', current timestamp, current timestamp, '101 ', '90499040', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0029                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0029')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000040, 1, 'A', 'UT000040', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000040, 1, 'A', 'UT000040', '1234', 'TEST-0029', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000040, 1, 0, 1, '3', 'UT000040', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000040, 1, 1, 1, ' ', 'B', 'TESTEXNRACTIVE', '', 'V8R 3A5', 'TEST EXNR ACTIVE', '',
             '1234 TEST-0029                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000040, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0029 000928 non-residential MH registration
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000041', '000929', current timestamp, current timestamp, 'EXNR', '90499041', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0029                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0029')
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000040, 1, 1, 'UT000041', '', 'EXNR', 'A', '', TO_DATE('0001-01-01','YYYY-DD-MM'), '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0029                                                                  CITY                                    BC CA                            V8R 3A5', 
             'NON-RESIDENTIAL REMARKS')
;
-- UT-0030 000929 COMMON registration 1 ADMINISTRATOR.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000042, '000929', 'R', 'UT000042', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000042', '000929', current timestamp, current timestamp, '101 ', '90499042', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0030                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0030')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000042, 1, 'A', 'UT000042', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000042, 1, 'A', 'UT000042', '1234', 'TEST-0030', 'CITY', 'BC', 'park name', '1234', '', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000042, 1, 0, 1, '3', 'UT000042', 'TC', 'UNDIVIDED 1/2', 1, 'Y')
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000042, 2, 0, 2, '3', 'UT000042', 'TC', 'UNDIVIDED 1/2', 1, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000042, 1, 1, 1, ' ', 'I', 'HALLDENNIS', '6041234567', 'V8R 3A5', 'HALL                   DENNIS', 
             'ADMINISTRATOR OF THE ESTATE OF BEVERLY JOY STROM, DECEASED',
             '1234 TEST-0030                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000042, 2, 1, 1, ' ', 'I', 'HALLSHARON', '6041234567', 'V8R 3A5', 'HALL                   SHARON', '',
             '1234 TEST-0030                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000042, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
