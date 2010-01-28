# Copyright (C) 2010 Mat Booth <mat@matbooth.co.uk>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from trac.core import implements, Component
from trac.admin.api import IAdminPanelProvider
from trac.ticket.api import TicketSystem
from trac.util.translation import _

from ticketvalidation.main import TicketValidationRules

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
        rules = TicketValidationRules(self.env).get_rules()
        rule = [r for r in rules if r['name'] == path_info]

        # detail view
        if path_info and rule:
            if req.method == 'POST':
                if req.args.get('save'):
                    req.redirect(req.href.admin(cat, page))
                elif req.args.get('cancel'):
                    req.redirect(req.href.admin(cat, page))

            data = {'view': 'detail',
                    'rule': rule[0],
                    'fields': [{'name': f['name'], 'label': f['label']} for f in
                               TicketSystem(self.env).get_ticket_fields()]
                    }

        # list view
        else:
            data = {'view': 'list',
                    'rules': rules,
                    }

        data['label_singular'] = self._label[0]
        data['label_plural'] = self._label[1]
        return 'admin_ticketvalidation.html', data
