from cloudshell.devices.flows.snmp_action_flows import AutoloadFlow
from cloudshell.networking.juniper_e.autoload.juniper_e_snmp_autoload import JuniperESNMPAutoload


class JuniperSnmpAutoloadFlow(AutoloadFlow):
    def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
        with self._snmp_handler.get_snmp_service() as snpm_service:
            juniper_snmp_autoload = JuniperESNMPAutoload(snpm_service,
                                                         shell_name,
                                                         shell_type,
                                                         resource_name,
                                                         self._logger)
            return juniper_snmp_autoload.discover(supported_os)
