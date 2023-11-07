from __future__ import annotations


__all__ = [
        'DataList',
        'Li',
        'A',
        'Span',
        'H1',
        'H2',
        'H3',
        'H4',
        'H5',
        'H6',
        'Div',
        'BaseElement',
        'Element',
        'Option',
        'HR',
        'Ol',
        'Ul',
        'BaseTagNamedElement',
        'Button',
        'ElementStyles',
        'ElementMeta',
        'ElementHTMX',
        'ElementChildren',
        'ElementBooleanAttributes',
        'ElementAttributes',
        'ElementClassNames',
        'Script'
]

import io
from abc import ABC
from collections import deque, UserDict, UserList, UserString
from collections.abc import Sequence
from contextlib import contextmanager
from enum import Enum
from typing import Any, Callable, ClassVar, Literal, Optional, overload, Union
from typing_extensions import Self

from . import functions as fn


EMPTY: tuple[str, ...] = (
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'meta', 'param', 'source',
        'track', 'wbr'
)

TAGS: tuple[str, ...] = (
        'a', 'address', 'area', 'abbr', 'article', 'aside', 'audio', 'body', 'b', 'base', 'bdi', 'bdo', 'blockquote',
        'br', 'button', 'canvas', 'caption', 'cite', 'code', 'col', 'colgroup', 'data', 'datalist', 'dd', 'del',
        'details', 'dfn', 'div', 'dialog', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'footer',
        'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'hr', 'html', 'i', 'iframe', 'img', 'input',
        'ins', 'kbd', 'label', 'legend', 'li', 'link', 'main', 'map', 'mark', 'meta', 'meter', 'nav', 'nonscript',
        'object', 'ol', 'optgroup', 'output', 'p', 'param', 'picture', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby',
        's', 'samp', 'script', 'section', 'select', 'small', 'source', 'span', 'strong', 'style', 'sub', 'summary',
        'sup', 'svg', 'table', 'tbody', 'td', 'template', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr',
        'track', 'u', 'ul', 'var', 'video', 'wbr'
)

FORM_FIELDS: tuple[str, ...] = ('input', 'select', 'textarea')

INPUT_TYPES: tuple[str, ...] = (
        'button', 'checkbox', 'color', 'date', 'datetime-local', 'email', 'file', 'hidden', 'image', 'month', 'number',
        'password', 'radio', 'range', 'reset', 'search', 'submit', 'tel', 'text', 'time', 'url', 'week'
)

# BOOTSTRAP_ICON_LINK: str = ('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/boots'
#                             'trap-icons.css">')
# BOOTSTRAP_LINK: str = ('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="styles'
#                        'heet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" cross'
#                        'origin="anonymous">')
# BOOTSTRAP_SCRIPT: str = ('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" '
#                          'integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorig'
#                          'in="anonymous"></script>')
#
# META_CHARSET_UTF8: str = '<meta charset="utf-8" ></meta>'
# META_VIEWPORT: str = '<meta name="viewport" content="width=device-width, initial-scale=1" ></meta>'
# HTML_TITLE: str = '<title></title>'

class TagEnum(Enum):
    _ignore_ = 'TagEnum i'
    TagEnum = vars()
    for i in TAGS:
        TagEnum[f'{i}'.upper()] = i
        
    def __str__(self):
        return self.value


class ElementMeta(ABC):
    """"Base class for html element metadata object"""

class BaseElement(ABC):
    """"Base class for html element object"""

    
class ElementClassNames(UserList, ElementMeta):
    def __init__(self, value: str | list[str]):
        super().__init__([*value] if isinstance(value, (list, tuple, deque)) else [value] if value else [])
        
    def __str__(self):
        if len(self.data) > 0:
            return f'class="{fn.join(fn.filter_uniques(self.data))}"'
        return ''
    
    
class ElementBooleanAttributes(UserList, ElementMeta):
    def __str__(self):
        if len(self.data) > 0:
            return fn.join(self.data)
        return ''
    
    
class ElementAttributes(UserDict, ElementMeta):
    def __str__(self):
        if self.data:
            return fn.join(self.data, underscored=False, sep=' ')
        return ''


class ElementHTMX(UserDict, ElementMeta):
    def __str__(self):
        if self.data:
            return fn.join(self.data, prefix='data-hx-', underscored=False, sep=' ')
        return ''
    
    
class ElementStyles(UserDict, ElementMeta):
    def __str__(self):
        if self.data:
            return f'style="{fn.join(self.data, junction=": ", sep="; ", boundary="", underscored=False)}"'
        return ''
    

class ElementChildren(deque, ElementMeta):
    def __init__(self, data: Sequence[Element | str] | Element | str | None = None):
        super().__init__()
        self.include(data)
        
    def __str__(self):
        return fn.join(self)
    
    @overload
    def include(self, data: None) -> None:...
    
    @overload
    def include(self, data: Element | str) -> None:...
    
    @overload
    def include(self, data: Sequence[Element | str]) -> None:...
    
    def include(self, data: Sequence[Element | str] | Element | str) -> None:
        if isinstance(data, (Element, str)):
            self.append(data)
        elif isinstance(data, Sequence):
            self.extend(data)

class Element(UserString):
    def __init__(self, tag: str | None, *args: str, **kwargs):
        self._tag: TagEnum = TagEnum[tag.upper()]
        if self._tag is None:
            raise ValueError('Uma tag é necessária')
        else:
            self._classes = ElementClassNames(kwargs.pop('classes', list()))
            self._htmx: ElementHTMX = ElementHTMX(kwargs.pop('htmx', dict()))
            self._before = ElementChildren(kwargs.pop('before', list()))
            self._children = ElementChildren(kwargs.pop('children', list()))
            self._scripts = ElementChildren(kwargs.pop('scripts', list()))
            self._after = ElementChildren(kwargs.pop('after', list()))
            self._styles = ElementStyles(kwargs.pop('styles', dict()))
            self._boolean_attributes = ElementBooleanAttributes([i for i in args if isinstance(i, str)])
            self._attributes = ElementAttributes(kwargs)
            super().__init__(str(self))
        
    def __html__(self):
        return str(self)
        
    @property
    def tag(self) -> TagEnum:
        return self._tag
    
    @property
    def id(self) -> str:
        return self._attributes.get('id', None)
    
    @id.setter
    def id(self, value: str) -> None:
        self._attributes['id'] = value
        
    @property
    def classes(self) -> ElementClassNames:
        return self._classes
    
    @property
    def htmx(self) -> ElementHTMX:
        return self._htmx
    
    @property
    def children(self) -> ElementChildren:
        return self._children
    
    @property
    def styles(self) -> ElementStyles:
        return self._styles
    
    @property
    def boolean_attributes(self) -> ElementBooleanAttributes:
        return self._boolean_attributes
    
    @property
    def non_boolean_attributes(self) -> ElementAttributes:
        return self._attributes
    
    @property
    def attributes(self):
        return f'{self.boolean_attributes} {self.non_boolean_attributes}'
    
    @property
    def before(self) -> ElementChildren:
        return self._before
    
    @property
    def scripts(self) -> ElementChildren:
        return self._scripts
    
    @property
    def after(self) -> ElementChildren:
        return self._after
        
    def __str__(self) -> str:
        if self.tag.name in EMPTY:
            data = f'{self.before}<{self.tag} {self.htmx} {self.classes} {self.attributes} {self.styles}>{self.after}{self.scripts}'
        else:
            data = f'{self.before}<{self.tag} {self.htmx} {self.classes} {self.attributes} {self.styles}>{self.children}{self.scripts}</{self.tag}>{self.after}'
        return fn.remove_extra_whitespaces(data)
    
    def add_styles(self, **styles) -> Self:
        self.styles.data.update(**styles)
        return self
    
    def add_properties(self, **kwargs) -> Self:
        self.non_boolean_attributes.data.update(kwargs)
        return self
    
    @overload
    def add_children(self, data: Element | str) -> Self:...
    
    @overload
    def add_children(self, data: Sequence[Element | str]) -> Self:...

    def add_children(self, data: Element | str) -> Self:
        if isinstance(data, (Element, str)):
            self.children.append(data)
        elif isinstance(data, Sequence):
            self.children.extend(data)
        return self
    
    def append_child(self, child: Element | str) -> Self:
        self.children.append(child)
        return self
    
    def append_before(self, child: Element | str) -> Self:
        self.before.append(child)
        return self
    
    def append_after(self, child: Element | str) -> Self:
        self.after.append(child)
        return self
    
    def prepend_child(self, child: Element | str) -> Self:
        self.children.appendleft(child)
        return self
    
    def prepend_before(self, child: Element | str) -> Self:
        self.before.appendleft(child)
        return self
    
    def prepend_after(self, child: Element | str) -> Self:
        self.after.appendleft(child)
        return self
    
    
class BaseTagNamedElement(Element):
    TAG: ClassVar[str] = None
    def __init__(self, *args: str, **kwargs):
        super().__init__(self.TAG or self.__class__.__name__.lower(), *args, **kwargs)


class Div(BaseTagNamedElement):
    ...


class Button(BaseTagNamedElement):
    ...


class DataList(BaseTagNamedElement):
    ...


class H1(BaseTagNamedElement):
    ...


class H2(BaseTagNamedElement):
    ...


class H3(BaseTagNamedElement):
    ...


class H4(BaseTagNamedElement):
    ...


class H5(BaseTagNamedElement):
    ...


class H6(BaseTagNamedElement):
    ...


class HR(BaseTagNamedElement):
    ...


class Span(BaseTagNamedElement):
    ...


class Ul(BaseTagNamedElement):
    ...


class A(BaseTagNamedElement):
    ...


class Ol(BaseTagNamedElement):
    ...


class Li(BaseTagNamedElement):
    ...


class P(BaseTagNamedElement):
    ...


class Script(BaseTagNamedElement):
    location: Literal['head', 'body']
    
    def __init__(self, *args, **kwargs):
        self.location = kwargs.pop('location', 'head')
        super().__init__(*args, **kwargs)


class Section(BaseTagNamedElement):
    ...


class Body(BaseTagNamedElement):
    SCRIPT_BOOTSTRAP: ClassVar[Script] = Script(
            src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js",
            integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL",
            crossorigin="anonymous")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scripts.include(self.SCRIPT_BOOTSTRAP)
    
    # @property
    # def children(self) -> ElementChildren:
    #     children = self._children
    #     children.append(self.SCRIPT_BOOTSTRAP)
    #     return children

class Meta(BaseTagNamedElement):
    ...

class Link(BaseTagNamedElement):
    ...


class Title(BaseTagNamedElement):
    def __init__(self, value: str):
        super().__init__(children=[value])


class Head(BaseTagNamedElement):

    META_CHARSET_UTF8: ClassVar[Meta] = Meta(charset='utf-8')
    META_VIEWPORT: ClassVar[Meta] = Meta(
            name='viewport',
            content="width=device-width, initial-scale=1"
    )
    LINK_BOOTSTRAP_ICON: ClassVar[Link] = Link(
            rel='stylesheet',
            href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
    )
    LINK_BOOTSTRAP: ClassVar[Link] = Link(
            rel='stylesheet',
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css",
            integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN",
            crossorigin="anonymous"
    )
    
    def __init__(self, *children):
        elements = [
                self.META_CHARSET_UTF8,
                self.META_VIEWPORT,
                *fn.filter_by_type(children, Meta),
                *fn.filter_by_type(children, Title),
                self.LINK_BOOTSTRAP_ICON,
                self.LINK_BOOTSTRAP,
                *fn.filter_by_type(children, Link),
                *fn.filter_by_type(children, Script)
        ]
        super().__init__(children=elements)


class Option(BaseTagNamedElement):
    def __init__(self, value: str = None, children: str | Element | list[Element | str] = None, id: str = None, **kwargs):
        super().__init__(value=value, children=children, id=id, **kwargs)


class HTML(BaseTagNamedElement):
    def __init__(self, *args, **kwargs):
        self.lang: str = kwargs.pop('lang', 'pt-BR')
        body = kwargs.pop('body', [])
        head = kwargs.pop('head', [])
        if isinstance(body, Body): _body = body
        else: _body = Body(children=body)
        if isinstance(head, Head): _head = head
        else: _head = Head(children=head)
        self.body: Body  = _body
        self.body.id = 'body'
        self.head: Head = _head
        self.head.id = 'head'
        super().__init__(*args, lang=self.lang, **kwargs)
        
    @staticmethod
    def container(*args, **kwargs):
        return Div(*args, **kwargs)
    
    @property
    def children(self) -> ElementChildren:
        return ElementChildren([self.head, self.body])
        
    @staticmethod
    def section(*args, **kwargs):
        return Section(*args, **kwargs)
    
    @staticmethod
    def grid(*args, **kwargs):
        new = Div(*args, **kwargs)
        new.classes.append('row')
        return new
    
    
class Document(ElementChildren):
    def __init__(self, children: Element | str | list[Element | str] = None, **kwargs):
        self.kwargs = kwargs
        super().__init__(children or list())

    def __str__(self):
        return '\n'.join([str(i) for i in self])

    def file(self):
        return IoDocument(children=[*self])


class IoDocument(io.StringIO):
    children: Document[Element | str]
    def __init__(self, children: Element | str | list[Element | str] = None, *args, **kwargs):
        self.children = Document(children if isinstance(children, list) else list() if not children else [children])
        self.kwargs = kwargs
        super().__init__(*args)

    def __str__(self):
        try:
            return self.getvalue()
        finally:
            self.close()

    def __html__(self):
        return str(self)

    def include(self, *args):
        self.children.include(args)

    def append(self, child: Element | str):
        self.children.append(child)

    def extend(self, children: [Element | str]):
        self.children.extend(children)

    def prepend(self, child: Element | str):
        self.children.appendleft(child)

    def wrap(self, parent: Element):
        parent.children.extend(self.children)
        self.__init__(parent)

    def getvalue(self) -> str:
        super().__init__(str(self.children))
        return super().getvalue()


