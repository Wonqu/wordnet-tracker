from time import gmtime, strftime

from sqlalchemy import text

from tracker.extensions import db


def find_created_items_today():
    sql = text('SELECT  count(case when tr.inserted = 1 and tr.`table` = "synset" then  1 END) synset_created, \
                    count(case when tr.inserted = 1 and tr.`table` = "synsetrelation" then  1 END) synsetrelation_created, \
                    count(case when tr.inserted = 1 and tr.`table` = "lexicalunit" then  1 END) sense_created, \
                    count(case when tr.inserted = 1 and tr.`table` = "lexicalrelation" then  1 END) senserelation_created \
                FROM tracker tr WHERE DATE(tr.datetime) = :now GROUP BY DATE(tr.datetime)')

    return db.engine.execute(sql, {'now': strftime("%Y-%m-%d", gmtime())})


def find_user_activity_now(today):
    sql = text('SELECT tr.user, TIME_FORMAT(tr.datetime, "%H:00"), count(tr.id) \
                FROM tracker tr WHERE DATE(tr.datetime) = :today \
                GROUP BY tr.user, hour( tr.datetime ) order by  hour( tr.datetime )')
    return db.engine.execute(sql, {'today': today})
