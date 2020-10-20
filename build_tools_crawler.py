#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT
import platform

from msvs_tools import MsvsTools
from stat_configuration import StatConfiguration
from services import meta_class, SingletonMeta


class BuildToolsCrawler(meta_class(SingletonMeta, object)):

    def __init__(self):
        self.__msvsTools = MsvsTools(StatConfiguration()) if platform.system() == "Windows" else None
        self.__tools = [tools for tools in (self.__msvsTools,) if tools]

    def retrieveMsvs(self):
        """
        :rtype: MsvsTools
        """
        return self.__msvsTools

    def getBuildAttributes(self):
        return dict(*(tools.getAttributes() for tools in self.__tools))
