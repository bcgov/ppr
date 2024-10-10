-- Post staging tables load step 8:
-- Remove all draft changes from the staging tables.
-- Registrations in a draft state have no staging_mhr_document.docuregi and a regidate year of 1.
-- Remove TEST MH registrations from the staging tables for MHR numbers: '094506', '096392', '089036'

-- location draft records
-- Anomaly, draft but no active record
UPDATE staging_mhr_location
   SET status = 'A', candocid = null
 WHERE manhomid in (20447)
   AND status = 'H'
;  
delete
  from staging_mhr_location
 where status = 'D'
   and manhomid in (20447)
;

-- Truly a draft
delete
  from staging_mhr_location
 where status = 'D'
   and trim(regdocid) = ''
;
delete
  from staging_mhr_location
 where status = 'D'
   and not exists (select l.regdocid
                     from staging_mhr_location l
                    where l.manhomid = staging_mhr_location.manhomid
                      and l.status != 'D'
                      and l.candocid = staging_mhr_location.regdocid)
;
update staging_mhr_location
   set candocid = (select regdocid
                     from staging_mhr_location l2
                    where l2.manhomid = staging_mhr_location.manhomid
                      and status = 'A')
 where status = 'H'
   and candocid = (select l.regdocid
                     from staging_mhr_location l
                    where l.manhomid = staging_mhr_location.manhomid
                      and l.status = 'D')
;
delete
  from staging_mhr_location
 where status = 'D'
;


-- description draft records
delete
  from staging_mhr_description
 where status = 'D'
   and trim(regdocid) = ''
;
delete
  from staging_mhr_description
 where status = 'D'
;


-- unit note draft records
update staging_mhr_note
   set candocid = null, status = 'A'
 where candocid in (select d.documtid
                      from staging_mhr_document d
                     where d.docuregi is null or trim(d.docuregi) = '')
;
delete
  from staging_mhr_note
 where regdocid in (select d.documtid
                      from staging_mhr_document d
                     where d.docuregi is null or trim(d.docuregi) = '')
;
delete
  from staging_mhr_note
 where manhomid in (select m.manhomid
                      from staging_mhr_manuhome m, staging_mhr_document d
                     where m.mhregnum = d.mhregnum
                       and trim(docuregi) = '')
  and status = 'D'
;

-- owner draft records
delete
  from staging_mhr_owner o
 where o.manhomid in (select og.manhomid
                       from staging_mhr_owngroup og
                      where og.manhomid = o.manhomid
                        and og.status = '1')
  and o.owngrpid in (select og.owngrpid
                       from staging_mhr_owngroup og
                      where og.manhomid = o.manhomid
                        and og.status = '1')

;

-- owner group draft records
update staging_mhr_owngroup
   set pending = null
 where pending is not null
   and pending = 'X'
   and status = '3'
   and exists (select og.manhomid
                 from staging_mhr_owngroup og
                where og.manhomid = staging_mhr_owngroup.manhomid
                  and og.status = '1')
;
delete
  from staging_mhr_owngroup
 where status = '1'
;

-- document draft records
delete
  from staging_mhr_document
 where docuregi is null or trim(docuregi) = ''
;

-- draft registrations
delete
  from staging_mhr_manuhome
 where mhstatus in ('D', 'DRAFT') 
;


delete
  from staging_mhr_note n
 where not exists (select d.documtid
                     from staging_mhr_document d
                    where d.documtid = n.regdocid) 
;



-- Remove test registrations below.
delete
  from staging_mhr_note
where manhomid in (90512,96026,97916);

delete
  from staging_mhr_location
where manhomid in (90512,96026,97916);

delete
  from staging_mhr_description
where manhomid in (90512,96026,97916);

delete
  from staging_mhr_owner
where manhomid in (90512,96026,97916);

delete
  from staging_mhr_owngroup
where manhomid in (90512,96026,97916);

delete
 from staging_mhr_document
where mhregnum in ('094506', '096392', '089036')
;

delete
 from staging_mhr_manuhome
where mhregnum in ('094506', '096392', '089036')
;



