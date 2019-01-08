from tracker.blueprints.tracker_admin.models import AdminQuery


def test_admin_query_validation():
    test_queries = [
        ("select * from collocation where id=1", True),
        ("select * from dblock where id=1", True),
        ("select * from emotion where id=1", True),
        ("select * from errorreasontype where id=1", True),
        ("select * from extgraph where id=1", True),
        ("select * from extgraphevaluation where id=1", True),
        ("select * from extgraphextension where rank=0", True),
        ("select * from iplimit where id=1", True),
        ("select * from iplog where id=1", True),
        ("select * from lexicalrelation where valid=0", True),
        ("select * from lexicalunit where id=1", True),
        ("select * from message where id=1", True),
        ("select * from parameter where id=1", True),
        ("select * from pkglock where id=1", True),
        ("select * from projects where id=1", True),
        ("select * from proposedconnectiontype where id=1", True),
        ("select * from relationtype where id=1", True),
        ("select * from synset where id=1", True),
        ("select * from synsetrelation where valid=0", True),
        ("select * from temp_english_synsets where id=1", True),
        ("select * from test where id=1", True),
        ("select * from tracker where id=1", True),
        ("select * from tracker_lexicalrelation where valid=0", True),
        ("select * from tracker_synset where id=1", True),
        ("select * from tracker_synsetrelation where valid=1", True),
        ("select * from tracker_unitandsynset where LEX_ID=0", True),
        ("select * from unitandsynset where LEX_ID=0", True),
        ("select * from unitdistance where id=1", True),
        ("select * from usage_examples where id=1", True),
        ("select * from wordforms where id=1", True),
        ("select * from test;select * from mysql.user", False),
        ("select * from test;select * from users", False),
        ("select * from test;select email, password from users", False),
        ("select * from test;delete from test where name='test'", False),
        ("select * from test;insert into test (id, name) VALUES (1, 'test')", False),
        ("select * from test;create table test (id int auto_increment)", False),
        ("select * from test;truncate table 'test'", False),
        ("select * from test;drop database test", False),
        ("select * from test;begin work", False),
        ("select * from test;start transaction", False),
        ("select * from test;commit", False),
        ("select * from test;describe test", False),
        ("select * from test;show tables", False),
        ("select * from test;show databases", False),
        ("select * from test;show index from test", False),
        ("select * from test;use sys; select * from config", False),
        ("select * from test;create user 'super_admin'@'127.0.0.1' IDENTIFIED by '1234'", False),
        ("select * from test;grant all on test to 'super_admin'@'127.0.0.1'", False),
        ("select * from test;set test=00", False),
    ]
    for (q, correct) in test_queries:
        try:
            print(q)  # for debug purposes
            AdminQuery().validate_query_text(None, q)
            assert correct
        except ValueError:
            assert (not correct)
