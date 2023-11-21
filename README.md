# hx-markup

--- 

### Element TagEnum 
TagEnum name of the element, according to HTML5 official tags. 
This is represented in **hx_markup** as a TagEnum member, auto loadded for each Element. 

### HTML Element 
All HTML elements. 

### Element Config
HTML Element render_config include:
- boolean attributes: BooleanAttributes class is a subclass of UserList that render attributes like 'required' or 'readonly'.
- key value attributes: KeyValueAttributes class is a subclass of UserDict that render all key-value attributes, like 'value=77'.
- class names: ClassNames class render the 'class' attribute, storing info as a list of unique values. 
- htmx attributes: HTMX class accept a dictionary with key value pairs and will render 'data-hx-...'

