__author__ = 'root'

class UtilHelper(object):


	_metric_type = {
		'CPULoad': 'xs:double',
		'NrUSERS': 'xs:decimal',
		'SWAPfree': 'xs:double',
		'RAMUsed': 'xs:double',
		'NrProcs': 'xs:decimal',
		'DiskUsed': 'xs:decimal',
		'NrZOMBIEprocs': 'xs:decimal'
	}

	_metric_location = {
		'CPULoad': 'orion/CPULoad',
		'NrUSERS': 'orion/NrUSERS',
		'SWAPfree': 'orion/SWAPfree',
		'RAMUsed': 'orion/RAMUsed',
		'NrProcs': 'orion/NrProcs',
		'DiskUsed': 'orion/DiskUsed',
		'NrZOMBIEprocs': 'orion/NrZOMBIEprocs'
	}

	_guarantee_cons_list = {
		'0': 'GT',
		'1': 'GE',
		'2': 'EQ',
		'3': 'LT',
		'4': 'LE',
		'5': 'NE',
		'6': 'BETWEEN',
		'7': 'IN'
	}

	_trento_vm_list = {
		'0': 'vm-Trento:10.250.3.105',
		'1': 'vm-Trento:10.250.3.101',
		'2': 'vm-Trento:193.205.211.67',
		'3': 'vm-Trento:10.250.3.102',
		'4': 'vm-Trento:10.250.3.104',
		'5': 'vm-Trento:10.250.3.103',
		'6': 'vm-Trento:10.250.3.111',
		'7': 'vm-Trento:193.205.211.66',
		'8': 'host|Trento:node-1'
	}

	agr_service_host_map = {
		'0f6c0631-c819-4df7-bdd8-5fccd94530f2': 'node-3'
	}
	agr_node_host_map = {
		'Trento': 'node-3',
		'Lannion': 'node-5'
	}
	
	@staticmethod
	def correlate_host(node, uuid):
		try:
			idHost = UtilHelper.agr_service_host_map[uuid]
		except KeyError:
			try:
				idHost= UtilHelper.agr_node_host_map[node]
			except KeyError:
				idHost=""
		return idHost
		