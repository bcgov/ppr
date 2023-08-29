-- Search unit test registrations
-- UT 001 active, no other registrations, used by search
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000001, '000900', 'R', 'UT000001', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000001', '000900', current timestamp, current timestamp, '101 ', '90499001', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0001                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0001')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE, SERNUMB1,
                             LENGTH1, LENGIN1, WIDTH1, WIDIN1, MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000001, 1, 'A', 'UT000001', '7777700000', '1234', 1, '2000', '0310282AB', 60, 10, 14, 11, 
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000001, 1, 'A', 'UT000001', '1234', 'TEST-0001', 'CITY', 'BC', 'park name', 'pad', '008000000', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000001, 1, 0, 1, '3', 'UT000001', 'TC', 'UNDIVIDED 1/2', 1, 'Y')
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000001, 2, 0, 1, '3', 'UT000001', 'TC', 'UNDIVIDED 1/2', 1, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000001, 1, 1, 1, ' ', 'B', 'CELESTIALHEAVENLYHOMES', '2507701067', 'V8R 3A5', 'CELESTIAL HEAVENLY HOMES', '',
             '1234 TEST-0001                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000001, 2, 1, 1, ' ', 'I', 'MCKAYBOBARTHUR', '2507701067', 'V8R 3A5', 'MCKAY                    BOB                     ARTHUR', '',
             '1234 TEST-0001                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000001, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 100865))
;

-- UT 002 active, owners used by search
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000002, '000901', 'R', 'UT000002', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000002', '000901', current timestamp, current timestamp, '101 ', '90499002', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0002                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0002')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE, SERNUMB1,
                             LENGTH1, LENGIN1, WIDTH1, WIDIN1, MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000002, 1, 'A', 'UT000002', '77777', '1234', 1, '2000', 'D1644', 60, 10, 14, 11, 
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000002, 1, 'A', 'UT000002', '1234', 'TEST-0001', 'CITY', 'BC', 'park name', 'pad', '008000000', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000002, 1, 0, 1, '3', 'UT000002', 'JT', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000002, 1, 1, 1, ' ', 'I', 'RAMMONDBRIAN', '2507701067', 'V8R 3A5', 'RAMMOND                  BRIAN', '',
             '1234 TEST-0002                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000002, 1, 2, 2, ' ', 'I', 'RAMMONDROSECHERYL', '2507701067', 'V8R 3A5', 'RAMMOND                  ROSE                    CHERYL', '',
             '1234 TEST-0002                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000002, 1, 3, 3, ' ', 'I', 'RAMMONDDENISE', '2507701067', 'V8R 3A5', 'RAMMOND                  DENISE', '',
             '1234 TEST-0002                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000002, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 76226))
;

-- UT-0007 org name collapse
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000007, '000906', 'R', 'UT000007', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000007', '000906', current timestamp, current timestamp, '101 ', '90499007', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0007                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0002')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE, SERNUMB1,
                             LENGTH1, LENGIN1, WIDTH1, WIDIN1, MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000007, 1, 'A', 'UT000007', '77777', '1234', 1, '2000', '998765', 60, 10, 14, 11, 
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000007, 1, 'A', 'UT000007', '1234', 'TEST-0007', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC, CANDOCID)
     VALUES (200000007, 1, 0, 1, '5', 'UT000007', 'JT', '', 0, 'Y', 'UT000007')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000007, 1, 1, 1, ' ', 'B', 'TESTONLYSERAPHICHOMES', '', 'V8R 3A5', 'TEST ONLY SERAPHIC HOMES', '',
             '1234 TEST-0007                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000007, 1, 2, 2, ' ', 'B', 'TESTONLYSERAPHICHOMES', '', 'V8R 3A5', 'TEST ONLY SERAPHIC HOMES', '',
             '1234 TEST-0007                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000007, 2, 0, 1, '3', 'UT000007', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000007, 2, 1, 1, ' ', 'B', 'TESTONLYSERAPHICHOMES', '', 'V8R 3A5', 'TEST ONLY SERAPHIC HOMES', '',
             '1234 TEST-0007                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000007, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 76225))
;

-- UT-0008 individual name collapse
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000008, '000907', 'R', 'UT000008', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000008', '000907', current timestamp, current timestamp, '101 ', '90499008', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0008                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0002')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE, SERNUMB1,
                             LENGTH1, LENGIN1, WIDTH1, WIDIN1, MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000008, 1, 'A', 'UT000008', '77777', '1234', 1, '2000', '998765', 60, 10, 14, 11, 
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000008, 1, 'A', 'UT000008', '1234', 'TEST-0008', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC, CANDOCID)
     VALUES (200000008, 1, 0, 1, '5', 'UT000008', 'SO', '', 0, 'Y', 'UT000008')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000008, 1, 1, 1, ' ', 'I', 'ZAXODGAYLEX', '', 'V8R 3A5', 'ZAXOD                    GAYLEX', '',
             '1234 TEST-0008                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC, CANDOCID)
     VALUES (200000008, 2, 0, 1, '4', 'UT000008', 'SO', '', 0, 'Y', 'UT000008')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000008, 2, 1, 1, ' ', 'I', 'ZAXODGAYLEX', '', 'V8R 3A5', 'ZAXOD                    GAYLEX', '',
             '1234 TEST-0008                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000008, 3, 0, 1, '3', 'UT000008', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000008, 3, 1, 1, ' ', 'I', 'ZAXODGAYLEX', '', 'V8R 3A5', 'ZAXOD                    GAYLEX', '',
             '1234 TEST-0008                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000008, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 76225))
;
-- UT-0009 serial number collapse
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000009, '000908', 'R', 'UT000009', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000009', '000908', current timestamp, current timestamp, '101 ', '90499009', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0009                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0002')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             SERNUMB2, LENGTH2, LENGIN2, WIDTH2, WIDIN2,
                             SERNUMB3, LENGTH3, LENGIN3, WIDTH3, WIDIN3,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000009, 1, 'A', 'UT000009', '77777', '1234', 3, '2000', '000060', 60, 10, 14, 11,
             '000060', 60, 10, 14, 11,
             '000060', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000009, 1, 'A', 'UT000009', '1234', 'TEST-0009', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000009, 1, 0, 1, '3', 'UT000009', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000009, 1, 1, 1, ' ', 'B', 'TESTSERIALNINE', '', 'V8R 3A5', 'TEST SERIAL NINE', '',
             '1234 TEST-0009                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000009, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 100865 AND CMPSERID = 1))
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000009, 2, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 100865 AND CMPSERID = 1))
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000009, 3, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 100865 AND CMPSERID = 1))
;
-- UT-0010 search results registration with caution unit note and cancel unit note. 
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000010, '000909', 'R', 'UT000010', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000010', '000909', current timestamp, current timestamp, '101 ', '90499010', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0010                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0010')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000010, 1, 'A', 'UT000010', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000010, 1, 'A', 'UT000010', '1234', 'TEST-0009', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000010, 1, 0, 1, '3', 'UT000010', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000010, 1, 1, 1, ' ', 'B', 'TEST NOTE CAU CANCEL', '', 'V8R 3A5', 'TEST NOTE CAU CANCEL', '',
             '1234 TEST-0010                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000010, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0010 CAU unit note 
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000011', '000909', current timestamp, current timestamp, 'CAU ', '90499011', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0010                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0010')
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000010, 1, 1, 'UT000011', '', 'CAU ', 'A', '', TO_DATE('0001-01-01','YYYY-DD-MM'), '6041234567', 
             'PERSON GIVING NOTICE', 
             '1234 TEST-0010                                                                  CITY                                    BC CA                            V8R 3A5', 
             'unit test remarks')
;
-- UT-0010 NCAN unit note 
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000012', '000909', current timestamp, current timestamp, 'NCAN', '90499012', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0010                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0010')
;
UPDATE amhrtdb.mhomnote
   SET status = 'C', candocid = 'UT000012'
 WHERE manhomid = 200000010
   AND mhnoteid = 1
   AND docutype = 'CAU '
;
-- UT-0011 search results registration with TAXN unit note and cancel unit note. 
INSERT INTO amhrtdb.manuhome(MANHOMID, MHREGNUM, MHSTATUS, REGDOCID, UPDATECT, UPDATEID, UPDATEDA, UPDATETI)
     VALUES (200000013, '000910', 'R', 'UT000013', 1, 'PS12345 ', current date, current time)
;
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000013', '000910', current timestamp, current timestamp, '101 ', '90499013', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0011                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0011')
;
INSERT INTO amhrtdb.descript(MANHOMID, DESCRNID, STATUS, REGDOCID, CSANUMBR, CSASTAND, NUMBSECT, YEARMADE,
                             SERNUMB1, LENGTH1, LENGIN1, WIDTH1, WIDIN1,
                             MANUNAME, MAKEMODL, REBUILTR, OTHERREM, ENGIDATE)
     VALUES (200000013, 1, 'A', 'UT000013', '77777', '1234', 1, '2000', '888888', 60, 10, 14, 11,
             'manufacturer', 'make model', 'rebuilt', 'other', TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.location(MANHOMID, LOCATNID, STATUS, REGDOCID, STNUMBER, STNAME, TOWNCITY, PROVINCE, MAHPNAME,
                             MAHPPAD, PIDNUMB, TAXCERT, TAXDATE)
     VALUES (200000013, 1, 'A', 'UT000013', '1234', 'TEST-0011', 'CITY', 'BC', '', '', '005509807', 'N',
             TO_DATE('0001-01-01', 'YYYY-MM-DD'))
;
INSERT INTO amhrtdb.owngroup(MANHOMID, OWNGRPID, COPGRPID, GRPSEQNO, STATUS, REGDOCID, TENYTYPE, INTEREST, INTNUMER, TENYSPEC)
     VALUES (200000013, 1, 0, 1, '3', 'UT000013', 'SO', '', 0, 'Y')
;
INSERT INTO amhrtdb.owner(MANHOMID, OWNGRPID, OWNERID, OWNSEQNO, VERIFIED, OWNRTYPE, COMPNAME, OWNRFONE, OWNRPOCO, OWNRNAME, OWNRSUFF, OWNRADDR)
     VALUES (200000013, 1, 1, 1, ' ', 'B', 'TEST NOTE TAXN CANCEL', '', 'V8R 3A5', 'TEST NOTE TAXN CANCEL', '',
             '1234 TEST-0011                          CITY                                    BC CA')
;
INSERT INTO amhrtdb.cmpserno(MANHOMID, CMPSERID, SERIALNO)
     VALUES (200000013, 1, (SELECT serialno FROM amhrtdb.cmpserno WHERE manhomid = 40865 AND CMPSERID = 1))
;
-- UT-0011 TAXN unit note 
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000014', '000910', current timestamp, current timestamp, 'TAXN', '90499014', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0011                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0011')
;
INSERT INTO amhrtdb.mhomnote(MANHOMID, MHNOTEID, MHNOTENO, REGDOCID, CANDOCID, DOCUTYPE, STATUS, DESTROYD, EXPIRYDA, PHONE, NAME, ADDRESS, REMARKS)
     VALUES (200000013, 1, 1, 'UT000014', '', 'TAXN', 'A', '', TO_DATE('0001-01-01','YYYY-DD-MM'), '6041234567', 
             'PERSON GIVING NOTICE', 
             '1234 TEST-0011                                                                  CITY                                    BC CA                            V8R 3A5', 
             'unit test remarks')
;
-- UT-0011 NRED unit note 
INSERT INTO amhrtdb.document(DOCUMTID, MHREGNUM, DRAFDATE, REGIDATE, DOCUTYPE, DOCUREGI, OWNLAND, UPDATEID, PHONE, NAME, ADDRESS, AFFIRMBY, OLBCFOLI)
     VALUES ('UT000015', '000910', current timestamp, current timestamp, 'NRED', '90499015', 'N', 'PS12345 ', '6041234567', 
             'SUBMITTING', 
             '1234 TEST-0011                                                                  CITY                                    BC CA                            V8R 3A5', 
             'TESTUSER', 'UT-0011')
;
UPDATE amhrtdb.mhomnote
   SET status = 'C', candocid = 'UT000015'
 WHERE manhomid = 200000013
   AND mhnoteid = 1
   AND docutype = 'TAXN'
;

