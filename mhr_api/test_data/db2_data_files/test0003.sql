-- Unit note test registrations. 
-- UT-0015 000914 active TAXN.
-- UT-0016 000915 active REST.
-- UT-0017 000916 active CAU.
-- UT-0015 000914 active TAXN.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000019, '000914', 'R', 'UT000019', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000019', '000914', current timestamp, current timestamp, '101 ', '90499019', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0015                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0015')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000019, 1, 'A', 'UT000019', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000019, 1, 'A', 'UT000019', '1234', 'TEST-0015', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000019, 1, 0, 1, '3', 'UT000019', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000019, 1, 1, 1, ' ', 'B', 'TESTNOTEACTIVETAXN', '', 'V8R 3A5', 'TEST NOTE ACTIVE TAXN', '',
             '1234 TEST-0015                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000019, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0015 TAXN unit note 
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000020', '000914', current timestamp, current timestamp, 'TAXN', '90499020', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0015                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0015')
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000019, 1, 1, 'UT000020', '', 'TAXN', 'A', '', TO_DATE('0001-01-01','YYYY-DD-MM'), '6041234567', 
             'PERSON GIVING NOTICE', 
             '1234 TEST-0015                                                                  CITY                                    BC CA                            V8R 3A5', 
             'unit test remarks')
;
-- UT-0016 000915 active REST.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000021, '000915', 'R', 'UT000021', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000021', '000915', current timestamp, current timestamp, '101 ', '90499021', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0016                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0016')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000021, 1, 'A', 'UT000021', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000021, 1, 'A', 'UT000021', '1234', 'TEST-0016', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000021, 1, 0, 1, '3', 'UT000021', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000021, 1, 1, 1, ' ', 'B', 'TESTNOTEACTIVEREST', '', 'V8R 3A5', 'TEST NOTE ACTIVE REST', '',
             '1234 TEST-0016                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000021, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0016 REST unit note 
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000022', '000915', current timestamp, current timestamp, 'REST', '90499022', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0016                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0016')
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000021, 1, 1, 'UT000022', '', 'REST', 'A', '', TO_DATE('0001-01-01','YYYY-DD-MM'), '6041234567', 
             'PERSON GIVING NOTICE', 
             '1234 TEST-0016                                                                  CITY                                    BC CA                            V8R 3A5', 
             'unit test remarks')
;
-- UT-0013 EXRS unit note 
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000023', '000912', current timestamp, current timestamp, 'EXRS', '90499023', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0013                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0013')
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000017, 1, 1, 'UT000023', '', 'EXRS', 'A', '', TO_DATE('0001-01-01','YYYY-DD-MM'), '6041234567', 
             'PERSON GIVING NOTICE', 
             '1234 TEST-0013                                                                  CITY                                    BC CA                            V8R 3A5', 
             'unit test remarks')
;
-- UT-0017 000916 active CAU registration.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000024, '000916', 'R', 'UT000024', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000024', '000916', current timestamp, current timestamp, '101 ', '90499024', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0017                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0017')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000024, 1, 'A', 'UT000024', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000024, 1, 'A', 'UT000024', '1234', 'TEST-0017', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000024, 1, 0, 1, '3', 'UT000024', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000024, 1, 1, 1, ' ', 'B', 'TESTNOTEACTIVECAU', '', 'V8R 3A5', 'TEST NOTE ACTIVE CAU', '',
             '1234 TEST-0017                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000024, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0017 000916 active CAU unit note.
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000025', '000916', current timestamp, current timestamp, 'CAU ', '90499025', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0017                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0017')
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000024, 1, 1, 'UT000025', '', 'CAU ', 'A', '', current date + 89 days, '6041234567', 
             'PERSON GIVING NOTICE', 
             '1234 TEST-0017                                                                  CITY                                    BC CA                            V8R 3A5', 
             'unit test remarks')
;


