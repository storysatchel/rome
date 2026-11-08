## Treemap Diagram

> A treemap diagram displays hierarchical data as a set of nested rectangles. Each branch of the tree is represented by a rectangle, which is then tiled with smaller rectangles representing sub-branches.

## Introduction

Treemap diagrams are an effective way to visualize hierarchical data and show proportions between categories and subcategories. The size of each rectangle is proportional to the value it represents, making it easy to compare different parts of a hierarchy.

Treemap diagrams are particularly useful for:

- Visualizing hierarchical data structures
- Comparing proportions between categories
- Displaying large amounts of hierarchical data in a limited space
- Identifying patterns and outliers in hierarchical data

## Syntax

### Node Definition

Nodes in a treemap are defined using the following syntax:

- **Section/Parent nodes**: Defined with quoted text `"Section Name"`
- **Leaf nodes with values**: Defined with quoted text followed by a colon and value `"Leaf Name": value`
- **Hierarchy**: Created using indentation (spaces or tabs)
- **Styling**: Nodes can be styled using the `:::class` syntax

## Examples

### Basic Treemap

<svg id="mermaid-77" width="100%" xmlns="http://www.w3.org/2000/svg" viewBox="2 27 996 371" style="max-width: 996px;" class="flowchart" role="graphics-document document" aria-roledescription="treemap"><g></g><g transform="translate(0, 0)" class="treemapContainer"><g class="treemapSection" transform="translate(0,0)"><clipPath id="clip-section-mermaid-77-0"><rect width="988" height="25"></rect></clipPath></g><g class="treemapSection" transform="translate(10,35)"><rect width="556" height="25" class="treemapSectionHeader" fill="none" fill-opacity="0.6" stroke-width="0.6" style=""></rect><clipPath id="clip-section-mermaid-77-1"><rect width="544" height="25"></rect></clipPath><rect width="556" height="355" class="treemapSection section1" fill="#1f2020" fill-opacity="0.6" stroke="hsl(180, 1.5873015873%, 22.3529411765%)" stroke-width="2" stroke-opacity="0.4" style=";"></rect><text class="treemapSectionLabel" x="6" y="12.5" dominant-baseline="middle" font-weight="bold" clip-path="url(#clip-section-mermaid-77-1)" style="dominant-baseline: middle; font-size: 12px; fill:lightgrey; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Category B</text> <text class="treemapSectionValue" x="546" y="12.5" text-anchor="end" dominant-baseline="middle" font-style="italic" style="text-anchor: end; dominant-baseline: middle; font-size: 10px; fill:lightgrey; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">40</text></g> <g class="treemapSection" transform="translate(576,35)"><rect width="414" height="25" class="treemapSectionHeader" fill="none" fill-opacity="0.6" stroke-width="0.6" style=""></rect><clipPath id="clip-section-mermaid-77-2"><rect width="402" height="25"></rect></clipPath><rect width="414" height="355" class="treemapSection section2" fill="#0b0000" fill-opacity="0.6" stroke="hsl(0, 100%, 12.1568627451%)" stroke-width="2" stroke-opacity="0.4" style=";"></rect><text class="treemapSectionLabel" x="6" y="12.5" dominant-baseline="middle" font-weight="bold" clip-path="url(#clip-section-mermaid-77-2)" style="dominant-baseline: middle; font-size: 12px; fill:lightgrey; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Category A</text> <text class="treemapSectionValue" x="404" y="12.5" text-anchor="end" dominant-baseline="middle" font-style="italic" style="text-anchor: end; dominant-baseline: middle; font-size: 10px; fill:lightgrey; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">30</text></g> <g class="treemapNode treemapLeafGroup leaf0x" transform="translate(20,70)"><rect width="331" height="310" class="treemapLeaf" fill="#1f2020" style="" fill-opacity="0.3" stroke="#1f2020" stroke-width="3"></rect><clipPath id="clip-mermaid-77-0"><rect width="327" height="306"></rect></clipPath><text class="treemapLabel" x="165.5" y="155" style="text-anchor: middle; dominant-baseline: middle; font-size: 38px;fill:lightgrey;" clip-path="url(#clip-mermaid-77-0)">Item B2</text> <text class="treemapValue" x="165.5" y="176" style="text-anchor: middle; dominant-baseline: hanging; font-size: 23px; fill: lightgrey;" clip-path="url(#clip-mermaid-77-0)">25</text></g> <g class="treemapNode treemapLeafGroup leaf1x" transform="translate(361,70)"><rect width="195" height="310" class="treemapLeaf" fill="#1f2020" style="" fill-opacity="0.3" stroke="#1f2020" stroke-width="3"></rect><clipPath id="clip-mermaid-77-1"><rect width="191" height="306"></rect></clipPath><text class="treemapLabel" x="97.5" y="155" style="text-anchor: middle; dominant-baseline: middle; font-size: 38px;fill:lightgrey;" clip-path="url(#clip-mermaid-77-1)">Item B1</text> <text class="treemapValue" x="97.5" y="176" style="text-anchor: middle; dominant-baseline: hanging; font-size: 23px; fill: lightgrey;" clip-path="url(#clip-mermaid-77-1)">15</text></g> <g class="treemapNode treemapLeafGroup leaf2x" transform="translate(586,70)"><rect width="259" height="310" class="treemapLeaf" fill="#0b0000" style="" fill-opacity="0.3" stroke="#0b0000" stroke-width="3"></rect><clipPath id="clip-mermaid-77-2"><rect width="255" height="306"></rect></clipPath><text class="treemapLabel" x="129.5" y="155" style="text-anchor: middle; dominant-baseline: middle; font-size: 38px;fill:lightgrey;" clip-path="url(#clip-mermaid-77-2)">Item A2</text> <text class="treemapValue" x="129.5" y="176" style="text-anchor: middle; dominant-baseline: hanging; font-size: 23px; fill: lightgrey;" clip-path="url(#clip-mermaid-77-2)">20</text></g> <g class="treemapNode treemapLeafGroup leaf3x" transform="translate(855,70)"><rect width="125" height="310" class="treemapLeaf" fill="#0b0000" style="" fill-opacity="0.3" stroke="#0b0000" stroke-width="3"></rect><clipPath id="clip-mermaid-77-3"><rect width="121" height="306"></rect></clipPath><text class="treemapLabel" x="62.5" y="155" style="text-anchor: middle; dominant-baseline: middle; font-size: 33px; fill: lightgrey;" clip-path="url(#clip-mermaid-77-3)">Item A1</text> <text class="treemapValue" x="62.5" y="173.5" style="text-anchor: middle; dominant-baseline: hanging; font-size: 20px; fill: lightgrey;" clip-path="url(#clip-mermaid-77-3)">10</text></g></g></svg>

##### Code:

```
mermaidtreemap-beta
"Category A"
    "Item A1": 10
    "Item A2": 20
"Category B"
    "Item B1": 15
    "Item B2": 25
```

### Hierarchical Treemap

##### Code:

```
mermaidtreemap-beta
"Products"
    "Electronics"
        "Phones": 50
        "Computers": 30
        "Accessories": 20
    "Clothing"
        "Men's": 40
        "Women's": 40
```

### Treemap with Styling

##### Code:

```
mermaidtreemap-beta
"Section 1"
    "Leaf 1.1": 12
    "Section 1.2":::class1
      "Leaf 1.2.1": 12
"Section 2"
    "Leaf 2.1": 20:::class1
    "Leaf 2.2": 25
    "Leaf 2.3": 12

classDef class1 fill:red,color:blue,stroke:#FFD600;
```

## Styling and Configuration

Treemap diagrams can be customized using Mermaid's styling and configuration options.

### Using classDef for Styling

You can define custom styles for nodes using the `classDef` syntax, which is a standard feature across many Mermaid diagram types:

##### Code:

```
mermaidtreemap-beta
"Main"
    "A": 20
    "B":::important
        "B1": 10
        "B2": 15
    "C": 5

classDef important fill:#f96,stroke:#333,stroke-width:2px;
```

### Theme Configuration

You can customize the colors of your treemap using the theme configuration:

##### Code:

```
mermaid---
config:
    theme: 'forest'
---
treemap-beta
"Category A"
    "Item A1": 10
    "Item A2": 20
"Category B"
    "Item B1": 15
    "Item B2": 25
```

### Diagram Padding

You can adjust the padding around the treemap diagram using the `diagramPadding` configuration option:

##### Code:

```
mermaid---
config:
  treemap:
    diagramPadding: 200
---
treemap-beta
"Category A"
    "Item A1": 10
    "Item A2": 20
"Category B"
    "Item B1": 15
    "Item B2": 25
```

## Configuration Options

The treemap diagram supports the following configuration options:

| Option | Description | Default |
| --- | --- | --- |
| useMaxWidth | When true, the diagram width is set to 100% and scales with available space | true |
| padding | Internal padding between nodes | 10 |
| diagramPadding | Padding around the entire diagram | 8 |
| showValues | Whether to show values in the treemap | true |
| nodeWidth | Width of nodes | 100 |
| nodeHeight | Height of nodes | 40 |
| borderWidth | Width of borders | 1 |
| valueFontSize | Font size for values | 12 |
| labelFontSize | Font size for labels | 14 |
| valueFormat | Format for values (see Value Formatting section) | ',' |

## Advanced Features

### Value Formatting

Values in treemap diagrams can be formatted to display in different ways using the `valueFormat` configuration option. This option primarily uses [D3's format specifiers](https://github.com/d3/d3-format#locale_format) to control how numbers are displayed, with some additional special cases for common formats.

Some common format patterns:

- `,` - Thousands separator (default)
- `$` - Add dollar sign
- `.1f` - Show one decimal place
- `.1%` - Show as percentage with one decimal place
- `$0,0` - Dollar sign with thousands separator
- `$.2f` - Dollar sign with 2 decimal places
- `$,.2f` - Dollar sign with thousands separator and 2 decimal places

The treemap diagram supports both standard D3 format specifiers and some common currency formats that combine the dollar sign with other formatting options.

Example with currency formatting:

##### Code:

```
mermaid---
config:
  treemap:
    valueFormat: '$0,0'
---
treemap-beta
"Budget"
    "Operations"
        "Salaries": 700000
        "Equipment": 200000
        "Supplies": 100000
    "Marketing"
        "Advertising": 400000
        "Events": 100000
```

Example with percentage formatting:

## Common Use Cases

Treemap diagrams are commonly used for:

1. **Financial Data**: Visualizing budget allocations, market shares, or portfolio compositions
2. **File System Analysis**: Showing disk space usage by folders and files
3. **Population Demographics**: Displaying population distribution across regions and subregions
4. **Product Hierarchies**: Visualizing product categories and their sales volumes
5. **Organizational Structures**: Representing departments and team sizes in a company

## Limitations

- Treemap diagrams work best when the data has a natural hierarchy
- Very small values may be difficult to see or label in a treemap diagram
- Deep hierarchies (many levels) can be challenging to represent clearly
- Treemap diagrams are not well suited for representing data with negative values

If treemap diagrams don't suit your needs, consider these alternatives:

- [**Pie Charts**](https://mermaid.ai/open-source/syntax/pie.html): For simple proportion comparisons without hierarchy
- **Sunburst Diagrams**: For hierarchical data with a radial layout (yet to be released in Mermaid).
- [**Sankey Diagrams**](https://mermaid.ai/open-source/syntax/sankey.html): For flow-based hierarchical data

## Notes

The treemap diagram implementation in Mermaid is designed to be simple to use while providing powerful visualization capabilities. As this is a newer diagram type, feedback and feature requests are welcome through the Mermaid GitHub repository.