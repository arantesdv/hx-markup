from __future__ import annotations

import dataclasses
import io
import os.path
from collections.abc import Sequence
from abc import ABC, abstractmethod
from collections import deque
from typing import Optional, TypeVar

from bs4 import BeautifulSoup
from lxml import etree
from lxml.builder import E

from hx_markup import functions
from hx_markup import enums



@dataclasses.dataclass
class Render(ABC):
    tag: str
    
    @property
    def tag_enum(self):
        return enums.TagEnum[self.tag.upper()]
    
    def __str__(self):
        if isinstance(self, NodeText):
            return self.render()
        if self.tag_enum.tagname == 'html':
            return self.bs4.prettify()
        return self.render()
    
    @property
    def etree(self):
        return etree.fromstring(self.render(), parser=etree.HTMLParser())
    
    @abstractmethod
    def render(self) -> str:...
    
    @property
    def bs4(self):
        return BeautifulSoup(self.render(), 'lxml')
    
    def __html__(self):
        return str(self)
    
    @staticmethod
    def js_function(name: str, /, *args, statements: Sequence[str | NodeText]) -> NodeText:
        return NodeText(f'function {name} ({", ".join(args)}) {{{"; ".join([str(i) for i in statements])}}}')
    
    @staticmethod
    def selector_style(selector: str, styles: dict[str, str]) -> NodeText:
        return NodeText(f'{selector} {{{functions.join_style_attrs(styles)}}} ')
    
    @staticmethod
    def js_anonymous_function(*args, statements: Sequence[str]) -> NodeText:
        return NodeText(f'function ({", ".join(args)}) {{{functions.join(statements, sep="; ")}}}')
    
    @staticmethod
    def js_arrow_function(*args, statements: Sequence[str]) -> NodeText:
        return NodeText(f'({", ".join(args)}) => {{{functions.join(statements, sep="; ")}}}')

    @staticmethod
    def js_const(name: str, /, value: str | int | float | NodeText = None) -> NodeText:
        if value is None:
            return NodeText(f'const {name}')
        if isinstance(value, str):
            return NodeText(f'const {name} = "{value}"')
        return NodeText(f'const {name} = {value}')

    @staticmethod
    def js_let(name: str, /, value: str = None) -> NodeText:
        if value is None:
            return NodeText(f'let {name}')
        if isinstance(value, str):
            return NodeText(f'let {name} = "{value}"')
        return NodeText(f'let {name} = {value}')

    @staticmethod
    def js_conditional_loop(statements: Sequence[tuple[NodeText, NodeText]], _else: NodeText | None = None) -> NodeText:
        with io.StringIO() as f:
            for item in statements:
                if statements.index(item) == 0:
                    f.write(f'if ({item[0]}) {{{item[1]}}} ')
                else:
                    f.write(f'else if ({item[0]}) {{{item[1]}}} ')
            if _else:
                f.write(f'else {{{_else}}} ')
            return NodeText(f.getvalue())

@dataclasses.dataclass(init=False)
class BaseArgument(ABC):
    data: str | ElementType | list[str | ElementType] | dict[str, str]
    
    def __init__(self, data: str | Render | list[str | Render] | dict[str, str]) -> None:
        if isinstance(data, (list, dict)):
            self.data = data
        elif isinstance(data, (str, Render)):
            self.data = [data]
            
    
@dataclasses.dataclass(init=False)
class After(BaseArgument):
    data: str | ElementType | list[str | ElementType]
    
    
@dataclasses.dataclass(init=False)
class Before(BaseArgument):
    data: str | ElementType | list[str | ElementType]


@dataclasses.dataclass(init=False)
class HTMX(BaseArgument):
    data: dict[str, str]


@dataclasses.dataclass
class NodeTextBase(Render):
    text: str
    

@dataclasses.dataclass(init=False)
class NodeText(NodeTextBase):
    def __init__(self, text: str | NodeText) -> None:
        self.text = str(text)
        
    def render(self) -> str:
        return self.text
    
    def __str__(self):
        return self.render()


@dataclasses.dataclass
class ElementBase(Render):
    tag: str
    id: Optional[str] = None
    booleans: list[str] | str |  None = dataclasses.field(default_factory=list)
    classlist: list[str] | str | None = dataclasses.field(default_factory=list)
    keywords: dict[str, str] | None = dataclasses.field(default_factory=dict)
    htmx: dict[str, str] | None = dataclasses.field(default_factory=dict)
    dataset: dict[str, str] | None = dataclasses.field(default_factory=dict)
    styles: dict[str, str] | None = dataclasses.field(default_factory=dict)
    children: deque[str | ElementType] | list[str | ElementType] | str | ElementType = dataclasses.field(default_factory=deque)
    before: deque[str | ElementType] | list[str | ElementType] | str | ElementType = dataclasses.field(default_factory=deque)
    after: deque[str | ElementType] | list[str | ElementType] | str | ElementType = dataclasses.field(default_factory=deque)


@dataclasses.dataclass(init=False)
class Element(ElementBase):

    def __init__(self, tag: str, /, *args, **kwargs):
        self.tag = tag
        self._init_args(*args)
        self.children.extend(self._setup_deque(kwargs.pop('children', deque())))
        self.after.extend(self._setup_deque(kwargs.pop('after', deque())))
        self.before.extend(self._setup_deque(kwargs.pop('before', deque())))
        self.htmx.update(kwargs.pop('htmx', {}))
        self.styles = kwargs.pop('styles', {})
        self.dataset = kwargs.pop('dataset', {})
        self.keywords = kwargs

    
    @staticmethod
    def _setup_deque(children: deque[str | ElementType]) -> deque:
        if not isinstance(children, deque):
            if isinstance(children, (str, Element)):
                return deque([children])
            elif isinstance(children, Sequence):
                return deque([*children])
        else:
            return children

    def _init_args(self, *args):
        items, self.classlist, self.booleans, self.after, self.before, self.children, self.htmx = [], [], [], deque(), deque(), deque(), {}
        for item in args:
            if isinstance(item, str):
                items.extend(item.split())
            elif isinstance(item, Before):
                self.before.extend(item.data)
            elif isinstance(item, After):
                self.after.extend(item.data)
            elif isinstance(item, (NodeText, Element)):
                self.children.append(item)
            elif isinstance(item, HTMX):
                self.htmx.update(**item.data)
        for item in functions.filter_uniques(items):
            if item.startswith('#'):
                self.id = item[1:]
            elif item.startswith('.'):
                self.classlist.append(item[1:])
            else:
                self.booleans.append(item)

    @property
    def _auto_render_tag_related_config(self):
        if self.tag_enum.name == 'MAIN':
            return ' role="main"'
        return ''
        
    @property
    def _render_booleans(self) -> str:
        items = [i for i in self.booleans if all([
                functions.is_boolean_attr(i),
                any([functions.attr_element_match(i, self.tag_enum.tagname),
                     functions.is_global_attr(i)])
        ])]
        return ' '.join(functions.filter_uniques(items)).strip()

    @property
    def render_config(self):
        with io.StringIO() as f:
            if self.id:
                f.write(f' id="{self.id}"')
            f.write(self._auto_render_tag_related_config)
            if self.booleans:
                f.write(f' {self._render_booleans}')
            if self.keywords:
                f.write(' ')
                f.write(functions.join_html_keyword_attrs({
                        functions.slug_to_kebab_case(k): v
                        for k, v in self.keywords.items()
                        if k != 'id'
                        if all([not functions.is_boolean_attr(k), functions.attr_element_match(k, self.tag_enum.tagname)])}))
            if self.classlist:
                f.write(f' class="{functions.join(functions.filter_uniques(self.classlist))}"')
            if self.dataset:
                f.write(' ')
                f.write(functions.join_html_dataset_attrs(self.dataset))
            if self.htmx:
                f.write(' ')
                f.write(functions.join_htmx_attrs({k:v for k, v in self.htmx.items() if functions.is_htmx_attr(k)}))
            if self.styles:
                f.write(f' style="{functions.join_style_attrs(self.styles)}"')
            return f.getvalue()
        
    @staticmethod
    def _is_script(item):
        return any([isinstance(item, Element) and item.tag_enum.tagname == 'script', str(item).startswith('<script')])
    
    @staticmethod
    def _is_style(item):
        return any([isinstance(item, Element) and item.tag_enum.tagname == 'style', str(item).startswith('<style')])


    @property
    def render_children(self):
        with io.StringIO() as f:
            if self.tag_enum.tagname == 'script':
                f.write('; '.join([str(i) for i in self.children]))
            elif self.tag_enum.tagname == 'style':
                f.write(functions.join(self.children, sep=" "))
            else:
                f.write(functions.join([i for i in self.children if self._is_style(i)]))
                f.write(functions.join([i for i in self.children if all([not self._is_script(i), not self._is_style(i)])]))
                f.write(functions.join([i for i in self.children if self._is_script(i)]))
            return f.getvalue()
        
    def render(self) -> str:
        with io.StringIO() as f:
            if self.before:
                f.write(functions.join(self.before))
            if self.tag_enum.is_void:
                f.write(f'<{self.tag_enum.tagname}{self.render_config}/>')
            else:
                f.write(f'<{self.tag_enum.tagname}{self.render_config}>')
                f.write(self.render_children)
                f.write(f'</{self.tag_enum.tagname}>')
            if self.after:
                f.write(functions.join(self.after))
            return f.getvalue()
            
            
ElementType = TypeVar('ElementType', Element, NodeText)


@dataclasses.dataclass(init=False)
class Head(Element):
    def __init__(self, *args):
        super().__init__('head', children=[*args])
        
        
@dataclasses.dataclass(init=False)
class Body(Element):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__('body', *args, **kwargs)
        

@dataclasses.dataclass(init=False)
class Script(Element):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__('script', *args, **kwargs)
        
        
@dataclasses.dataclass(init=False)
class Style(Element):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__('style', *args, **kwargs)
        
        
@dataclasses.dataclass(init=False)
class Div(Element):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__('div', *args, **kwargs)
        
        
@dataclasses.dataclass(init=False)
class Nav(Element):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__('nav', *args, **kwargs)
        
        
@dataclasses.dataclass(init=False)
class Main(Element):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__('main', *args, **kwargs)
        
        
@dataclasses.dataclass(init=False)
class Footer(Element):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__('footer', *args, **kwargs)


if __name__ == '__main__':
    x = Element(
            'html',
            Before('<!doctype html>'),
            Head(Element('link', rel='stylesheet', href='/static/css/main.css')),
            Body(Element('header', Div('#daniel .bg', NodeText('boa noite'))), Footer('hidden'),
                 HTMX({'get': '/'}), Style(NodeText('*{color: black}'), NodeText('html {padding: 0}'))))
    print(x)
    

