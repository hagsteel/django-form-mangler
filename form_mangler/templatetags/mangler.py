from django import template
from django.forms import widgets
from django.template.loader import get_template
from django.template import Context

register = template.Library()


def get_widget_template_name(field):
    if isinstance(field.widget, widgets.TextInput):
        return 'widgets/text_input_field.html'
    if isinstance(field.widget, widgets.Textarea):
        return 'widgets/textarea_field.html'
    elif isinstance(field.widget, widgets.CheckboxSelectMultiple):
        return 'widgets/checkbox_select_multiple.html'
    # elif isinstance(field.widget, widgets.Select) and hasattr(field.widget.choices, 'queryset'):
    #     return 'widgets/select_queryset.html'
    elif isinstance(field.widget, widgets.Select):
        return 'widgets/select.html'
    elif isinstance(field.widget, widgets.CheckboxInput):
        return 'widgets/checkbox.html'
    else:
        return 'widgets/default.html'


class MangleWidgetNode(template.Node):
    def __init__(self, field_name, extra_attributes):
        self.extra_attributes = extra_attributes
        self.field_name = field_name
        self.field = template.Variable(field_name)

    def render(self, context):
        bound_field = self.field.resolve(context)
        extra_attributes = dict(self.extra_attributes)
        widget_template = get_template(get_widget_template_name(bound_field.field))
        value = bound_field.value()
        if isinstance(bound_field.field.widget, widgets.PasswordInput):
            value = ''
        return widget_template.render(Context({
            'bound_field': bound_field,
            'attributes': [{'key': a, 'value': extra_attributes[a]} for a in extra_attributes ],
            'value': value,
        }))


@register.tag()
def mangle_widget(parser, token):
    contents = token.split_contents()
    extra_attributes = {}
    if len(contents) > 2:
        for a in contents[2:]:
            kv = a.split('=')
            key = kv[0]
            value = kv[1]
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            extra_attributes[key] = value
    field_name = contents[1]
    # extra_attributes['class'] = 'form-control'
    return MangleWidgetNode(field_name, extra_attributes)
