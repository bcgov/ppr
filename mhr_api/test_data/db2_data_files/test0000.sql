-- Reset existing test data
DELETE FROM amhrtdb.mhomnote WHERE manhomid >= 200000000;
DELETE FROM amhrtdb.owner WHERE manhomid >= 200000000;
DELETE FROM amhrtdb.owngroup WHERE manhomid >= 200000000;
DELETE FROM amhrtdb.location WHERE manhomid >= 200000000;
DELETE FROM amhrtdb.cmpserno WHERE manhomid >= 200000000;
DELETE FROM amhrtdb.descript WHERE manhomid >= 200000000;
DELETE FROM amhrtdb.document WHERE mhregnum LIKE '0009%';
DELETE FROM amhrtdb.manuhome WHERE mhregnum LIKE '0009%';
