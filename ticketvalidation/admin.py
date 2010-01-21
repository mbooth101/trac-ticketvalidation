# Copyright (C) 2010 Mat Booth <mat@matbooth.co.uk>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from trac.core import implements, Component
from trac.admin.api import IAdminPanelProvider
from trac.util.translation import _
from trac.web.chrome import add_script


class TicketValidationAdminPanel(Component):
    """Provides an admin panel for ticket validation config."""

    implements(IAdminPanelProvider)

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if 'TICKET_ADMIN' in req.perm:
            yield ('ticket', 'Ticket System', 'validation', 'Field Validation')

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require('TICKET_ADMIN')
        data = {}
        return 'admin_ticketvalidation.html', data
