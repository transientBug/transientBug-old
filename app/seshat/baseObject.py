#!/usr/bin/env python
"""
Seshat
Web App/API framework built on top of gevent
baseObject to build pages off of

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2012
http://joshashby.com
joshuaashby@joshashby.com
"""
from views.template import template
import json
import traceback


class baseHTTPObject(object):
        __login__ = False
        _groups   = []

        """
        Base HTTP page response object
        This determins which REQUEST method to send to,
        along with authentication level needed to access the object.
        """
        def __init__(self, request):
            self.request = request
            self.post_init_hook()

        def post_init_hook(self):
            pass

        def build(self):
            content = ""

            if self.__login__ and not self.request.session.userID:
                self.request.session.pushAlert("You need to be logged in to view this page.", level="error")
                print "login please"
                self._redirect("/login")
                return "", self.head

            if self._groups and (not self.request.session.has_perm("root") \
               or not len(set(self._groups).union(self.request.session.groups)) >= 1):
                    self.request.session.pushAlert("You are not authorized to perfom this action.", "error")
                    print "not authorized please"
                    self._redirect("/")
                    return "", self.head

            self.pre_content_hook()
            try:
                content = getattr(self, self.request.method)() or ""
                content = self.post_content_hook(content)
                if content: content = unicode(content)
            except Exception as e:
                content = (e, traceback.format_exc())

            if self.head[0] != "303 SEE OTHER":
                del self.request.session.alerts

            return content, self.head

        def pre_content_hook(self):
            pass

        def post_content_hook(self, content):
            return content

        def _404(self):
            self.head = ("404 NOT FOUND", [])

        def _redirect(self, loc):
            self.head = ("303 SEE OTHER", [("Location", loc)])

        def HEAD(self):
            """
            This is wrong since it should only return the headers... technically...
            """
            return self.GET()

        def GET(self):
            pass

        def POST(self):
            pass

        def PUT(self):
            pass

        def DELETE(self):
            pass


class HTMLObject(baseHTTPObject):
    def post_init_hook(self):
        self.head = ("200 OK", [("Content-Type", "text/html")])

        try:
            title = self._title
        except:
            title = "untitled"

        self.request.title = title

    def pre_content_hook(self):
        try:
          tmpl = self._defaultTmpl
          self.view = template(tmpl, self.request)
        except:
          self.view = ""

    def post_content_hook(self, content):
        if type(content) == template:
            return content.render()
        else:
            return content


class JSONObject(baseHTTPObject):
    def post_init_hook(self):
        self.head = ("200 OK", [("Content-Type", "application/json")])

    def post_content_hook(self, content):
        response = [{"status": self.head[0], "data": content}]

        return json.dumps(response)
