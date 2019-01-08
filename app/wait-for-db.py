#!/bin/usr/env python
import re
from optparse import OptionParser
import socket
import time
import sys

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


class OptionException(Exception):
    def __init__(self, value):
        self.value = value


class wait_for_app:
    def log(self, loginfo):
        if self.options.quiet is not False:
            print(loginfo)

    def build_log(self, type, app, time=0):
        # 1=enable_timeout,2=disable_timeout,3=success_msg,4=unavailable,5=timeout_msg
        loginfo = {
            1: "%s: waiting %d seconds for %s" % (sys.argv[0], time, app),
            2: "%s: waiting for %s without a timeout" % (sys.argv[0], app),
            3: "%s: %s is available after %d seconds" % (sys.argv[0], app, time),
            4: "%s: %s is unavailable" % (sys.argv[0], app),
            5: "%s: timeout occurred after waiting %d seconds for %s" % (sys.argv[0], time, app),
        }.get(type)
        return loginfo

    def wait_for(self, db_url, timeout):
        start_ts = int(time.time())
        diff_ts = 0
        engine = create_engine(db_url)
        db_url_sanitized = re.sub(':.+@', ':****:****@', db_url)
        while diff_ts < timeout:
            time.sleep(15)
            try:
                sk = socket.socket()
                logmsg = self.build_log(2, db_url_sanitized, timeout)
                if timeout != 0:
                    logmsg = self.build_log(1, db_url_sanitized, timeout - diff_ts)
                    sk.settimeout(timeout)
                self.log(logmsg)

                con = engine.connect()

                logmsg = self.build_log(3, db_url_sanitized, diff_ts)
                self.log(logmsg)
                con.close()
                sys.exit(0)
            except OperationalError:
                logmsg = self.build_log(4, db_url_sanitized)
                self.log(logmsg)
            end_ts = int(time.time())
            diff_ts = end_ts - start_ts

    def get_parser(self):
        parser = OptionParser()
        parser.add_option('-u', '--url', dest='url', help='Database URL')
        parser.add_option('-t', '--timeout', dest='timeout', default='15',
                          help='Timeout in seconds, zero for no timeout')
        parser.add_option('-q', '--quiet', dest='quiet', action='store_false', help='Don\'t output any status messages')
        return parser

    def verify_options(self):
        if self.options.url is None:
            raise OptionException("The url must be set!")

    def start_up(self):
        parser = self.get_parser()
        try:
            self.options, self.args = parser.parse_args()
            self.verify_options()
        except OptionException as err:
            print(err)
            parser.print_help()

        self.wait_for(self.options.url, int(self.options.timeout))


if __name__ == '__main__':
    w = wait_for_app()
    w.start_up()
