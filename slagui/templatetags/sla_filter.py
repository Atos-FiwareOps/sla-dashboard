from django import template

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
