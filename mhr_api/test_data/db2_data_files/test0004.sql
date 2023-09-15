-- Transfer test registrations. 
-- UT-0018 000917 active TRANS_AFFIDAVIT
-- UT-0019 000918 QS FROZEN NCON unit note
-- UT-0020 000919 SOLE registration
-- UT-0021 000920 JOINT registration with middle names
-- UT-0022 000921 JOINT registration with no middle names
-- UT-0023 000922 SOLE ADMIN registration
-- UT-0018 000917 registration active TRANS_AFFIDAVIT FROZEN.
-- UT-0024 000923 JOINT registration EXECUTOR party types.
-- UT-0025 000924 COMMON registration 1 EXECUTOR.
-- UT-0026 000925 COMMON registration 3 groups.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000026, '000917', 'R', 'UT000026', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000026', '000917', current timestamp, current timestamp, '101 ', '90499026', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0018                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0018')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000026, 1, 'A', 'UT000026', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000026, 1, 'A', 'UT000026', '1234', 'TEST-0018', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000026, 1, 0, 1, '3', 'UT000026', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000026, 1, 1, 1, ' ', 'I', 'RAMMONDJOAN', '', 'V8R 3A5', 'RAMMOND                  JOAN', '',
             '1234 TEST-0018                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000026, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;

-- UT-0018 000917 active AFFE
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI, DATEOFEX)
     VALUES ('UT000027', '000917', current timestamp, current timestamp, 'AFFE', '90499027', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0018                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0018', current date)
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000026, 2, 0, 1, '3', 'UT000027', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000026, 2, 1, 1, ' ', 'I', 'EXECUTORJACKSON', '', 'V8R 3A5', 'EXECUTOR                 JACKSON', 
             'EXECUTOR OF THE ESTATE OF JOAN RAMMOND',
             '1234 TEST-0018                          CITY                                    BC CA')
;
UPDATE amhrtdb.owngroup
   SET status = '5', candocid = 'UT000027'
 WHERE manhomid = 200000026
   AND owngrpid = 1
   AND regdocid = 'UT000026'
;
-- UT-0019 000918 QS FROZEN NCON registration
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000028, '000918', 'R', 'UT000028', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000028', '000918', current timestamp, current timestamp, '101 ', '90499028', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0019                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0019')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000028, 1, 'A', 'UT000028', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000028, 1, 'A', 'UT000028', '1234', 'TEST-0019', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000028, 1, 0, 1, '3', 'UT000028', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000028, 1, 1, 1, ' ', 'B', 'TESTNOTEACTIVENCON', '', 'V8R 3A5', 'TEST NOTE ACTIVE NCON', '',
             '1234 TEST-0019                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000028, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0019 000918 QS FROZEN NCON unit note
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000029', '000918', current timestamp, current timestamp, 'NCON', '90499029', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0019                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0019')
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000028, 1, 1, 'UT000029', '', 'NCON', 'A', '', TO_DATE('0001-01-01','YYYY-DD-MM'), '6041234567', 
             'PERSON GIVING NOTICE', 
             '1234 TEST-0019                                                                  CITY                                    BC CA                            V8R 3A5', 
             'unit test remarks')
;
-- UT-0020 000919 SOLE registration
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000030, '000919', 'R', 'UT000030', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000030', '000919', current timestamp, current timestamp, '101 ', '90499030', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0020                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0020')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000030, 1, 'A', 'UT000030', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000030, 1, 'A', 'UT000030', '1234', 'TEST-0020', 'CITY', 'BC', 'park name', '1234', '', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000030, 1, 0, 1, '3', 'UT000030', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000030, 1, 1, 1, ' ', 'I', 'SMITHJANE', '', 'V8R 3A5', 'SMITH                    JANE', '',
             '1234 TEST-0020                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000030, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0021 000920 JOINT registration with middle names
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000031, '000920', 'R', 'UT000031', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000031', '000920', current timestamp, current timestamp, '101 ', '90499031', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0021                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0021')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000031, 1, 'A', 'UT000031', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000031, 1, 'A', 'UT000031', '1234', 'TEST-0021', 'CITY', 'BC', 'park name', '1234', '', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000031, 1, 0, 1, '3', 'UT000031', 'JT', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000031, 1, 1, 1, ' ', 'I', 'MOWATROBERTJOHN', '6041234567', 'V8R 3A5', 'MOWAT                    ROBERT         JOHN', '',
             '1234 TEST-0021                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000031, 1, 2, 2, ' ', 'I', 'MOWATKARENPATRICIA', '6041234567', 'V8R 3A5', 'MOWAT                    KAREN          PATRICIA', '',
             '1234 TEST-0021                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000031, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0022 000921 JOINT registration with no middle names
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000032, '000921', 'R', 'UT000032', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000032', '000921', current timestamp, current timestamp, '101 ', '90499032', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0022                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0022')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000032, 1, 'A', 'UT000032', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000032, 1, 'A', 'UT000032', '1234', 'TEST-0022', 'CITY', 'BC', 'park name', '1234', '', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000032, 1, 0, 1, '3', 'UT000032', 'JT', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000032, 1, 1, 1, ' ', 'I', 'HALLDENNIS', '6041234567', 'V8R 3A5', 'HALL                     DENNIS', '',
             '1234 TEST-0022                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000032, 1, 2, 2, ' ', 'I', 'HALLSHARON', '6041234567', 'V8R 3A5', 'HALL                     SHARON', '',
             '1234 TEST-0022                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000032, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0023 000922 SOLE ADMIN registration
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000033, '000922', 'R', 'UT000033', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000033', '000922', current timestamp, current timestamp, '101 ', '90499033', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0023                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0023')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000033, 1, 'A', 'UT000033', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000033, 1, 'A', 'UT000033', '1234', 'TEST-0023', 'CITY', 'BC', 'park name', '1234', '', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000033, 1, 0, 1, '3', 'UT000033', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000033, 1, 1, 1, ' ', 'I', 'KIDDERJOHNTALBOT', '6041234567', 'V8R 3A5', 'KIDDER                   JOHN           TALBOT', 
             'ADMINISTRATOR OF THE ESTATE OF BEVERLY JOY STROM, DECEASED',
             '1234 TEST-0023                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000033, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0024 000923 JOINT registration EXECUTOR party types.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000034, '000923', 'R', 'UT000034', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000034', '000923', current timestamp, current timestamp, '101 ', '90499034', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0024                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0024')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000034, 1, 'A', 'UT000034', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000034, 1, 'A', 'UT000034', '1234', 'TEST-0024', 'CITY', 'BC', 'park name', '1234', '', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000034, 1, 0, 1, '3', 'UT000034', 'JT', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000034, 1, 1, 1, ' ', 'I', 'HALLDENNIS', '6041234567', 'V8R 3A5', 'HALL                   DENNIS', 
             'EXECUTOR OF THE ESTATE OF BEVERLY JOY STROM, DECEASED',
             '1234 TEST-0024                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000034, 1, 2, 2, ' ', 'I', 'HALLSHARON', '6041234567', 'V8R 3A5', 'HALL                   SHARON', 
             'EXECUTOR OF THE ESTATE OF BEVERLY JOY STROM, DECEASED',
             '1234 TEST-0024                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000034, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0025 000924 COMMON registration 1 EXECUTOR.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000035, '000924', 'R', 'UT000035', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000035', '000924', current timestamp, current timestamp, '101 ', '90499035', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0025                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0025')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000035, 1, 'A', 'UT000035', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000035, 1, 'A', 'UT000035', '1234', 'TEST-0025', 'CITY', 'BC', 'park name', '1234', '', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000035, 1, 0, 1, '3', 'UT000035', 'TC', 'UNDIVIDED 1/2', 1, 'Y')
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000035, 2, 0, 2, '3', 'UT000035', 'TC', 'UNDIVIDED 1/2', 1, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000035, 1, 1, 1, ' ', 'I', 'HALLDENNIS', '6041234567', 'V8R 3A5', 'HALL                   DENNIS', 
             'EXECUTOR OF THE ESTATE OF BEVERLY JOY STROM, DECEASED',
             '1234 TEST-0025                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000035, 2, 1, 1, ' ', 'I', 'HALLSHARON', '6041234567', 'V8R 3A5', 'HALL                   SHARON', '',
             '1234 TEST-0025                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000035, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0026 000925 COMMON registration 3 groups.
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000036, '000925', 'R', 'UT000036', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000036', '000925', current timestamp, current timestamp, '101 ', '90499036', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0026                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0026')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000036, 1, 'A', 'UT000036', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000036, 1, 'A', 'UT000036', '1234', 'TEST-0026', 'CITY', 'BC', 'park name', '1234', '', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000036, 1, 0, 1, '3', 'UT000036', 'TC', 'UNDIVIDED 1/3', 1, 'Y')
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000036, 2, 0, 2, '3', 'UT000036', 'TC', 'UNDIVIDED 1/3', 1, 'Y')
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000036, 3, 0, 3, '3', 'UT000036', 'TC', 'UNDIVIDED 1/3', 1, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000036, 1, 1, 1, ' ', 'I', 'HALLDENNIS', '6041234567', 'V8R 3A5', 'HALL                   DENNIS', '',
             '1234 TEST-0026                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000036, 2, 1, 1, ' ', 'I', 'HALLSHARON', '6041234567', 'V8R 3A5', 'HALL                   SHARON', '',
             '1234 TEST-0026                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000036, 3, 1, 1, ' ', 'I', 'HALLSHELLEY', '6041234567', 'V8R 3A5', 'HALL                   SHELLEY', '',
             '1234 TEST-0026                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000036, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
