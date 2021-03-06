# Copyright (C) 2010 Mat Booth <mat@matbooth.co.uk>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from trac.core import TracError
from trac.ticket.admin import TicketAdminPanel
from trac.ticket.api import TicketSystem
from trac.util.translation import _
from trac.admin.web_ui import _save_config

from ticketvalidation.rules import TicketValidationRules

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
                    enabled = str(req.args.get('enabled')).strip()
                    assert name, 'Cannot save a rule with no name'
                    assert condition, 'Cannot save a rule with no condition'
                    if enabled == 'enabled':
                        enabled = 'True'
                    else:
                        enabled = 'False'

                    self._delete_rules(rule[0]['name'])

                    self.config.set('ticket-validation', name, condition)
                    self.config.set('ticket-validation', '%s.enabled' % name, enabled)
                    for opt in ('required', 'hidden'):
                        value = req.args.get(opt)
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
                               TicketSystem(self.env).get_ticket_fields() if f['name'] != 'status']
                    }

        # list view
        else:
            if req.method == 'POST':
                if req.args.get('add'):
                    name = str(req.args.get('name')).strip()
                    if name:
                        if name in [r['name'] for r in rules]:
                            raise TracError(_('A rule with this name already exists'))
                        self.config.set('ticket-validation', name, 'type == defect')
                        self.config.set('ticket-validation', '%s.enabled' % name, 'False')
                        _save_config(self.config, req, self.log)
                    req.redirect(req.href.admin(cat, page))
                elif req.args.get('remove'):
                    sel = req.args.get('sel')
                    if not sel:
                        raise TracError(_('No rules selected'))
                    self._delete_rules(sel)
                    _save_config(self.config, req, self.log)
                    req.redirect(req.href.admin(cat, page))

            data = {'view': 'list',
                    'rules': rules,
                    }

        data['label_singular'] = self._label[0]
        data['label_plural'] = self._label[1]
        return 'admin_ticketvalidation.html', data

    def _delete_rules(self, names):
        if not isinstance(names, list):
            names = [names]
        for name in names:
            self.config.remove('ticket-validation', name)
            for opt in ('required', 'hidden', 'enabled'):
                self.config.remove('ticket-validation', '%s.%s' % (name, opt))
        return
