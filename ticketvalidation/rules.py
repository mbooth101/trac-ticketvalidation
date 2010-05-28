# Copyright (C) 2010 Mat Booth <mat@matbooth.co.uk>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

try:
    import threading
except ImportError:
    import dummy_threading as threading

from pyparsing import *

from trac.core import implements, Component
from trac.ticket.api import ITicketManipulator
from trac.util.translation import _
from trac.web.api import ITemplateStreamFilter
from trac.web.chrome import ITemplateProvider

__all__ = ['TicketValidationRules']


class BoolOperator(object):
    ticket = None
    def __init__(self, t):
        self._args = t[0]
    def __str__(self):
        return "(" + " ".join(map(str,self._args)) + ")"

class BoolEquality(BoolOperator):
    def _expanded_args(self):
        """Generator that returns expanded arguments by replacing them with field
        values if they are ticket field names."""
        for a in self._args:
            field = [f for f in BoolOperator.ticket.fields if f['name'] == a]
            if field:
                yield BoolOperator.ticket.get_value_or_default(a)
            else:
                yield a
    def __nonzero__(self):
        # TODO: This implementation naively assumes we will only get 3 arguments.
        # It could really do with making better somehow.
        args = [a for a in self._expanded_args()]
        if args[1] == '==':
            return args[0] == args[2]
        if args[1] == '!=':
            return args[0] != args[2]

class BoolAnd(BoolOperator):
    def __nonzero__(self):
        for a in self._args[0::2]:
            v = bool(a)
            if not v:
                return False
        return True

class BoolOr(BoolOperator):
    def __nonzero__(self):
        for a in self._args[0::2]:
            v = bool(a)
            if v:
                return True
        return False


class TicketValidationRules(Component):
    """Main component of the ticket validation plug-in. Fetches the validation
    rules from the config, parses them and applies them appropriately."""

    implements(ITemplateProvider, ITicketManipulator, ITemplateStreamFilter)

    _rules = None

    def __init__(self):
        self._rules_lock = threading.RLock()
        
        # grammar definition for parsing rule conditions
        self._grammar = operatorPrecedence(Word(alphanums + '_') | quotedString.setParseAction(removeQuotes),
                                           [(oneOf('== !='), 2, opAssoc.LEFT, BoolEquality),
                                            (oneOf('and &&'), 2, opAssoc.LEFT, BoolAnd),
                                            (oneOf('or ||'), 2, opAssoc.LEFT, BoolOr),
                                            ])

    def _get_rules(self):
        rules = []
        config = self.config['ticket-validation']
        for name in [k for k,v in config.options() if '.' not in k]:
            # at least the condition must exist
            if config.get(name):
                rule = {
                        'name': name,
                        'condition': config.get(name),
                        'required': config.get('%s.required' % name).split(),
                        'hidden': config.get('%s.hidden' % name).split(),
                        }
                rules.append(rule)
            else:
                self.log.warning('ignoring rule "%s" without a condition' % name)
        rules.sort(lambda x, y: cmp(x['name'], y['name']))
        return rules

    # Public API

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
        """Iterate through all the ticket validation rules and if any them evaluate
        to true then the fields specified in that rule's "required" config will be
        mandatory. The user will not be able to submit the ticket until all mandatory
        fields have been changed away from their default value."""
        problems = []
        # TODO: It's possible a race condition to make the ticket a class attribute
        # of the BoolOperator... This needs thinking about -- maybe cleverer parse
        # in the grammar definition actions
        BoolOperator.ticket = ticket
        for r in self.get_rules():
            result = self._grammar.parseString(r['condition'])[0]
            b = bool(result)
            self.log.debug('required field rule "%s": %s is %s' % (r['name'], str(result), b))
            if b:
                for name in r['required']:
                    field = [f for f in ticket.fields if f['name'] == name]
                    default = field[0].get('value') or ''
                    current = ticket.get_value_or_default(name)
                    if default == current:
                        problems.append((field[0]['label'], _('This field is mandatory.')))
        return problems

    # ITemplateStreamFilter methods

    def filter_stream(self, req, method, filename, stream, data):
        """Iterate through all the ticket validation rules and if any them evaluate
        to true then the fields specified in that rule's "hidden" config will be
        hidden from the user on the ticket entry form."""
        if not req.path_info.startswith(('/newticket', '/ticket')):
            return stream
        # TODO: It's possible a race condition to make the ticket a class attribute
        # of the BoolOperator... This needs thinking about -- maybe cleverer parse
        # in the grammar definition actions
        BoolOperator.ticket = data['ticket']
        for r in self.get_rules():
            result = self._grammar.parseString(r['condition'])[0]
            b = bool(result)
            self.log.debug('hidden field rule "%s": %s is %s' % (r['name'], str(result), b))
            if b:
                for name in r['hidden']:
                    for f in data['fields']:
                        if f['name'] == name:
                            f['skip'] = True
        #TODO: Fettle the stream
        return stream
