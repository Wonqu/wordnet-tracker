CREATE VIEW view_tracker_synsets_history AS
SELECT t.id as id, t.datetime, t.user,
case
	when t.inserted = 1 and t.table ='synset' then 'created'
    when t.inserted = 1 and t.table ='unitandsynset' then 'attached sense'
	when t.deleted = 1 and t.table ='synset' then 'removed'
    when t.deleted = 1 and t.table ='unitandsynset' then 'detached sense'
    when t.inserted = 0 and t.deleted = 0 then 'modified'
end as operation,
case
	when uas.SYN_ID is not null then uas.SYN_ID
    when s.ID is not null then s.ID
    when ts.ID is not null then ts.ID
end as synset_id,
case
	when ts.unitsstr is not null then ts.unitsstr
    when s.unitsstr is not null then s.unitsstr
end as synset_unitstr,
    l.id as sense_id,
    l.lemma as lemma
FROM tracker t
   LEFT JOIN tracker_unitandsynset uas ON (uas.tid=t.tid AND t.table='unitandsynset')
   LEFT JOIN tracker_synset ts ON (ts.tid=t.tid AND t.table='synset')
   LEFT JOIN lexicalunit l ON (uas.lex_id=l.id)
   LEFT JOIN synset s ON (s.id = uas.syn_id)
WHERE t.table in ("synset","unitandsynset")
AND ( uas.tid IS NOT NULL OR ts.tid IS NOT NULL )
AND ( t.inserted = 1 OR t.deleted = 1 OR t.data_before_change IS NOT NULL)
ORDER BY t.id DESC
