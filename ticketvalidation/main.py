# Copyright (C) 2010 Mat Booth <mat@matbooth.co.uk>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

try:
    import threading
except ImportError:
    import dummy_threading as threading

from trac.core import implements, Component
from trac.ticket.api import ITicketManipulator
from trac.web.chrome import ITemplateProvider

__all__ = ['TicketValidationPlugin']


class TicketValidationPlugin(Component):
    """Main component of the ticket validation plug-in. Fetches the validation
    rules from the config and applies them when the user submits the ticket. If
    any fields are found to violate the rules, the submission is disallowed and
    the user is chastised."""

    implements(ITemplateProvider, ITicketManipulator)

    def __init__(self):
        self._rules_lock = threading.RLock()

    def _get_rules(self):
        rules = []
        config = self.config['ticket-validation']
        for name in [k for k,v in config.options() if '.' not in k]:
            rule = {
                    'name': name,
                    'condition': config.get(name),
                    }
            rules.append(rule)
        rules.sort(lambda x, y: cmp(x['name'], y['name']))
        return rules

    # Public API

    _rules = None

    def get_rules(self):
        """Returns the list of ticket validation rules. Rules are cached in memory
        after the first time this is called."""
        if self._rules is None:
            self._rules_lock.acquire()
            try:
                if self._rules is None: # double-checked locking
                    self._rules = self._get_rules()
            finally:
                self._rules_lock.release()
        return [r.copy() for r in self._rules]

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        """Return the directories containing static resources."""
        from pkg_resources import resource_filename
        return [('ticketvalidation', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        """Return the directories containing templates."""
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

    # ITicketManipulator methods

    def prepare_ticket(self, req, ticket, fields, actions):
        """This API is not called by Trac, but should be implemented anyway."""
        pass

    def validate_ticket(self, req, ticket):
        """This API is called by Trac when the user tries to submit a ticket.
        This is where the magic happens."""
        rules = self.get_rules()
        problems = []
        print rules
        print ticket.fields
        return problems
