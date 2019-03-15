from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.networking.juniper_e.command_templates.generic_action_error_map import ERROR_MAP

COMMIT = CommandTemplate('commit', error_map=ERROR_MAP)
ROLLBACK = CommandTemplate('rollback', error_map=ERROR_MAP)
