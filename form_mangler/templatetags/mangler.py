from django import template
from django.forms import widgets
from django.template.loader import get_template
from django.template import Context

register = template.Library()


def get_widget_template_name(field, use_bootstrap=False):
    widget_dir = 'widgets'
    if use_bootstrap:
        widget_dir = 'widgets/bootstrap3'

    if isinstance(field.widget, widgets.DateInput):
        return '{}/date_input_field.html'.format(widget_dir)
    if isinstance(field.widget, widgets.TextInput):
        return '{}/text_input_field.html'.format(widget_dir)
    if isinstance(field.widget, widgets.Textarea):
        return '{}/textarea_field.html'.format(widget_dir)
    elif isinstance(field.widget, widgets.CheckboxSelectMultiple):
        return '{}/checkbox_select_multiple.html'.format(widget_dir)
    elif isinstance(field.widget, widgets.Select):
        return '{}/select.html'.format(widget_dir)
    elif isinstance(field.widget, widgets.CheckboxInput):
        return '{}/checkbox.html'.format(widget_dir)
    else:
        return '{}/default.html'.format(widget_dir)


class MangleWidgetNode(template.Node):
    def __init__(self, field_name, extra_attributes, use_bootstrap):
        self.extra_attributes = extra_attributes
        self.field_name = field_name
        self.field = template.Variable(field_name)
        self.use_bootstrap = use_bootstrap

    def render(self, context):
        bound_field = self.field.resolve(context)
        extra_attributes = dict(self.extra_attributes)
        widget_template = get_template(get_widget_template_name(bound_field.field, self.use_bootstrap))
        value = bound_field.value()
        if isinstance(bound_field.field.widget, widgets.PasswordInput):
            value = ''
        return widget_template.render(Context({
            'bound_field': bound_field,
            'attributes': [{'key': a, 'value': extra_attributes[a]} for a in extra_attributes ],
            'value': value,
        }))


@register.tag()
def mangle_widget(parser, token, use_bootstrap=False):
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
    return MangleWidgetNode(field_name, extra_attributes, use_bootstrap)


@register.tag()
def mangle_widget_bs3(parser, token):
    return mangle_widget(parser, token, use_bootstrap=True)
