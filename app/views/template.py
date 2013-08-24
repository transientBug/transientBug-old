#!/usr/bin/env python
"""
TEMPLATE ALL THE THINGS WITH HANDLEBARS!!!!
Uses the mustache templating language to make a base template object by which is
easy to work with in the controllers, and a walker and templateFile objects
which provide automatic reading and rereading in debug mode of template files.

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import pystache
import os
import time
import config.config as c
import logging
import yaml

logger = logging.getLogger(c.general["logName"]+".views")

tmplPath = os.path.dirname(__file__)+"/mustache/"

tmpls = {}


class templateFile(object):
    def __init__(self, fileBit):
        """
        Reads in fileBit into memory, and sets the modified time for the
        object to that of the file at the current moment.
        """
        self._file = ''.join([tmplPath, fileBit])
        self._mtime = 0

        self.config = {}

        self.readTemplate()

    @property
    def template(self):
        """
        Returns the template, while reading it in if the file has been
        modified since we first read it in, and only if we are in debug
        mode. Otherwise this will just return the template stored in memory
        from first read/startup.
        """
        if c.general["debug"]:
            self.readTemplate()

        return self._template

    def readTemplate(self):
        """
        Read in the template only if it has been modified since we first
        read it into our `_template`
        """
        mtime = time.ctime(os.path.getmtime(self._file))

        if self._mtime < mtime:
            if c.general["debug"]:
                logger.debug("""\n\r============== Template =================
    Rereading template into memory...
    TEMPLATE:  %s
    OLD MTIME: %s
    NEW MTIME: %s
""" % (self._file, self._mtime, mtime))
            with open(self._file, "r") as openTmpl:
                raw = unicode(openTmpl.read())
            self._mtime = mtime

            if raw[:3] == "+++":
                config, template = raw.split("+++", 2)[1:]
                self.config = yaml.load(config)
                self._template = template
            else:
                self._template = raw


class template(object):
    def __init__(self, template, data):
        self._baseData = {
            "req": data,
            "stylesheets": [],
            "scripts": [],
        }

        self._template = template
        self._base = "skeleton_empty"

        self._render = ""

    @property
    def skeleton(self):
        return self._base

    @skeleton.setter
    def skeleton(self, value):
        assert type(value) == str
        self._base = value

    @skeleton.deleter
    def skeleton(self):
        self._base = "skeleton_empty"

    @property
    def data(self):
        return self._baseData

    @data.setter
    def data(self, value):
        assert type(value) == dict
        self._baseData.update(value)

    @property
    def scripts(self):
        return self._baseData["scripts"]

    @scripts.setter
    def scripts(self, value):
        assert type(value) == list
        self._baseData["scripts"].extend(value)

    @scripts.deleter
    def scripts(self):
        self._baseData["scripts"] = []

    @property
    def stylesheets(self):
        return self._baseData["stylesheets"]

    @stylesheets.setter
    def stylesheets(self, value):
        assert type(value) == list
        self._baseData["stylesheets"].extend(value)

    @stylesheets.deleter
    def stylesheets(self):
        self._baseData["stylesheets"] = []

    def partial(self, placeholder, template, data):
        data.update(self._baseData)
        self._data[placeholder] = pystache.render(template, data)

    def render(self):
        _data = self._baseData
        _data["req"].session.renderAlerts()

        template = tmpls[self._template]
        _data.update(template.config)

        body = pystache.render(template.template, _data)

        if "base" in template.config and template.config["base"] is not None:
            _data.update({
                "body"  : body,
            })

            self._render = pystache.render(tmpls[template.config["base"]].template, _data)
        elif self._base is not None:
            _data.update({
                "body"  : body,
            })

            self._render = pystache.render(tmpls[self._base].template, _data)
        else:
            self._render = body

        return unicode(self._render)

    def __str__(self):
        return unicode(self._render)


for top, folders, files in os.walk(tmplPath):
    for fi in files:
        base = top.split(tmplPath)[1]
        file_name, extension = fi.rsplit('.', 1)
        if extension == "mustache":
            name = '/'.join([base, file_name]).lstrip('/')
            fi = '/'.join([base, fi])
            tmpls[name] = templateFile(fi)
