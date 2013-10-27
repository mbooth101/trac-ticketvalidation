# Welcome to TicketValidation

TicketValidation is a plug-in for Trac that adds support for conditionally required or hidden fields. The plug-in allows you to make built-in or custom fields required or hidden based on configurable boolean conditions.

## Installation and Usage

Install the TicketValidation plug-in:

    $ easy_install -Z https://www.matbooth.co.uk/svn/trunk/ticketvalidation/

Ensure the plug-in is enabled in trac.ini:

    [components]
    ticketvalidation.* = enabled

Once configured, Trac administrators will find a new ticket system admin panel for maintaining ticket validation rules.
