from datetime import datetime, timedelta
from time import gmtime, strftime

from flask_sqlalchemy import xrange
from sqlalchemy import text

from tracker.extensions import db, cache


def find_created_items_today():
    sql = text(
        """
        SELECT count(case when tr.inserted = 1 and tr.`table` = "synset" then  1 END) synset_created,
               count(case when tr.inserted = 1 and tr.`table` = "synsetrelation" then  1 END) synsetrelation_created,
               count(case when tr.inserted = 1 and tr.`table` = "lexicalunit" then  1 END) sense_created,
               count(case when tr.inserted = 1 and tr.`table` = "lexicalrelation" then  1 END) senserelation_created 
        FROM tracker tr WHERE DATE(tr.datetime) = :now GROUP BY DATE(tr.datetime)
        """
    )

    return db.engine.execute(sql, {'now': strftime("%Y-%m-%d", gmtime())})


def find_user_activity_now(today, user):
    if user != '':
        user = user.replace(" ", ".")
        sql = text(
            """
            SELECT CASE WHEN tr.user IS NULL THEN "Auto" ELSE tr.user END, TIME_FORMAT(tr.datetime, "%H:00"), count(tr.id)
            FROM tracker tr WHERE DATE(tr.datetime) = :today AND tr.user=:user_name
            GROUP BY tr.user, TIME_FORMAT(tr.datetime, "%H:00") order by TIME_FORMAT(tr.datetime, "%H:00")
            """
        )
        return db.engine.execute(sql, {'today': today, 'user_name': user})
    else:
        sql = text(
            """
            SELECT CASE WHEN tr.user IS NULL THEN "Auto" ELSE tr.user END, TIME_FORMAT(tr.datetime, "%H:00"), count(tr.id)
            FROM tracker tr WHERE DATE(tr.datetime) = :today
            GROUP BY tr.user, TIME_FORMAT(tr.datetime, "%H:00") order by TIME_FORMAT(tr.datetime, "%H:00")
            """
        )
        return db.engine.execute(sql, {'today': today})


def user_activity_cached(day, user, update=False, timeout=3600):
    cache_key = "USER_ACTIVITY_NOW_{}_{}".format(day, user)

    result = cache.get(cache_key)
    if update:
        result = None
    if result is not None:
        d, users = result
    else:
        active = find_user_activity_now(day, user)

        start_date = datetime(2018, 1, 1, 0, 0, 0)
        d = []
        v = []
        users = set()
        for x in active:
            v.append(x)
            users.add(x[0])

        for td in (start_date + timedelta(hours=1 * it) for it in xrange(24)):
            row = dict()
            row['y'] = td.strftime("%H:%M")
            for u in users:
                row[u] = 0
            d.append(row)

        for r in v:
            for item in range(0, len(d)):
                if d[item]['y'] == r[1]:
                    d[item][r[0]] = r[2]

        cache.set(cache_key, (d, users), timeout=timeout)
    return d, users


def find_user_activity_month(year, month, user):
        user = user.replace(" ", ".")
        sql = text(
            """
            SELECT tr.user, DATE_FORMAT(tr.datetime, "%d"), count(tr.id)
            FROM tracker tr WHERE YEAR(tr.datetime) = :yr AND MONTH(tr.datetime)=:mnth AND tr.user=:user_name
            GROUP BY tr.user, DATE_FORMAT( tr.datetime , "%d") order by DATE_FORMAT( tr.datetime , "%d")
            """
        )

        return db.engine.execute(sql, {'yr': year,'mnth': month, 'user_name': user})
