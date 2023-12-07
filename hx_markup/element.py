from __future__ import annotations

import dataclasses
import io
from collections.abc import Sequence
from abc import ABC, abstractmethod
from collections import deque
from typing import Optional, TypeVar

from hx_markup import functions
from hx_markup import enums


@dataclasses.dataclass
class RenderBase(ABC):
    
    def __str__(self):
        return functions.remove_extra_whitespaces(self.render())
    @abstractmethod
    def render(self) -> str:...
    
    def __html__(self):
        return str(self)
    
    
@dataclasses.dataclass
class StyleStatement(RenderBase):
    target: str
    properties: dict[str, str]
    
    def render(self) -> str:
        return f'{self.target} {{{functions.join_style_attrs(self.properties)}}}'


@dataclasses.dataclass
class ScriptFunction(RenderBase):
    name: str | None = None
    args: str | None = None
    statements: list[str, ScriptFunction] = dataclasses.field(default_factory=list)
    
    def render(self) -> str:
        with io.StringIO() as f:
            if self.name:
                f.write(f'function {self.name}')
            else:
                f.write(f'function')
            if self.args:
                f.write(f'({functions.join(self.args.split(), sep=", ")})')
            else:
                f.write('()')
            f.write(f'{{{functions.join(self.statements, sep="; ")}}}')
            return f.getvalue()
    
    

@dataclasses.dataclass
class ChildBase:
    _parent: Element | None = dataclasses.field(init=False)

    
@dataclasses.dataclass
class BaseElement(RenderBase):
    
    def __post_init__(self):
        if booleans:= getattr(self, 'booleans'):
            if isinstance(booleans, str):
                self.booleans = functions.split_words(booleans)


ElementType = TypeVar('ElementType', bound=BaseElement)


@dataclasses.dataclass
class Script(ChildBase, BaseElement):
    id: Optional[str] = None
    booleans: list[str] | str |  None = dataclasses.field(default_factory=list)
    keywords: dict[str, str] | None = dataclasses.field(default_factory=dict)
    statements: list[str, ScriptFunction] | None = dataclasses.field(default_factory=list)
    
    @property
    def render_booleans(self):
        return functions.join([
                i for i in self.booleans
                if all([functions.is_boolean_attr(i), functions.attr_element_match(i, 'script')])])
    
    @property
    def render_keywords(self):
        return functions.join_html_keyword_attrs(self.keywords)
    
    @property
    def render_config(self):
        with io.StringIO() as f:
            if self.id:
                f.write(f' id="{self.id}"')
            if self.booleans:
                f.write(f' {self.render_booleans}')
            if self.keywords:
                f.write(f' {self.render_keywords}')
            return f.getvalue()
            
    def render(self) -> str:
        with io.StringIO() as f:
            f.write(f'<script {self.render_config}>')
            if self.statements:
                f.write(' ')
                f.write(functions.join(self.statements, sep="; "))
            f.write('</script>')
            return f.getvalue()

@dataclasses.dataclass
class Style(ChildBase, BaseElement):
    id: Optional[str] = None
    booleans: list[str] | str |  None = dataclasses.field(default_factory=list)
    keywords: dict[str, str] | None = dataclasses.field(default_factory=dict)
    vars: dict[str, str] | None = dataclasses.field(default_factory=dict)
    statements: list[StyleStatement] | None = dataclasses.field(default_factory=list)
    
    @property
    def render_booleans(self):
        return functions.join([
                i for i in self.booleans
                if all([functions.is_boolean_attr(i), functions.attr_element_match(i, 'style')])])
    
    @property
    def render_keywords(self):
        return functions.join_html_keyword_attrs(self.keywords)
    
    @property
    def render_config(self):
        with io.StringIO() as f:
            if self.id:
                f.write(f' id="{self.id}"')
            if self.booleans:
                f.write(f' {self.render_booleans}')
            if self.keywords:
                f.write(f' {self.render_keywords}')
            return f.getvalue()
            
    
    @classmethod
    def var_name(cls, key: str):
        return f'--{functions.slug_to_kebab_case(key)}'
        
    def render(self) -> str:
        with io.StringIO() as f:
            f.write(f'<style {self.render_config}>')
            if self.vars:
                f.write(' ')
                f.write(f':root {{{functions.join({self.var_name(k): v for k, v in self.vars.items()}, sep="; ", junction=": ")}}}')
            if self.statements:
                f.write(' ')
                f.write(functions.join(self.statements))
            f.write('</style>')
            return f.getvalue()
            
@dataclasses.dataclass
class NodeText(ChildBase):
    text: str | None = None
    def render(self) -> str:
        return self.text or ''


class ListOfUniques:
    pass


@dataclasses.dataclass
class Element(ChildBase, BaseElement):
    tag: str
    id: Optional[str] = None
    booleans: list[str] | str |  None = dataclasses.field(default_factory=list)
    classlist: list[str] | str | None = dataclasses.field(default_factory=list)
    keywords: dict[str, str] | None = dataclasses.field(default_factory=dict)
    extra_keywords: dict[str, str] | None = dataclasses.field(default_factory=dict)
    htmx: dict[str, str] | None = dataclasses.field(default_factory=dict)
    dataset: dict[str, str] | None = dataclasses.field(default_factory=dict)
    styles: dict[str, str] | None = dataclasses.field(default_factory=dict)
    children: deque[str | ElementType] | list[str | ElementType] | str | ElementType = dataclasses.field(default_factory=deque)
    
    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.classlist, str):
            self.classlist = functions.split_words(self.classlist)
        if not isinstance(self.children, deque):
            if isinstance(self.children, (str, ChildBase)):
                self.children = deque([self.children])
            elif isinstance(self.children, Sequence):
                self.children = deque([*self.children])
        for item in self.children:
            if isinstance(item, ChildBase):
                item._parent = self
            else:
                node = NodeText(item)
                node._parent = self
                
    def parse_args(self, *args):
        items = []
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
        return self
                
                
    @classmethod
    def create(cls, tag: str, *args: str, **kwargs):
        new = cls(tag, **kwargs)
        return new.parse_args(*args)
                

    @property
    def tag_enum(self):
        return enums.TagEnum[self.tag.upper()]
    
    @property
    def _auto_render_tag_related_config(self):
        if self.tag_enum.name == 'MAIN':
            return ' role="main"'
        return ''
        

    @property
    def render_config(self):
        with io.StringIO() as f:
            if self.id:
                f.write(f' id="{self.id}"')
            f.write(self._auto_render_tag_related_config)
            if self.booleans:
                f.write(' ')
                f.write(functions.join([
                        i for i in self.booleans
                        if all([functions.is_boolean_attr(i), functions.attr_element_match(i, self.tag_enum.tagname)])]))
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

    @property
    def render_children(self):
        with io.StringIO() as f:
            if self.tag_enum.tagname == 'script':
                f.write(functions.join(self.children, sep="; "))
            else:
                f.write(functions.join(self.children))
            return f.getvalue()
        
    def render(self) -> str:
        with io.StringIO() as f:
            f.write(f'<{self.tag_enum.tagname} {self.render_config}>')
            if not self.tag_enum.void:
                f.write(self.render_children)
                f.write(f'</{self.tag_enum.tagname}>')
            return f.getvalue()
            



if __name__ == '__main__':
    x = Element.create('input', '#myid .myclass required')
    print(x)
