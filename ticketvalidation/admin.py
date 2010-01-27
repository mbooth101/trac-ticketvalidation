# Copyright (C) 2010 Mat Booth <mat@matbooth.co.uk>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from trac.core import implements, Component
from trac.admin.api import IAdminPanelProvider
from trac.util.translation import _
from trac.web.chrome import add_script

__all__ = ['TicketValidationAdminPanel']


class TicketValidationAdminPanel(Component):
    """Provides an admin panel for configuring ticket validation rules."""

    implements(IAdminPanelProvider)

    _label = (_('Validation Rule'), _('Validation Rules'))

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if 'TICKET_ADMIN' in req.perm:
            yield ('ticket', 'Ticket System', 'validation', self._label[1])

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require('TICKET_ADMIN')
        data = {}
        data['label_singular'] = self._label[0]
        data['label_plural'] = self._label[1]
        return 'admin_ticketvalidation.html', data
