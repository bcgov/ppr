-- assets 15157 begin DEV 2023-01-30, TEST 2023-01-31, PROD 2023-02-02
select mh.mhregnum, trim(n.remarks)
  from amhrtdb.manuhome mh, amhrtdb.mhomnote n
 where mh.manhomid = n.manhomid
   and n.docutype = 'TAXN'
   and n.remarks like '%403%'
;
/*
075430	A NOTICE PURSUANT TO SECTION 403 OF THE MUNICIPAL ACT WAS FILED
022778	A NOTICE PURSUANT TO SECTION 403 OF THE LOCAL GOVERNMENT ACT WAS FILED
062390	A NOTICE PURSUANT TO SECTION 403, CHAPTER 323 OF THE LOCAL GOVERNMENT ACT WAS FILED
042473	A NOTICE PURSUANT TO SECTION 403 OF THE MUNICIPAL ACT WAS FILED
042481	A NOTICE PURSUANT TO SECTION 403 OF THE LOCAL GOVERNMENT ACT WAS FILED
037481	A NOTICE PURSUANT TO SECTION 403 (1) OF THE MUNICIPAL ACT WAS FILED
036384	A NOTICE PURSUANT TO SECTION 403 OF THE MUNICIPAL ACT WAS FILED
032776	A NOTICE PURSUANT TO SECTION 403 OF THE LOCAL GOVERNMENT ACT WAS FILED
030987	A NOTICE PURSUANT TO SECTION 403 OF THE LOCAL GOVERNMENT ACT WAS FILED
030301	A NOTICE PURSUANT TO SECTION 403 OF THE LOCAL GOVERNMENT ACT WAS FILED
024774	A NOTICE PURSUANT TO SECTION 403 OF THE MUNICIPAL ACT WAS FILED
022483	A NOTICE PURSUANT TO DIVISION 8, SECTION 403 OF THE MUNICIPAL ACT WAS FILED
020320	A NOTICE PURSUANT TO SECTION 403 OF THE LOCAL GOVERNMENT ACT WAS FILED
016149	A NOTICE PURSUANT TO SECTOIN 400,403 AND 407 OF THE LOCAL GOVERNMENT  ACT WAS FILED
013550	A NOTICE PURSUANT TO SECTIONS 400, 403 AND 407 OF THE MUNICIPAL ACT   WAS FILED.
*/

UPDATE amhrtdb.mhomnote
   SET remarks = 'A NOTICE PURSUANT TO SECTION 457/464 OF THE MUNICIPAL ACT WAS FILED'
 WHERE docutype = 'TAXN'
   AND TRIM(remarks) = 'A NOTICE PURSUANT TO SECTION 403 OF THE MUNICIPAL ACT WAS FILED'
;

UPDATE amhrtdb.mhomnote
   SET remarks = 'A NOTICE PURSUANT TO SECTION 457/464 OF THE MUNICIPAL ACT WAS FILED'
 WHERE docutype = 'TAXN'
   AND TRIM(remarks) = 'A NOTICE PURSUANT TO SECTION 403 OF THE LOCAL GOVERNMENT ACT WAS FILED'
;

UPDATE amhrtdb.mhomnote
   SET remarks = 'A NOTICE PURSUANT TO SECTION 457/464 OF THE MUNICIPAL ACT WAS FILED'
 WHERE docutype = 'TAXN'
   AND TRIM(remarks) = 'A NOTICE PURSUANT TO SECTION 403, CHAPTER 323 OF THE LOCAL GOVERNMENT ACT WAS FILED'
;

UPDATE amhrtdb.mhomnote
   SET remarks = 'A NOTICE PURSUANT TO SECTION 457/464 OF THE MUNICIPAL ACT WAS FILED'
 WHERE docutype = 'TAXN'
   AND TRIM(remarks) = 'A NOTICE PURSUANT TO SECTION 403 (1) OF THE MUNICIPAL ACT WAS FILED'
;

UPDATE amhrtdb.mhomnote
   SET remarks = 'A NOTICE PURSUANT TO SECTION 457/464 OF THE MUNICIPAL ACT WAS FILED'
 WHERE docutype = 'TAXN'
   AND TRIM(remarks) = 'A NOTICE PURSUANT TO DIVISION 8, SECTION 403 OF THE MUNICIPAL ACT WAS FILED'
;

UPDATE amhrtdb.mhomnote
   SET remarks = 'A NOTICE PURSUANT TO SECTION 457/464 OF THE MUNICIPAL ACT WAS FILED'
 WHERE docutype = 'TAXN'
   AND TRIM(remarks) = 'A NOTICE PURSUANT TO SECTOIN 400,403 AND 407 OF THE LOCAL GOVERNMENT  ACT WAS FILED'
;

UPDATE amhrtdb.mhomnote
   SET remarks = 'A NOTICE PURSUANT TO SECTION 457/464 OF THE MUNICIPAL ACT WAS FILED'
 WHERE docutype = 'TAXN'
   AND TRIM(remarks) = 'A NOTICE PURSUANT TO SECTIONS 400, 403 AND 407 OF THE MUNICIPAL ACT   WAS FILED.'
;
-- assets 15157 end

