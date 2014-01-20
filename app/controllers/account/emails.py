#!/usr/bin/env python
"""
For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2014
http://joshashby.com
joshuaashby@joshashby.com
"""
from seshat.route import route
from seshat_addons.MixedObject import MixedObject
from seshat_addons.objectMods import login, template
from seshat_addons.funcMods import HTML

import rethinkdb as r
from models.rethink.user import userModel as um


@route()
@login()
@template("public/account/emails", "Emails")
class emails(MixedObject):
    @HTML
    def GET(self):
        user = um.User(self.request.session.id)

        self.view.partial("tabs",
                          "partials/public/account/tabs",
                          {"user": user,
                           "command": "emails"})

        self.view.data = {"user": user}
        return self.view
