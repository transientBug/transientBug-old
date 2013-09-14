#!/usr/bin/env python
"""
Seshat
Web App/API framework built on top of gevent
Main framework app

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import config.config as c

import logging
logger = logging.getLogger(c.general["logName"]+".seshat.request")

import Cookie
import re
import urllib
import uuid

import models.redis.session.sessionModel as sm
import models.redis.bucket.bucketModel as bm
import models.redis.announcement.announcementModel as am


def split_members(item):
    members = {}
    raw = {}
    for part in item.split("&"):
        query = part.split("=")
        if query[0]:
            if len(query) > 1:
                raw.update({query[0]: query[1]})
                members.update({re.sub("\+", " ", query[0]): urllib.unquote(re.sub("\+", " ", query[1]))})
            else:
              raw.update({part: None})
    return members, raw


class requestItem(object):
    def __init__(self, env):
        self._env = env
        self.buildParams()
        self.buildCookie()
        self.buildSession()
        self.buildCfg()

        self.method = self._env["REQUEST_METHOD"]
        self.url = env["PATH_INFO"]
        self.remote = env["HTTP_X_REAL_IP"] if "HTTP_X_REAL_IP" in env else "Unknown IP"
        self.user_agent = env["HTTP_USER_AGENT"] if "HTTP_USER_AGENT" in env else "Unknown User Agent"
        self.referer = env["HTTP_REFERER"] if "HTTP_REFERER" in env else "No Referer"

        self.id = None

    def buildParams(self):
        all_mem = {}
        all_raw = {}

        # GET Params
        members, raw = split_members(self._env["QUERY_STRING"])
        all_mem.update(members)
        all_raw.update(raw)

        # POST Params
        members, raw = split_members(self._env["wsgi.input"].read())
        all_mem.update(members)
        all_raw.update(raw)

        if len(all_raw) == 0:
            bits = self._env["PATH_INFO"].split("?", 1)
            if len(bits) > 1:
                members, raw = split_members(bits[1])
                all_mem.update(members)
                all_raw.update(raw)

        self.params = all_mem
        self.rawParams = all_raw

    def buildCookie(self):
        cookie = Cookie.SimpleCookie()
        try:
            cookie.load(self._env["HTTP_COOKIE"])
            self.sessionCookie = { value.key: value.value for key, value in cookie.iteritems() }
            self.sessionID = self.sessionCookie["bug_sid"]
        except:
            self.sessionID = str(uuid.uuid4())
            self.sessionCookie = {"bug_sid": self.sessionID}

    def buildSession(self):
        self.session = sm.session("session:"+self.sessionID)

    def buildCfg(self):
        self.cfg = bm.cfgBuckets()
        self.announcements = am.CfgAnnouncements()

    @property
    def has_announcements(self):
        return len(self.announcements._data) >= 1

    def generateHeader(self, header, length):
        for morsal in self.sessionCookie:
            cookieHeader = ("Set-Cookie", ("%s=%s")%(morsal, self.sessionCookie[morsal]))
            header.append(cookieHeader)

        header.append(("Content-Length", str(length)))
        header.append(("Server", self._env["SERVER_SOFTWARE"]))
        header.append(("X-Seshat-Says", "Ello!"))
        return header

    def getParam(self, param, default="", cast=str):
        try:
            p = self.params[param]
            if cast and cast != str:
                p = cast(p)
            else:
                if p == "True" or p == "true":
                    p = True
                elif p == "False" or p == "false":
                    p = False
            return p
        except:
            return default
