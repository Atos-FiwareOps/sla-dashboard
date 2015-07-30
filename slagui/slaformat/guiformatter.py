import re

def paramunparse(params):
	result = ""
	for k, v in params.iteritems():
		result += k + "=" + v + "&"
	return result.rstrip('&')

def humanReadableMetric(measureUnit, showUnits=False):
	units = ""
	if showUnits:
		units += u" (in %)"
	
	if measureUnit == u"percDiskUsed":
		return u"Used disk" + units
	elif measureUnit == u"bwd_status":
		return u"Bandwidth status"
	elif measureUnit == u"percRAMUsed":
		return u"Used RAM" + units
	elif measureUnit == u"sysUptime":
		return u"Availability" + units
	elif measureUnit == u"percCPULoad":
		return u"Used CPU" + units
	else:
		return measureUnit;

def machineReadableMetric(measureUnit):
	if u"Used disk" in measureUnit:
		return u"percDiskUsed"
	elif u"Bandwidth status" in measureUnit:
		return u"bwd_status"
	elif u"Used RAM" in measureUnit:
		return u"percRAMUsed"
	elif u"Availability" in measureUnit:
		return u"sysUptime"
	elif u"Used CPU" in measureUnit:
		return u"percCPULoad"
	else:
		return measureUnit;

def formatConstraint(unformattedConstraint):
	formattedConstraint = ""
	constraintElements = unformattedConstraint.split(" ")
	
	for element in constraintElements[1:]:
		formattedConstraint += element
		formattedConstraint += " "
			
	return formattedConstraint

def getIntervalFromPolicy(policy):
	apiPolicyRE = "^.+breach, (\d+).+$"
	humanReadablePolicyRE = "^Over (\d+).+$"
	
	if re.search(apiPolicyRE, policy):
		policy_obj = re.search(apiPolicyRE, policy)
	elif re.search(humanReadablePolicyRE, policy):
		policy_obj = re.search(humanReadablePolicyRE, policy)
	else:
		raise ValueError(u"Policy is not well formatted")
	
	interval = policy_obj.group(1)
	return interval