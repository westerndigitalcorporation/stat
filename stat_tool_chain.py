#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

class StatToolchain(object):

    def getCommandToCompile(self):
        raise NotImplementedError('Method "{0}" is not implemented'.format(self.getCommandToCompile.__name__))