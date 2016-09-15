# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#
from oslo_db.sqlalchemy import models
from sqlalchemy.ext import declarative
from sqlalchemy import orm, Column, Integer

    
class EAuthModel(models.SoftDeleteMixin,
               models.TimestampMixin,
               models.ModelBase):
    """Base class for Zen Models."""

    __table_args__ = {'mysql_engine': 'InnoDB'}

    @declarative.declared_attr
    def __tablename__(cls):
        # NOTE(jkoelker) use the pluralized name of the class as the table
        return cls.__name__.lower() + 's'

    def __iter__(self):
        self._i = iter(orm.object_mapper(self).columns)
        return self

    def next(self):
        n = next(self._i).name
        return n, getattr(self, n)

    __next__ = next

    def __repr__(self):
        """sqlalchemy based automatic __repr__ method."""
        items = ['%s=%r' % (col.name, getattr(self, col.name))
                 for col in self.__table__.columns]
        return "<%s.%s[object at %x] {%s}>" % (self.__class__.__module__,
                                               self.__class__.__name__,
                                               id(self), ', '.join(items))

    def save(self, session=None):
        from authhub.db import api

        if session is None:
            session = api.get_session()
        super(EAuthModel, self).save(session=session)


class HasId(object):
    """id mixin, add to subclasses that have an id."""

    id = Column(Integer, primary_key=True, autoincrement=True)

BASE = declarative.declarative_base(cls=EAuthModel)
