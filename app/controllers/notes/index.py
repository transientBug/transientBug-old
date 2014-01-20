#!/usr/bin/env python
"""
main index listing for notes - reroutes to login if you're not logged in

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2014
http://joshashby.com
joshuaashby@joshashby.com
"""
from seshat.route import route
from seshat_addons.MixedObject import MixedObject
from seshat_addons.objectMods import template
from seshat_addons.funcMods import HTML

from utils.paginate import Paginate

import rethinkdb as r
from rethinkORM import RethinkCollection
import models.rethink.note.noteModel as nm


@route()
@template("public/notes/index", "Notes")
class index(MixedObject):
    @HTML
    def GET(self):
        parts = r.table(nm.Note.table).filter({"disable": False})

        if self.request.session.id:
            what_type = self.request.get_param("filter", "all")

            if what_type=="private":
                parts = parts.filter({"public": False})
            elif what_type=="public":
                parts = parts.filter({"public": True})

            self.view.data = {"type": what_type.lower()}

        else:
            parts = parts.filter({"public": True})

        result = RethinkCollection(nm.Note, query=parts)
        page = Paginate(result, self.request, "created", sort_direction="asc")

        self.view.data = {"page": page}

        return self.view
