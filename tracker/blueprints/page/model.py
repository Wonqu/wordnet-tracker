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


def find_user_activity_now(today, user):
    if user != '':
        user = user.replace(" ", ".")
        sql = text('SELECT CASE WHEN tr.user IS NULL THEN "Auto" ELSE tr.user END, TIME_FORMAT(tr.datetime, "%H:00"), count(tr.id) \
                        FROM tracker tr WHERE DATE(tr.datetime) = :today AND tr.user=:user_name \
                        GROUP BY tr.user, hour( tr.datetime ) order by  hour( tr.datetime )')
        return db.engine.execute(sql, {'today': today, 'user_name': user})
    else:
        sql = text('SELECT CASE WHEN tr.user IS NULL THEN "Auto" ELSE tr.user END, TIME_FORMAT(tr.datetime, "%H:00"), count(tr.id) \
                FROM tracker tr WHERE DATE(tr.datetime) = :today \
                GROUP BY tr.user, hour( tr.datetime ) order by  hour( tr.datetime )')
        return db.engine.execute(sql, {'today': today})


def find_user_activity_month(year, month, user):
        user = user.replace(" ", ".")
        sql = text('SELECT tr.user, DATE_FORMAT(tr.datetime, "%d"), count(tr.id) \
                        FROM tracker tr WHERE YEAR(tr.datetime) = :yr AND MONTH(tr.datetime)=:mnth AND tr.user=:user_name \
                        GROUP BY tr.user, day( tr.datetime ) order by day( tr.datetime )')

        return db.engine.execute(sql, {'yr': year,'mnth': month, 'user_name': user})
