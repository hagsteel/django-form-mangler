from django import template
from django.forms import widgets
from django.template.loader import get_template
from django.template import Context
from django.utils.encoding import force_text

register = template.Library()


def get_widget_template_name(field, use_bootstrap=False):
    widget_dir = 'widgets'
    if use_bootstrap:
        widget_dir = 'widgets/bootstrap3'
    if isinstance(field.widget, widgets.TextInput):
        return '{}/text_input_field.html'.format(widget_dir)
    if isinstance(field.widget, widgets.Textarea):
        return '{}/textarea_field.html'.format(widget_dir)
    elif isinstance(field.widget, widgets.CheckboxSelectMultiple):
        return '{}/checkbox_select_multiple.html'.format(widget_dir)
    elif isinstance(field.widget, widgets.SelectMultiple):
        return '{}/select_multiple.html'.format(widget_dir)
    elif isinstance(field.widget, widgets.Select):
        return '{}/select.html'.format(widget_dir)
    elif isinstance(field.widget, widgets.CheckboxInput):
        return '{}/checkbox.html'.format(widget_dir)
    elif isinstance(field.widget, widgets.ClearableFileInput):
        return '{}/file.html'.format(widget_dir)
    elif isinstance(field.widget, widgets.FileInput):
        return '{}/file.html'.format(widget_dir)
    else:
        return '{}/default.html'.format(widget_dir)


def add_bs3_form_control_class(attributes):
    if 'class' in attributes:
        if 'form-control' in attributes['class']:
            return attributes
        attributes['class'] += ' form-control'
        return attributes
    attributes['class'] = 'form-control'
    return attributes


def render_field(field, extra_attributes=None, use_bootstrap=False):
    widget_template = get_template(get_widget_template_name(field.field, use_bootstrap))
    widget = field.field.widget
    value = field.value()
    if value is not None:
        if isinstance(widget, widgets.Input):
            value = force_text(widget._format_value(value))
        else:
            value = force_text(field.value())
        if isinstance(widget, widgets.PasswordInput):
            value = ''

    attributes = field.field.widget.attrs
    if extra_attributes:
        for k, v in extra_attributes.items():
            if k == 'class' and k in attributes:
                attributes[k] += ' {}'.format(v)
            else:
                attributes[k] = v

    if use_bootstrap and not isinstance(field.field.widget, widgets.CheckboxInput):
        attributes = add_bs3_form_control_class(attributes)
    return widget_template.render(Context({
        'bound_field': field,
        'attributes': attributes,
        'value': value,
    }))



class MangleWidgetNode(template.Node):
    def __init__(self, field_name, extra_attributes, use_bootstrap):
        self.extra_attributes = extra_attributes
        self.field_name = field_name
        self.field = template.Variable(field_name)
        self.use_bootstrap = use_bootstrap

    def render(self, context):
        bound_field = self.field.resolve(context)
        extra_attributes = dict(self.extra_attributes)
        return render_field(bound_field, extra_attributes, self.use_bootstrap)


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


class MangleFormNode(template.Node):
    def __init__(self, form):
        self.form = template.Variable(form)

    def render(self, context):
        form = self.form.resolve(context)
        output = ''
        for field in form.visible_fields():
            output += render_field(field, use_bootstrap=True)
        return output


@register.tag()
def mangle_form_bs3(parser, token):
    contents = token.split_contents()
    form = contents[1]
    return MangleFormNode(form)
