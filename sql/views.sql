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

CREATE VIEW view_tracker_synsets_relations_history AS
SELECT
 t.id as id, t.datetime, t.user,
case
	when t.inserted = 1 then 'created'
	when t.deleted = 1 then 'removed'
end as operation,
tparent.ID as source_id,
tparent.unitsstr as source_unitstr,
rtype.ID as relation_id,
rtype.name as relation_name,
tchild.ID as target_id,
tchild.unitsstr as target_unitstr
FROM tracker t
LEFT JOIN `tracker_synsetrelation` tsyn ON (tsyn.tid = t.tid AND t.table='synsetrelation')
LEFT JOIN `relationtype` rtype ON (rtype.ID=tsyn.REL_ID)
LEFT JOIN `synset` tparent ON (tparent.ID=tsyn.PARENT_ID)
LEFT JOIN `synset` tchild ON (tchild.ID=tsyn.CHILD_ID)
WHERE t.table = "synsetrelation"
AND ( t.inserted = 1 OR t.deleted = 1 OR t.data_before_change IS NOT NULL)
ORDER BY t.id DESC

CREATE VIEW view_tracker_sense_relations_history AS
SELECT
 t.id as id, t.datetime, t.user,
case
	when t.inserted = 1 then 'created'
	when t.deleted = 1 then 'removed'
end as operation,
tparent.ID as source_id,
concat(tparent.lemma,' ',tparent.variant) as source_unitstr,
rtype.ID as relation_id,
rtype.name as relation_name,
tchild.ID as target_id,
concat(tchild.lemma,' ',tchild.variant) as target_unitstr
FROM tracker t
LEFT JOIN `tracker_lexicalrelation` tsyn ON (tsyn.tid = t.tid AND t.table='lexicalrelation')
LEFT JOIN `relationtype` rtype ON (rtype.ID=tsyn.REL_ID)
LEFT JOIN `lexicalunit` tparent ON (tparent.ID=tsyn.PARENT_ID)
LEFT JOIN `lexicalunit` tchild ON (tchild.ID=tsyn.CHILD_ID)
WHERE t.table = "lexicalrelation"
AND ( t.inserted = 1 OR t.deleted = 1 OR t.data_before_change IS NOT NULL)
ORDER BY t.id DESC
