#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

from build_tools import BuildTools
from msvs_tools import MsvsTools
from stat_configuration import StatConfiguration
from services import meta_class, SingletonMeta


class BuildToolsCrawler(meta_class(SingletonMeta, object)):

    def __init__(self):
        self.__tools = MsvsTools(StatConfiguration())

    def retrieve(self):
        """
        :rtype: BuildTools
        """
        return self.__tools
