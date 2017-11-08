# -*- coding: utf-8 -*-
#
# File: utils.py
#
# Copyright (c) 2017 by Imio.be
#
# GNU General Public License (GPL)
#

from imio.zamqp.core.utils import next_scan_id


def next_scan_id_pm():
    return next_scan_id(
        file_portal_types=['annex', 'annexDecision'],
        cliend_id_var='client_id',
        scan_type='3')
