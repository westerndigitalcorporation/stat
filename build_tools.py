#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

from services import abstract_method


class BuildTools(object):

    def __init__(self, *args):
        pass

    @abstract_method
    def getAttributes(self): pass


class GccBuildTools(BuildTools):

    def getAttributes(self):
        return {}
