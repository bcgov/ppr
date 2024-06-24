-- 21975 begin PPR API build 1.2.5 

-- 3635874 PROD 2024-06-24
select max(id)
  from drafts
;

-- 1886177
select max(id)
  from drafts
 where account_id = '0'
;

-- 1746001
select count(d.id)
  from drafts d, registrations r 
 where d.account_id != '0'
   and d.account_id not like '%_USED'
   and d.id = r.draft_id
   and d.id between 1886177 and 2300000 -- 412787
--   and d.id between 2300001 and 2800000 -- 498879
--   and d.id between 2800001 and 3300000 -- 499138
--   and d.id > 3300000 -- 335219
;
update drafts
   set account_id = account_id || '_USED'
 where id in (select d.id
                from drafts d, registrations r 
               where d.account_id != '0'
                 and d.account_id not like '%_USED'
                 and d.id = r.draft_id
                 and d.id between 1886177 and 2300000)
;

update drafts
   set account_id = account_id || '_USED'
 where id in (select d.id
                from drafts d, registrations r 
               where d.account_id != '0'
                 and d.account_id not like '%_USED'
                 and d.id = r.draft_id
                 and d.id between 2300001 and 2800000)
;
update drafts
   set account_id = account_id || '_USED'
 where id in (select d.id
                from drafts d, registrations r 
               where d.account_id != '0'
                 and d.account_id not like '%_USED'
                 and d.id = r.draft_id
                 and d.id between 2800001 and 3300000)
;
update drafts
   set account_id = account_id || '_USED'
 where id in (select d.id
                from drafts d, registrations r 
               where d.account_id != '0'
                 and d.account_id not like '%_USED'
                 and d.id = r.draft_id
                 and d.id > 3300000)
;

-- 21975 end PPR API build 1.2.5 
