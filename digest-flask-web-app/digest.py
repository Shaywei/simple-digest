#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) Shay Weiss another.shay.weiss@gmail.com
import os
import time
import json
# import shelve
import hashlib
import logging
import argparse
import logging.handlers


import flask

log = logging.getLogger(__name__)


class DigestWebService(object):
    # TODO: use https://docs.python.org/3/library/shelve.html

    def __init__(self, digest_message_dict_path):
        self.app = flask.Flask(__name__)

        self.digest_message_dict_path = digest_message_dict_path

        if not os.path.exists(self.digest_message_dict_path):
            self._write_empty_db()
        else:
            try:
                self._load_db()
            except:
                self._write_empty_db()

        self.app.route('/messages', methods=['POST'])(self.store_digest)
        self.app.route('/messages/<path:request_path>',
                       methods=['GET'])(self.get_digest)
        self.app.route('/ping', methods=['GET'])(self.respond_to_ping)

    def _load_db(self):
        with open(self.digest_message_dict_path, 'r') as f:
            return json.loads(
                f.read().decode('string-escape').strip('"'))  # NOQA Because we're storing a "pretty" escaped json

    def _write_empty_db(self):
        with open(self.digest_message_dict_path, 'w') as f:
            f.write('{}')

    def _rewrite_db(self, new_db):
        with open(self.digest_message_dict_path, 'w') as f:
            f.write(json.dumps(new_db, indent=4, sort_keys=True))

    def _add_entry(self, digest, msg):
        digest_message_dict = self._load_db()
        digest_message_dict[digest] = msg
        self._rewrite_db(digest_message_dict)

    def _get_entry(self, digest):
        with open(self.digest_message_dict_path, 'r') as f:
            digest_message_dict = json.load(f)
            return digest_message_dict.get(digest)

    def store_digest(self):
        try:
            # print flask.request.headers
            msg = flask.request.get_json()["message"]
            log.info("Got message {}".format(msg))
            digest = hashlib.sha256(msg).hexdigest()
            self._add_entry(digest, msg)
            log.info("Successfully added {} to db".format(msg))
            return self._create_http_response(digest, 200)
        except:
            log.exception("Something went wrong while processing {}".format(
                flask.request.data))
            return self._create_http_response("FAIL! (is your input JSON and does it have a 'message' entry?)", 500)  # NOQA

    def get_digest(self, request_path):
        original_message = self._get_entry(request_path)
        log.info("Got GET request for {}".format(request_path))
        if original_message:
            return self._create_http_response(original_message, 200)
        return self._create_http_response(
            "NOT FOUND", 404, headers={"content-type": "text/plain"})

    def respond_to_ping(self):
        return self._create_http_response("All is well!", 200)

    @staticmethod
    def _create_http_response(message_str, status_code, headers=None):
        """Meant to be used mainly with Flask responses.
        See: http://flask.pocoo.org/docs/api/ and search for make_response(rv).
        """
        if not headers:
            headers = {}
        if "content-type" not in headers:
            headers["content-type"] = "application/json"
            message_str = {"message": str(message_str)}
        return json.dumps(message_str), status_code, headers


def _setup_logging(filename=None):
    """
    Configure the logging subsystem.
    Logs will reside in /var/log/upstart/
    """
    logging.root.handlers = []
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s+0000 - %(name)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime

    # urllib3 and werkzeug are spammy at level INFO, let's make it shut up
    for noisy in ("requests.packages.urllib3.connectionpool", "werkzeug"):
        l = logging.getLogger(noisy)
        l.setLevel(logging.WARNING)

    # Add log rotating file handler
    if filename:
        handler = logging.handlers.RotatingFileHandler(
            filename, maxBytes=1000000, backupCount=5)
        log.addHandler(handler)


def start_service(options):
    dws = DigestWebService(options.digest_db_path)
    dws.app.run(
        host=options.host,
        port=options.port)


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-l', '--logfile', default=False,
        action='store', help='Logfile Path')
    parser.add_argument(
        '-d', '--digest-db-path', action='store',
        required=True, help='Where to store the persistent state')
    parser.add_argument(
        '--host', action='store',
        default='0.0.0.0', help='Flask host conf')
    parser.add_argument(
        '-p', '--port', action='store', type=int,
        default=5000, help='Flask port conf')

    options = parser.parse_args()
    log.debug("Called from {} with options: {}".format(os.getcwd(), options))
    return options


if __name__ == '__main__':
    _setup_logging()
    options = _parse_args()

    logfile = options.logfile
    if logfile:
        log.info("log file at: {}".format(logfile))
        _setup_logging(logfile)

    start_service(options)
