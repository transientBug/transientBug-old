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

from seshat.actions import NotFound

from errors.general import NotFoundError

from models.rethink.user import userModel as um

import rethinkdb as r
from rethinkORM import RethinkCollection
import models.rethink.phot.photModel as pm
from utils.paginate import Paginate

from models.utils import dbUtils as dbu


@route()
@login(["admin"])
@template("admin/users/phots", "User Phots")
class phots(MixedObject):
    @HTML
    def GET(self):
        self.view.partial("sidebar", "partials/admin/sidebar", {"command": "users"})
        try:
            user = um.User(self.request.id)

        except NotFoundError:
            return NotFound()

        self.view.title = user.username

        self.view.partial("tabs",
                          "partials/admin/users/tabs",
                          {"user": user,
                           "command": self.request.command})

        disabled = self.request.get_param("q")
        hidden_ids = r.table(pm.Phot.table).filter({"user": user.id}).filter(r.row["disable"].eq(True)).concat_map(lambda doc: [doc["id"]]).coerce_to("array").run()

        if disabled == "enabled":
            query = r.table(pm.Phot.table).filter({"user": user.id}).filter(lambda doc: ~r.expr(hidden_ids).contains(doc["id"]))

        else:
            query = r.table(pm.Phot.table).filter({"user": user.id}).filter(lambda doc: r.expr(hidden_ids).contains(doc["id"]))

        res = RethinkCollection(pm.Phot, query=query)

        page = Paginate(res, self.request, "created", sort_direction="desc")

        self.view.data = {"page": page}

        return self.view
