# hx-markup

--- 

Write, clean and render html pages pythonically, powered with BeautifulSoup4 and lmxl for fast parsing.

## Example 

```
class Element(Render):
    def __init__(tag: str, *args, children: list[str | Render] = None):
        ...
        
```


### Element TagEnum 
TagEnum name of the element, according to HTML5 official tags. 
This is represented in **hx_markup** as a TagEnum member, 
auto loadded for each Element. 


### Render Classes 

#### NodeText 

#### Element 

