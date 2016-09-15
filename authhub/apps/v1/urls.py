# -*- coding: utf-8 -*-
from authhub.apps.v1.group_view import GroupViewSet
from authhub.apps.v1.group_user_view import GroupUserViewSet

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

'''
    This is the main api route for EAuth service.
    default api version is v1.
'''

from rest_framework.routers import DefaultRouter
from authhub.apps.v1.token_views import TokenViewSet
from authhub.apps.v1.user_views import UserViewSet
from authhub.apps.v1.user_role_views import UserRoleViewSet
from authhub.apps.v1.role_views import RoleViewSet
from rest_framework_nested import routers as NestedRouters
from django.conf.urls import patterns, include, url

router = DefaultRouter()
router.register(r'tokens', TokenViewSet, 'token')
router.register(r'users', UserViewSet, 'user')
router.register(r'groups', GroupViewSet, 'group')
router.register(r'roles', RoleViewSet, 'role')

#register nested routers roles for user
user_role_router = NestedRouters.NestedSimpleRouter(router, r'users', lookup='user')
user_role_router.register(r'roles', UserRoleViewSet, base_name='user-roles')

#register nested routers groups and users
group_user_router = NestedRouters.NestedSimpleRouter(router, r'groups', lookup='group')
group_user_router.register(r'users', GroupUserViewSet, base_name='group-users')

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^', include(user_role_router.urls)),
    url(r'^', include(group_user_router.urls)),
)
