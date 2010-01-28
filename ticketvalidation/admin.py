# Copyright (C) 2010 Mat Booth <mat@matbooth.co.uk>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from trac.ticket.admin import TicketAdminPanel
from trac.ticket.api import TicketSystem
from trac.util.translation import _
from trac.admin.web_ui import _save_config

from ticketvalidation.main import TicketValidationRules

__all__ = ['TicketValidationAdminPanel']


class TicketValidationAdminPanel(TicketAdminPanel):
    """Provides an admin panel for configuring ticket validation rules."""

    _type = 'validation'
    _label = (_('Validation Rule'), _('Validation Rules'))

    # IAdminPanelProvider methods

    def _render_admin_panel(self, req, cat, page, path_info):
        rules = TicketValidationRules(self.env).get_rules()
        rule = [r for r in rules if r['name'] == path_info]

        # detail view
        if path_info and rule:
            if req.method == 'POST':
                if req.args.get('save'):
                    name = str(req.args.get('name')).strip()
                    condition = str(req.args.get('condition')).strip()
                    assert name, 'Cannot save a rule with no name'
                    assert condition, 'Cannot save a rule with no condition'
                    self.config.remove('ticket-validation', rule[0]['name'])
                    self.config.set('ticket-validation', name, condition)

                    for opt in ('required', 'hidden'):
                        value = req.args.get(opt)
                        self.config.remove('ticket-validation',
                                           '%s.%s' % (rule[0]['name'], opt))
                        if isinstance(value, list):
                            self.config.set('ticket-validation',
                                            '%s.%s' % (name, opt), " ".join(value))
                        else:
                            self.config.set('ticket-validation',
                                            '%s.%s' % (name, opt), value)

                    _save_config(self.config, req, self.log)
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
