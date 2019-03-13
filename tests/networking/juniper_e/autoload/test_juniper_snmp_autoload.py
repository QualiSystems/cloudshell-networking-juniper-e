import os
from unittest import TestCase, skip

import sys

from cloudshell.networking.juniper.autoload.juniper_snmp_autoload import JuniperSnmpAutoload
from mock import MagicMock as Mock, patch, call


class TestJuniperSnmpAutoload(TestCase):
    FIREWALL_SHELL = 'CS_Firewall'
    SWITCH_SHELL = 'CS_Switch'
    ROUTER_SHELL = 'CS_Router'
    NETWORKING_MODEL_TYPES = [SWITCH_SHELL, ROUTER_SHELL]
    FIREWALL_MODEL_TYPES = [FIREWALL_SHELL]

    def setUp(self):
        self._snmp_handler = Mock()
        self._shell_name = Mock()
        self._resource_name = Mock()
        self._logger = Mock()
        self._supported_os = Mock()
        self._resource = Mock()

    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.firewall_model')
    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.networking_model')
    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.JuniperSnmpAutoload._initialize_snmp_handler')
    def _create_instance(self, initialize_snmp_handler, networking_model, firewall_model, shell_type=SWITCH_SHELL):
        networking_model.AVAILABLE_SHELL_TYPES = self.NETWORKING_MODEL_TYPES
        firewall_model.AVAILABLE_SHELL_TYPES = self.FIREWALL_MODEL_TYPES
        if shell_type in self.NETWORKING_MODEL_TYPES:
            model = networking_model
        else:
            model = firewall_model
        model.GenericResource.return_value = self._resource

        instance = JuniperSnmpAutoload(self._snmp_handler, self._shell_name, shell_type,
                                       self._resource_name, self._logger)

        model.GenericResource.assert_called_once_with(shell_name=self._shell_name,
                                                      shell_type=shell_type,
                                                      name=self._resource_name,
                                                      unique_id=self._resource_name)
        initialize_snmp_handler.assert_called_once_with()
        return instance

    def _mock_methods(self, instance):
        instance._is_valid_device_os = Mock()
        instance.enable_snmp = Mock()
        instance.disable_snmp = Mock()
        instance._build_root = Mock()
        instance._build_chassis = Mock()
        instance._build_power_modules = Mock()
        instance._build_modules = Mock()
        instance._build_sub_modules = Mock()
        instance._build_ports = Mock()
        instance._root = Mock()
        instance._log_autoload_details = Mock()

    def test_init_firewall(self):
        instance = self._create_instance(shell_type=self.FIREWALL_SHELL)
        self.assertIs(instance.shell_name, self._shell_name)
        self.assertIs(instance.shell_type, self.FIREWALL_SHELL)
        self.assertIs(instance.shell_type, self.FIREWALL_SHELL)
        self.assertIsNone(instance._content_indexes)
        self.assertIsNone(instance._if_indexes)
        self.assertIs(instance._logger, self._logger)
        self.assertIs(instance._snmp_handler, self._snmp_handler)
        self.assertIs(instance._resource_name, self._resource_name)
        self.assertIs(instance.resource, self._resource)
        self.assertEqual(instance._chassis, {})
        self.assertEqual(instance._modules, {})
        self.assertEqual(instance.sub_modules, {})
        self.assertEqual(instance._ports, {})
        self.assertEqual(instance._logical_generic_ports, {})
        self.assertEqual(instance._physical_generic_ports, {})
        self.assertIsNone(instance._generic_physical_ports_by_name)
        self.assertIsNone(instance._generic_logical_ports_by_name)
        self.assertIsNone(instance._ipv4_table)
        self.assertIsNone(instance._ipv6_table)
        self.assertIsNone(instance._if_duplex_table)
        self.assertIsNone(instance._autoneg)
        self.assertIsNone(instance._lldp_keys)

    def test_init_switch(self):
        instance = self._create_instance(shell_type=self.SWITCH_SHELL)
        self.assertIs(instance.shell_name, self._shell_name)
        self.assertIs(instance.shell_type, self.SWITCH_SHELL)
        self.assertIsNone(instance._content_indexes)
        self.assertIsNone(instance._if_indexes)
        self.assertIs(instance._logger, self._logger)
        self.assertIs(instance._snmp_handler, self._snmp_handler)
        self.assertIs(instance._resource_name, self._resource_name)
        self.assertIs(instance.resource, self._resource)
        self.assertEqual(instance._chassis, {})
        self.assertEqual(instance._modules, {})
        self.assertEqual(instance.sub_modules, {})
        self.assertEqual(instance._ports, {})
        self.assertEqual(instance._logical_generic_ports, {})
        self.assertEqual(instance._physical_generic_ports, {})
        self.assertIsNone(instance._generic_physical_ports_by_name)
        self.assertIsNone(instance._generic_logical_ports_by_name)
        self.assertIsNone(instance._ipv4_table)
        self.assertIsNone(instance._ipv6_table)
        self.assertIsNone(instance._if_duplex_table)
        self.assertIsNone(instance._autoneg)
        self.assertIsNone(instance._lldp_keys)

    def test_logger_property(self):
        instance = self._create_instance()
        self.assertIs(instance.logger, self._logger)

    def test_snm_handler_property(self):
        instance = self._create_instance()
        self.assertIs(instance.snmp_handler, self._snmp_handler)

    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.sort_elements_by_attributes')
    def test_ipv4_table_prop(self, sort_elements_by_attributes):
        instance = self._create_instance()
        table = Mock()
        sort_elements_by_attributes.return_value = table
        walk_result = Mock()
        self._snmp_handler.walk.return_value = walk_result
        self.assertIs(instance.ipv4_table, table)
        self.assertIs(instance.ipv4_table, table)
        self._snmp_handler.walk.assert_called_once_with(('IP-MIB', 'ipAddrTable'))
        sort_elements_by_attributes.assert_called_once_with(walk_result, 'ipAdEntIfIndex')

    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.sort_elements_by_attributes')
    def test_ipv6_table_prop(self, sort_elements_by_attributes):
        instance = self._create_instance()
        table = Mock()
        sort_elements_by_attributes.return_value = table
        walk_result = Mock()
        self._snmp_handler.walk.return_value = walk_result
        self.assertIs(instance.ipv6_table, table)
        self.assertIs(instance.ipv6_table, table)
        self._snmp_handler.walk.assert_called_once_with(('IPV6-MIB', 'ipv6AddrEntry'))
        sort_elements_by_attributes.assert_called_once_with(walk_result, 'ipAdEntIfIndex')

    def test_generic_physical_ports_by_name_prop(self):
        instance = self._create_instance()
        port1 = Mock()
        port2 = Mock()
        instance._physical_generic_ports = {Mock(): port1, Mock(): port2}
        result1 = instance.generic_physical_ports_by_name
        result2 = instance.generic_physical_ports_by_name
        self.assertIs(result1, result2)
        self.assertEqual(result1, {port1.port_name: port1, port2.port_name: port2})

    def test_generic_logical_ports_by_name_prop(self):
        instance = self._create_instance()
        port1 = Mock()
        port2 = Mock()
        instance._logical_generic_ports = {Mock(): port1, Mock(): port2}
        result1 = instance.generic_logical_ports_by_name
        result2 = instance.generic_logical_ports_by_name
        self.assertIs(result1, result2)
        self.assertEqual(result1, {port1.port_name: port1, port2.port_name: port2})

    def test_lldp_keys_prop(self):
        instance = self._create_instance()
        result = Mock()
        instance._build_lldp_keys = Mock()
        instance._build_lldp_keys.return_value = result
        self.assertIs(instance.lldp_keys, result)
        self.assertIs(instance.lldp_keys, result)
        instance._build_lldp_keys.assert_called_once_with()

    def test_initialize_snmp_handler(self):
        instance = self._create_instance()
        instance._initialize_snmp_handler()
        path = os.path.abspath(
            os.path.join(os.path.dirname(sys.modules[JuniperSnmpAutoload.__module__].__file__), '..', 'mibs'))
        self._snmp_handler.update_mib_sources.assert_called_once_with(path)
        calls = [call('JUNIPER-MIB'), call('JUNIPER-IF-MIB'), call('IF-MIB'), call('JUNIPER-CHASSIS-DEFINES-MIB'),
                 call('IEEE8023-LAG-MIB'),
                 call('EtherLike-MIB'), call('IP-MIB'), call('IPV6-MIB'), call('LLDP-MIB')]
        self._snmp_handler.load_mib.assert_has_calls(calls)
        self._snmp_handler.set_snmp_errors.assert_called_once_with(instance.SNMP_ERRORS)

    def test_build_root(self):
        instance = self._create_instance()
        vendor = 'Test_Vendor'
        model = 'Tets_Model'
        version = '12.1R6.5'
        contact_name = Mock()
        system_name = Mock()
        location = Mock()
        self._snmp_handler.get_property.side_effect = ["{0}-testjnxProductName{1}".format(vendor, model),
                                                       "TEst JUNOS {} #/test".format(version),
                                                       contact_name,
                                                       system_name,
                                                       location]
        instance._build_root()
        self.assertIs(instance.resource.contact_name, contact_name)
        self.assertIs(instance.resource.system_name, system_name)
        self.assertIs(instance.resource.location, location)
        self.assertEqual(self._resource.os_version, version)
        self.assertEqual(self._resource.vendor, vendor.capitalize())
        self.assertEqual(self._resource.model, model)
        calls = [call('SNMPv2-MIB', 'sysObjectID', 0), call('SNMPv2-MIB', 'sysDescr', '0'),
                 call('SNMPv2-MIB', 'sysContact', '0'), call('SNMPv2-MIB', 'sysName', '0'),
                 call('SNMPv2-MIB', 'sysLocation', '0')]
        self._snmp_handler.get_property.assert_has_calls(calls)

    def test_build_root2(self):
        instance = self._create_instance()
        vendor = 'Test_Vendor'
        model = 'Tets_Model'
        version = '12.1R6.5'
        contact_name = Mock()
        system_name = Mock()
        location = Mock()
        self._snmp_handler.get_property.side_effect = [
            "{0}-testjnxProduct{1}".format(vendor, model),
            "TEst JUNOS {} #/test".format(version),
            contact_name,
            system_name,
            location
        ]

        instance._build_root()

        self.assertIs(instance.resource.contact_name, contact_name)
        self.assertIs(instance.resource.system_name, system_name)
        self.assertIs(instance.resource.location, location)
        self.assertEqual(self._resource.os_version, version)
        self.assertEqual(self._resource.vendor, vendor.capitalize())
        self.assertEqual(self._resource.model, model)
        calls = [call('SNMPv2-MIB', 'sysObjectID', 0), call('SNMPv2-MIB', 'sysDescr', '0'),
                 call('SNMPv2-MIB', 'sysContact', '0'), call('SNMPv2-MIB', 'sysName', '0'),
                 call('SNMPv2-MIB', 'sysLocation', '0')]
        self._snmp_handler.get_property.assert_has_calls(calls)

    def test_get_content_indexes(self):
        instance = self._create_instance()
        index1 = 1
        index2 = 2
        index3 = 3
        index4 = 4
        value1 = {'jnxContentsContainerIndex': 4}
        value2 = {'jnxContentsContainerIndex': 5}
        value3 = {'jnxContentsContainerIndex': 6}
        value4 = {'jnxContentsContainerIndex': 6}
        container_indexes = {index1: value1, index2: value2, index3: value3, index4: value4}
        self._snmp_handler.walk.return_value = container_indexes
        self.assertEqual(instance._get_content_indexes(), {4: [1], 5: [2], 6: [3, 4]})
        self._snmp_handler.walk.assert_called_once_with(('JUNIPER-MIB', 'jnxContentsContainerIndex'))

    def test_content_indexes_prop(self):
        instance = self._create_instance()
        value = Mock()
        instance._get_content_indexes = Mock()
        instance._get_content_indexes.return_value = value
        self.assertIs(instance.content_indexes, value)
        self.assertIs(instance.content_indexes, value)
        instance._get_content_indexes.assert_called_once_with()

    def test_if_indexes(self):
        instance = self._create_instance()
        result = Mock()
        value = Mock()
        value.keys.return_value = result
        self._snmp_handler.walk.return_value = value
        self.assertIs(instance.if_indexes, result)
        self.assertIs(instance.if_indexes, result)
        self._snmp_handler.walk.assert_called_once_with(('JUNIPER-IF-MIB', 'ifChassisPort'))
        value.keys.assert_called_once_with()

    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.AutoloadDetailsBuilder')
    def test_discover(self, autoload_details_builder_class):
        instance = self._create_instance()
        autoload_details_builder = Mock()
        autoload_details_builder_class.return_value = autoload_details_builder
        autoload_details = Mock()
        autoload_details_builder.autoload_details.return_value = autoload_details
        self._mock_methods(instance)
        self.assertIs(instance.discover(self._supported_os), autoload_details)
        instance._is_valid_device_os.assert_called_once_with(self._supported_os)
        instance._build_root.assert_called_once_with()
        instance._build_chassis.assert_called_once_with()
        instance._build_power_modules.assert_called_once_with()
        instance._build_modules.assert_called_once_with()
        instance._build_sub_modules.assert_called_once_with()
        instance._build_ports.assert_called_once_with()
        instance._log_autoload_details.assert_called_once_with(autoload_details)
        autoload_details_builder_class.assert_called_once_with(self._resource)
        autoload_details_builder.autoload_details.assert_called_once_with()
