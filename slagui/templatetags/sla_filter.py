from django import template
from slagui.slaformat import guiformatter

register = template.Library()

@register.filter
def removeChars(value, args):
	"Removes all values of arg from the given string, separate by ,"
	if args is None:
		return False
	arg_list = [arg.strip() for arg in args.split(',')]
	print(arg_list)
	for item in arg_list:
		print(item)
		value = value.replace(item, "")
	return value

@register.filter
def humanReadableMetric(metric, showUnits=False):
	return guiformatter.humanReadableMetric(metric, showUnits)

@register.filter
def formatConstraint(unformattedConstraint):
	return guiformatter.formatConstraint(unformattedConstraint)

@register.filter
def getIntervalFromPolicy(policy):
	return guiformatter.getIntervalFromPolicy(policy)