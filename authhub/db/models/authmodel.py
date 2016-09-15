# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

import sqlalchemy as sa
from sqlalchemy import orm
from authhub.db import model_base


class Users(model_base.BASE, model_base.HasId):

    __tablename__ = 'users'
    __table_args__ = (
        sa.schema.UniqueConstraint("username", "deleted", name="user_deleted"),
        sa.Index('user_deleted_index', 'deleted'),
        sa.Index('user_email_index', 'email'),
        sa.Index('user_status_index', 'status'),
    )
    username = sa.Column(sa.String(20), nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
    type = sa.Column(sa.String(60), nullable=False) # type of user
    phone = sa.Column(sa.String(60))
    email = sa.Column(sa.String(60))
    status = sa.Column(sa.String(16), default="ACTIVE")
    privilege = sa.Column(sa.Integer, default=9)
    last_login_time = sa.Column(sa.DateTime)
    description = sa.Column(sa.String(255), default='')


class Groups(model_base.BASE, model_base.HasId):

    __tablename__ = 'groups'
    __table_args__ = (
        sa.schema.UniqueConstraint("groupname", "deleted", name="group_deleted"),
        sa.Index('group_deleted_index', 'deleted'),
        sa.Index('group_status_index', 'status'),
    )
    groupname = sa.Column(sa.String(255), nullable=False)
    type = sa.Column(sa.String(60), nullable=False) # type of group
    status = sa.Column(sa.String(16), default="ACTIVE") # group status
    description = sa.Column(sa.String(255), default='')


class GroupUser(model_base.BASE):
    __tablename__ = 'group_user'
    __table_args__ = (
        sa.schema.PrimaryKeyConstraint("user_id", "group_id", name="pk_group_user"),
    )
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'))
    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id', ondelete='CASCADE'))
    user = orm.relationship('Users', foreign_keys=[user_id])
    group = orm.relationship('Groups', foreign_keys=[group_id])


class Roles(model_base.BASE, model_base.HasId):

    __tablename__ = 'roles'
    __table_args__ = (
        sa.schema.UniqueConstraint("name", "deleted", name="role_deleted"),
    )
    name = sa.Column(sa.String(20), nullable=False)
    description = sa.Column(sa.String(255), default='')


class UserRole(model_base.BASE):
    __tablename__ = 'user_role'
    __table_args__ = (
        sa.schema.PrimaryKeyConstraint("user_id", "role_id", name="pk_user_role"),
    )
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = sa.Column(sa.Integer, sa.ForeignKey('roles.id', ondelete='CASCADE'))
    user = orm.relationship('Users', foreign_keys=[user_id])
    role = orm.relationship('Roles', foreign_keys=[role_id])
