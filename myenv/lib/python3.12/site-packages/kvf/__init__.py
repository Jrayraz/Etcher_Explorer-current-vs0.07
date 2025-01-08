import os.path
from collections import OrderedDict, UserDict
import braq
import paradict


def get_config(filename, *, type_ref=None,
               obj_builder=None):
    root_dir = os.path.dirname(os.path.abspath(filename))
    with open(filename, "r", encoding="utf-8") as file:
        return parse(file, type_ref=type_ref,
                     root_dir=root_dir,
                     obj_builder=obj_builder)


def put_config(sections, filename, *, spacing=1,
               type_ref=None, bin_to_text=False,
               attachments_dir="attachments"):
    root_dir = os.path.dirname(os.path.abspath(filename))
    with open(filename, "w", encoding="utf-8") as file:
        s = render(sections, spacing=spacing,
                   mode=paradict.CONFIG_MODE, type_ref=type_ref,
                   bin_to_text=bin_to_text, root_dir=root_dir,
                   attachments_dir=attachments_dir)
        file.write(s)


def load(file, *, type_ref=None,
         obj_builder=None, root_dir=None):
    if root_dir is None:
        try:
            root_dir = os.path.dirname(os.path.abspath(file.name))
        except AttributeError as e:
            root_dir = None
    return parse(file,
                 type_ref=type_ref,
                 root_dir=root_dir,
                 obj_builder=obj_builder,
                 end_of_stream="===")

def dump(sections, file, *, spacing=1, mode=paradict.CONFIG_MODE,
         type_ref=None, bin_to_text=False, root_dir=None,
         attachments_dir="attachments"):
    if bin_to_text:
        root_dir = None
    else:
        if root_dir is None:
            try:
                root_dir = os.path.dirname(os.path.abspath(file.name))
            except AttributeError as e:
                root_dir = None
    s = render(sections, spacing=spacing, mode=mode,
               type_ref=type_ref, bin_to_text=bin_to_text,
               root_dir=root_dir, attachments_dir=attachments_dir)
    file.write(s)


def parse(s, *, type_ref=None, root_dir=None,
          obj_builder=None):
    r = dict()
    d = braq.decode(s, end_of_stream="===")
    for header, body in d.items():
        r[header] = paradict.decode("\n".join(body), type_ref=type_ref,
                                    obj_builder=obj_builder,
                                    root_dir=root_dir)
    return r


def render(sections, *, spacing=1, mode=paradict.CONFIG_MODE,
           type_ref=None, bin_to_text=True,
           root_dir=None, attachments_dir="attachments"):
    s = list()
    for header, body in _iterate(sections):
        str_body = paradict.encode(body,
                                   mode=mode,
                                   type_ref=type_ref,
                                   bin_to_text=bin_to_text,
                                   root_dir=root_dir,
                                   attachments_dir=attachments_dir)
        section = braq.Section(header, str_body)
        s.append(section)
    return braq.render(s, spacing=spacing)


def _iterate(sections):
    if isinstance(sections, (dict, OrderedDict, UserDict)):
        it = sections.items()
    else:
        it = sections
    for header, body in it:
        yield header, body
