from django import template
from django.template import Library, Node, TemplateSyntaxError

register = Library()

class SplitListNode(Node):
    def __init__(self, list_string, chunk_size, new_list_name):
        self.list = list_string
        self.chunk_size = chunk_size
        self.new_list_name = new_list_name

    def split_seq(self, seq, size):
        return [seq[i:i+size] for i in range(0, len(seq), size)]

    def render(self, context):
        context[self.new_list_name] = self.split_seq(context[self.list], int(self.chunk_size))
        return ''


@register.tag()
def split_list(parser, token):
    bits = token.contents.split()
    if len(bits) != 5:
        raise TemplateSyntaxError, "split_list list as new_list 5"
    return SplitListNode(bits[1], bits[4], bits[3])


class GroupListNode(Node):
    def __init__(self, source_list, group_property, new_list_name):
        self.source_list = template.Variable(source_list)
        self.group_property = group_property
        self.new_list_name = new_list_name

    def render(self, context):
        source_list = self.source_list.resolve(context)
        group_property = self.group_property.replace('"','').replace("'",'')
        new_list = list(set(map(lambda x:getattr(x, group_property, None), source_list)))
        context[self.new_list_name] = new_list
        return ''


@register.tag()
def group_list(parser, token):
    bits = token.split_contents()
    if len(bits) != 5:
        raise TemplateSyntaxError, "group_list list as new_list [group property]"
    return GroupListNode(bits[1], bits[4], bits[3])

# group_list = register.tag(group_list)
