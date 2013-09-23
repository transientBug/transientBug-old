#!/usr/bin/env python
"""
helper files for generating pagination from a list of objects

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import rethinkdb as r
from operator import itemgetter


def rethink_pager(query, request, sort="", perpage_default=24):
    perpage = request.getParam("perpage", perpage_default)
    page = request.getParam("page", 0)
    sort_dir = request.getParam("dir", "asc").lower()

    di = sort
    if sort_dir == "desc":
        di = r.desc(sort)
    if sort_dir == "asc":
        di = r.asc(sort)

    query = query.order_by(di)

    page_dict = {
        "perpage": perpage,
        "direction": sort_dir
        }

    if perpage != "all":
        page_dict["show_pager"] = True

        perpage = int(perpage)
        page = int(page)

        offset_start = (perpage * page)
        offset_end = offset_start + perpage

        length = query.count().run()

        if length <= perpage:
            page_dict["show_pager"] = False

        page_dict["next_page"] = page + 1
        page_dict["prev_page"] = page - 1

        if page != 0:
            page_dict["has_prev"] = True
        else:
            page_dict["has_prev"] = False

        if length > offset_end:
            page_dict["has_next"] = True
        else:
            page_dict["has_next"] = False

        query = query.skip(offset_start).limit(perpage)
    else:
        page_dict["show_pager"] = False

    results = list(query.run())

    return results, page_dict


def pager(pail, perpage, page, sort_dir="", sort=""):
    """
    Creates a pager for pail

    :param pail: A list of items to paginate
    :param perpage: An int or string of "all" for how many results per page
    :param page: An int or string for which page the pager is on
    :param sort_dir: The direction to sort, asc or desc
    """
    page_dict = {
        "perpage": perpage,
        "dir": sort_dir
        }

    if sort:
        pail.sort(key=itemgetter(sort), reverse=True)

    if sort_dir == "asc":
        pail.reverse()

    if perpage != "all":
        page_dict["show"] = True

        perpage = int(perpage)
        page = int(page)

        offset_start = (perpage * page)
        offset_end = offset_start + perpage

        page_dict["next"] = page + 1
        page_dict["prev"] = page - 1

        if len(pail) <= perpage:
            page_dict["show"] = False

        if page != 0:
            page_dict["hasPrev"] = True
        else:
            page_dict["hasPrev"] = False

        if len(pail) > offset_end:
            page_dict["hasNext"] = True
        else:
            page_dict["hasNext"] = False

        pail = pail[offset_start:offset_end]

    return pail, page_dict
