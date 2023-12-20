from __future__ import annotations

import dataclasses
import io
import os.path
from collections.abc import Sequence
from abc import ABC, abstractmethod
from collections import deque
from typing import Optional, TypeVar

from bs4 import BeautifulSoup

from hx_markup import functions
from hx_markup import enums
from hx_markup import config


@dataclasses.dataclass
class RenderBase(ABC):
    
    def __str__(self):
        return self.bs4.prettify()
    
    @abstractmethod
    def render(self) -> str:...
    
    @property
    def bs4(self):
        return BeautifulSoup(self.render(), 'lxml')
    
    def __html__(self):
        return str(self)
    
    
# @dataclasses.dataclass
# class StyleStatement(RenderBase):
#     target: str
#     properties: dict[str, str]
#
#     def render(self) -> str:
#         return f'{self.target} {{{functions.join_style_attrs(self.properties)}}}'


# @dataclasses.dataclass
# class ScriptFunction(RenderBase):
#     name: str | None = None
#     args: str | None = None
#     statements: list[str, ScriptFunction] = dataclasses.field(default_factory=list)
#
#     def render(self) -> str:
#         with io.StringIO() as f:
#             if self.name:
#                 f.write(f'function {self.name}')
#             else:
#                 f.write(f'function')
#             if self.args:
#                 f.write(f'({functions.join(self.args.split(), sep=", ")})')
#             else:
#                 f.write('()')
#             f.write(f'{{{functions.join(self.statements, sep="; ")}}}')
#             return f.getvalue()
#
#

@dataclasses.dataclass
class NodeTextBase(RenderBase):
    text: str
    
# @dataclasses.dataclass
# class ChildBase:
#     _parent: Element | None = dataclasses.field(init=False, default=None)

    
@dataclasses.dataclass
class ElementBase(RenderBase):
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



# @dataclasses.dataclass
# class Script(ChildBase, ElementBase):
#     id: Optional[str] = None
#     booleans: list[str] | str |  None = dataclasses.field(default_factory=list)
#     keywords: dict[str, str] | None = dataclasses.field(default_factory=dict)
#     statements: list[str, ScriptFunction] | None = dataclasses.field(default_factory=list)
#
#     @property
#     def render_booleans(self):
#         return functions.join([
#                 i for i in self.booleans
#                 if all([functions.is_boolean_attr(i), functions.attr_element_match(i, 'script')])])
#
#     @property
#     def render_keywords(self):
#         return functions.join_html_keyword_attrs(self.keywords)
#
#     @property
#     def render_config(self):
#         with io.StringIO() as f:
#             if self.id:
#                 f.write(f' id="{self.id}"')
#             if self.booleans:
#                 f.write(f' {self.render_booleans}')
#             if self.keywords:
#                 f.write(f' {self.render_keywords}')
#             return f.getvalue()
#
#     def render(self) -> str:
#         with io.StringIO() as f:
#             f.write(f'<script {self.render_config}>')
#             if self.statements:
#                 f.write(' ')
#                 f.write(functions.join(self.statements, sep="; "))
#             f.write('</script>')
#             return f.getvalue()

# @dataclasses.dataclass
# class Style(ChildBase, ElementBase):
#     id: Optional[str] = None
#     booleans: list[str] | str |  None = dataclasses.field(default_factory=list)
#     keywords: dict[str, str] | None = dataclasses.field(default_factory=dict)
#     vars: dict[str, str] | None = dataclasses.field(default_factory=dict)
#     statements: list[StyleStatement] | None = dataclasses.field(default_factory=list)
#
#     @property
#     def render_booleans(self):
#         return functions.join([
#                 i for i in self.booleans
#                 if all([functions.is_boolean_attr(i), functions.attr_element_match(i, 'style')])])
#
#     @property
#     def render_keywords(self):
#         return functions.join_html_keyword_attrs(self.keywords)
#
#     @property
#     def render_config(self):
#         with io.StringIO() as f:
#             if self.id:
#                 f.write(f' id="{self.id}"')
#             if self.booleans:
#                 f.write(f' {self.render_booleans}')
#             if self.keywords:
#                 f.write(f' {self.render_keywords}')
#             return f.getvalue()
#
#
#     @classmethod
#     def var_name(cls, key: str):
#         return f'--{functions.slug_to_kebab_case(key)}'
#
#     def render(self) -> str:
#         with io.StringIO() as f:
#             f.write(f'<style {self.render_config}>')
#             if self.vars:
#                 f.write(' ')
#                 f.write(f':root {{{functions.join({self.var_name(k): v for k, v in self.vars.items()}, sep="; ", junction=": ")}}}')
#             if self.statements:
#                 f.write(' ')
#                 f.write(functions.join(self.statements))
#             f.write('</style>')
#             return f.getvalue()
            
# @dataclasses.dataclass
# class NodeText(NodeTextBase):
#
#     def render(self) -> str:
#         return self.text or ''


@dataclasses.dataclass(init=False)
class Element(ElementBase):

    def __init__(self, tag: str, /, *args, **kwargs):
        self.tag = tag
        self._init_args(*args)
        self.children = self._setup_deque(kwargs.pop('children', deque()))
        self.after = self._setup_deque(kwargs.pop('after', deque()))
        self.before = self._setup_deque(kwargs.pop('before', deque()))
        self.styles = kwargs.pop('styles', {})
        self.htmx = kwargs.pop('htmx', {})
        self.dataset = kwargs.pop('dataset', {})
        self.keywords = kwargs

    # def _setup_booleans(self):
    #     if isinstance(self.booleans, str):
    #         self.booleans = functions.split_words(self.booleans)
                
    # def _setup_classlist(self):
    #     if isinstance(self.classlist, str):
    #         self.classlist = functions.split_words(self.classlist)
    
    @staticmethod
    def _setup_deque(children: deque[str | ElementType]) -> deque:
        if not isinstance(children, deque):
            if isinstance(children, (str, Element)):
                return deque([children])
            elif isinstance(children, Sequence):
                return deque([*children])
        else:
            return children
        # self._setup_children_parent()
        
    # def _setup_before(self, before: deque[str | ElementType] ):
    #     if not isinstance(before, deque):
    #         if isinstance(before, (str, Element)):
    #             self.before = deque([before])
    #         elif isinstance(before, Sequence):
    #             self.before = deque([*before])
    #     else:
    #         self.before = before
    #
    # def _setup_after(self, after: deque[str | ElementType] ):
    #     if not isinstance(after, deque):
    #         if isinstance(after, (str, Element)):
    #             self.after = deque([after])
    #         elif isinstance(after, Sequence):
    #             self.after = deque([*after])
    #     else:
    #         self.after = after
                
    def _init_args(self, *args):
        items, self.classlist, self.booleans = [], [], []
        for item in args:
            if isinstance(item, str):
                items.extend(item.split())
        for item in functions.filter_uniques(items):
            if item.startswith('#'):
                self.id = item[1:]
            elif item.startswith('.'):
                self.classlist.append(item[1:])
            else:
                self.booleans.append(item)
        
    @property
    def tag_enum(self):
        return enums.TagEnum[self.tag.upper()]
    
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
        return ' '.join(functions.filter_uniques(items))

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
                f.write(' ')
                f.write(f'class="{functions.join(functions.filter_uniques(self.classlist))}"')
            if self.dataset:
                f.write(' ')
                f.write(functions.join_html_dataset_attrs(self.dataset))
            if self.htmx:
                f.write(' ')
                f.write(functions.join_htmx_attrs({k:v for k, v in self.htmx.items() if functions.is_htmx_attr(k)}))
            if self.styles:
                f.write(' ')
                f.write(f'style="{functions.join_style_attrs(self.styles)}"')
            return f.getvalue()
        
    @staticmethod
    def _is_script(item):
        return any([isinstance(item, Element) and item.tag_enum.tagname == 'script', str(item).startswith('<script')])

    @property
    def render_children(self):
        with io.StringIO() as f:
            if self.tag_enum.tagname == 'script':
                f.write(functions.join(self.children, sep="; "))
            if self.tag_enum.tagname == 'style':
                f.write(functions.join(self.children, sep="; ", junction=':', underscored=False, boundary=''))
            else:
                scripts = [i for i in self.children if self._is_script(i)]
                f.write(functions.join([i for i in self.children if not i in scripts]))
                f.write(functions.join(scripts))
            return f.getvalue()
        
    def render(self) -> str:
        with io.StringIO() as f:
            if self.before:
                f.write(functions.join(self.before))
            f.write(f'<{self.tag_enum.tagname} {self.render_config}>')
            if not self.tag_enum.void:
                f.write(self.render_children)
                f.write(f'</{self.tag_enum.tagname}>')
            if self.after:
                f.write(functions.join(self.after))
            return f.getvalue()
            
ElementType = TypeVar('ElementType', bound=Element)



if __name__ == '__main__':
    b = Element('body', children=[
            Element('script', 'defer', src='/teste'),
            '<script src="/other" type="text/javascript">console.log(body)</script>',
            Element('main','hidden required .mymain #main',  children=Element('div', 'myid', children=[Element('h1', children='dia', styles=dict(font_size='12px', color='red'))])),
    ])
    print(b)
    print(dataclasses.asdict(b))

