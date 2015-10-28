# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import json
import logging
import datetime
import PyRSS2Gen

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relation

from relengapi.blueprints.treestatus import types
from relengapi.lib import db

log = logging.getLogger(__name__)


class DbTree(db.declarative_base('relengapi')):
    __tablename__ = 'treestatus_trees'
    tree = Column(String(32), primary_key=True)
    status = Column(String(64), default="open", nullable=False)
    reason = Column(Text, default="", nullable=False)
    message_of_the_day = Column(Text, default="", nullable=False)

    def to_json(self):
        return types.JsonTree(
            tree=self.tree,
            status=self.status,
            reason=self.reason,
            message_of_the_day=self.message_of_the_day,
        )


class DbTreeRss(db.declarative_base('relengapi')):
    __tablename__ = 'treestatus_trees'
    tree = Column(String(32), primary_key=True)
    status = Column(String(64), default="open", nullable=False)
    reason = Column(Text, default="", nullable=False)
    message_of_the_day = Column(Text, default="", nullable=False)

    def to_rss(self):
        rss = PyRSS2Gen.RSS2(
        title = "Andrew's PyRSS2Gen feed",
        link = "http://www.dalkescientific.com/Python/PyRSS2Gen.html",
        description = "The latest news about PyRSS2Gen, a ",

        lastBuildDate = datetime.datetime.now(),

        items = [
        PyRSS2Gen.RSSItem(
        title = "PyRSS2Gen-0.0 released",
        link = "http://www.dalkescientific.com/news/030906-PyRSS2Gen.html",
        description = "Dalke Scientific today announced PyRSS2Gen-0.0, ",
        guid = PyRSS2Gen.Guid("http://www.dalkescientific.com/news/"),
        pubDate = datetime.datetime(2003, 9, 6, 21, 31)),
        PyRSS2Gen.RSSItem(
        title = "Thoughts on RSS feeds for bioinformatics",
        link = "http://www.dalkescientific.com/writings/diary/",
        description = "One of the reasons I wrote PyRSS2Gen was to ",
        guid = PyRSS2Gen.Guid("http://www.dalkescientific.com/writings/"),
        pubDate = datetime.datetime(2003, 9, 6, 21, 49)),
        ])

        rss.write_xml(open("pyrss2gen.rss", "w"))
        return "ugh"


class DbLog(db.declarative_base('relengapi')):
    __tablename__ = 'treestatus_log'

    id = Column(Integer, primary_key=True)
    tree = Column(String(32), nullable=False, index=True)
    when = Column(db.UTCDateTime, nullable=False, index=True)
    who = Column(Text, nullable=False)
    status = Column(String(64), nullable=False)
    reason = Column(Text, nullable=False)
    _tags = Column("tags", Text, nullable=False)

    def __init__(self, tags=None, **kwargs):
        if tags is not None:
            kwargs['_tags'] = json.dumps(tags)
        super(DbLog, self).__init__(**kwargs)

    @hybrid_property
    def tags(self):
        return json.loads(self._tags)

    def to_json(self):
        return types.JsonTreeLog(
            tree=self.tree,
            when=self.when,
            who=self.who,
            status=self.status,
            reason=self.reason,
            tags=self.tags,
        )


class DbStatusChange(db.declarative_base('relengapi')):
    __tablename__ = 'treestatus_changes'
    id = Column(Integer, primary_key=True)
    who = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    when = Column(db.UTCDateTime, nullable=False, index=True)
    status = Column(String(64), nullable=False)

    def to_json(self):
        return types.JsonStateChange(
            trees=[t.tree for t in self.trees],
            status=self.status,
            when=self.when,
            who=self.who,
            reason=self.reason,
            id=self.id,
        )


class DbStatusChangeTree(db.declarative_base('relengapi')):
    __tablename__ = 'treestatus_change_trees'
    id = Column(Integer, primary_key=True)
    stack_id = Column(Integer, ForeignKey(DbStatusChange.id), index=True)
    tree = Column(String(32), nullable=False, index=True)
    last_state = Column(Text, nullable=False)

    stack = relation(DbStatusChange, backref='trees')
