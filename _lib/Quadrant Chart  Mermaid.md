## Quadrant Chart

> A quadrant chart is a visual representation of data that is divided into four quadrants. It is used to plot data points on a two-dimensional grid, with one variable represented on the x-axis and another variable represented on the y-axis. The quadrants are determined by dividing the chart into four equal parts based on a set of criteria that is specific to the data being analyzed. Quadrant charts are often used to identify patterns and trends in data, and to prioritize actions based on the position of data points within the chart. They are commonly used in business, marketing, and risk management, among other fields.

## Example

<svg id="mermaid-11" width="100%" xmlns="http://www.w3.org/2000/svg" style="max-width: 500px;" viewBox="0 0 500 500" role="graphics-document document" aria-roledescription="quadrantChart"><g></g><g class="main"><g class="quadrants"><g class="quadrant"><rect x="263" y="45" width="232" height="212" fill="#1f2020"></rect><text x="0" y="0" fill="#e0dfdf" font-size="16" dominant-baseline="hanging" text-anchor="middle" transform="translate(379, 50) rotate(0)">We should expand</text></g> <g class="quadrant"><rect x="31" y="45" width="232" height="212" fill="#242525"></rect><text x="0" y="0" fill="#dbdada" font-size="16" dominant-baseline="hanging" text-anchor="middle" transform="translate(147, 50) rotate(0)">Need to promote</text></g> <g class="quadrant"><rect x="31" y="257" width="232" height="212" fill="#292a2a"></rect><text x="0" y="0" fill="#d6d5d5" font-size="16" dominant-baseline="hanging" text-anchor="middle" transform="translate(147, 262) rotate(0)">Re-evaluate</text></g> <g class="quadrant"><rect x="263" y="257" width="232" height="212" fill="#2e2f2f"></rect><text x="0" y="0" fill="#d1d0d0" font-size="16" dominant-baseline="hanging" text-anchor="middle" transform="translate(379, 262) rotate(0)">May be improved</text></g></g> <g class="border"><line x1="30" y1="45" x2="496" y2="45" style="stroke: rgb(204, 204, 204); stroke-width: 2px;"></line><line x1="495" y1="46" x2="495" y2="468" style="stroke: rgb(204, 204, 204); stroke-width: 2px;"></line><line x1="30" y1="469" x2="496" y2="469" style="stroke: rgb(204, 204, 204); stroke-width: 2px;"></line><line x1="31" y1="46" x2="31" y2="468" style="stroke: rgb(204, 204, 204); stroke-width: 2px;"></line><line x1="263" y1="46" x2="263" y2="468" style="stroke: rgb(204, 204, 204); stroke-width: 1px;"></line><line x1="32" y1="257" x2="494" y2="257" style="stroke: rgb(204, 204, 204); stroke-width: 1px;"></line></g><g class="data-points"><g class="data-point"><circle cx="193.4" cy="138.28" r="5" fill="hsl(180, 1.5873015873%, NaN%)" stroke="hsl(180, 1.5873015873%, NaN%)" stroke-width="0px"></circle><text x="0" y="0" fill="#e0dfdf" font-size="12" dominant-baseline="hanging" text-anchor="middle" transform="translate(193.4, 143.28) rotate(0)">Campaign F</text></g> <g class="data-point"><circle cx="216.6" cy="324.84" r="5" fill="hsl(180, 1.5873015873%, NaN%)" stroke="hsl(180, 1.5873015873%, NaN%)" stroke-width="0px"></circle><text x="0" y="0" fill="#e0dfdf" font-size="12" dominant-baseline="hanging" text-anchor="middle" transform="translate(216.6, 329.84) rotate(0)">Campaign E</text></g> <g class="data-point"><circle cx="392.92" cy="324.84" r="5" fill="hsl(180, 1.5873015873%, NaN%)" stroke="hsl(180, 1.5873015873%, NaN%)" stroke-width="0px"></circle><text x="0" y="0" fill="#e0dfdf" font-size="12" dominant-baseline="hanging" text-anchor="middle" transform="translate(392.92, 329.84) rotate(0)">Campaign D</text></g> <g class="data-point"><circle cx="295.47999999999996" cy="176.44" r="5" fill="hsl(180, 1.5873015873%, NaN%)" stroke="hsl(180, 1.5873015873%, NaN%)" stroke-width="0px"></circle><text x="0" y="0" fill="#e0dfdf" font-size="12" dominant-baseline="hanging" text-anchor="middle" transform="translate(295.47999999999996, 181.44) rotate(0)">Campaign C</text></g> <g class="data-point"><circle cx="239.8" cy="371.48" r="5" fill="hsl(180, 1.5873015873%, NaN%)" stroke="hsl(180, 1.5873015873%, NaN%)" stroke-width="0px"></circle><text x="0" y="0" fill="#e0dfdf" font-size="12" dominant-baseline="hanging" text-anchor="middle" transform="translate(239.8, 376.48) rotate(0)">Campaign B</text></g> <g class="data-point"><circle cx="170.2" cy="214.60000000000002" r="5" fill="hsl(180, 1.5873015873%, NaN%)" stroke="hsl(180, 1.5873015873%, NaN%)" stroke-width="0px"></circle><text x="0" y="0" fill="#e0dfdf" font-size="12" dominant-baseline="hanging" text-anchor="middle" transform="translate(170.2, 219.60000000000002) rotate(0)">Campaign A</text></g></g> <g class="labels"><g class="label"><text x="0" y="0" fill="#e0dfdf" font-size="16" dominant-baseline="hanging" text-anchor="middle" transform="translate(147, 479) rotate(0)">Low Reach</text></g> <g class="label"><text x="0" y="0" fill="#e0dfdf" font-size="16" dominant-baseline="hanging" text-anchor="middle" transform="translate(379, 479) rotate(0)">High Reach</text></g> <g class="label"><text x="0" y="0" fill="#e0dfdf" font-size="16" dominant-baseline="hanging" text-anchor="middle" transform="translate(5, 363) rotate(-90)">Low Engagement</text></g> <g class="label"><text x="0" y="0" fill="#e0dfdf" font-size="16" dominant-baseline="hanging" text-anchor="middle" transform="translate(5, 151) rotate(-90)">High Engagement</text></g></g> <g class="title"><text x="0" y="0" fill="#e0dfdf" font-size="20" dominant-baseline="hanging" text-anchor="middle" transform="translate(250, 10) rotate(0)">Reach and engagement of campaigns</text></g></g></svg>

##### Code:

```
mermaidquadrantChart
    title Reach and engagement of campaigns
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
    Campaign C: [0.57, 0.69]
    Campaign D: [0.78, 0.34]
    Campaign E: [0.40, 0.34]
    Campaign F: [0.35, 0.78]
```

## Syntax

INFO

If there are no points available in the chart both **axis** text and **quadrant** will be rendered in the center of the respective quadrant. If there are points **x-axis** labels will rendered from the left of the respective quadrant also they will be displayed at the bottom of the chart, and **y-axis** labels will be rendered at the bottom of the respective quadrant, the quadrant text will render at the top of the respective quadrant.

INFO

For points x and y value min value is 0 and max value is 1.

The title is a short description of the chart and it will always render on top of the chart.

#### Example

### x-axis

The x-axis determines what text would be displayed in the x-axis. In x-axis there is two part **left** and **right** you can pass **both** or you can pass only **left**. The statement should start with `x-axis` then the `left axis text` followed by the delimiter `-->` then `right axis text`.

#### Example

1. `x-axis <text> --> <text>` both the left and right axis text will be rendered.
2. `x-axis <text>` only the left axis text will be rendered.

### y-axis

The y-axis determines what text would be displayed in the y-axis. In y-axis there is two part **top** and **bottom** you can pass **both** or you can pass only **bottom**. The statement should start with `y-axis` then the `bottom axis text` followed by the delimiter `-->` then `top axis text`.

#### Example

1. `y-axis <text> --> <text>` both the bottom and top axis text will be rendered.
2. `y-axis <text>` only the bottom axis text will be rendered.

### Quadrants text

The `quadrant-[1,2,3,4]` determine what text would be displayed inside the quadrants.

#### Example

1. `quadrant-1 <text>` determine what text will be rendered inside the top right quadrant.
2. `quadrant-2 <text>` determine what text will be rendered inside the top left quadrant.
3. `quadrant-3 <text>` determine what text will be rendered inside the bottom left quadrant.
4. `quadrant-4 <text>` determine what text will be rendered inside the bottom right quadrant.

### Points

Points are used to plot a circle inside the quadrantChart. The syntax is `<text>: [x, y]` here x and y value is in the range 0 - 1.

#### Example

1. `Point 1: [0.75, 0.80]` here the Point 1 will be drawn in the top right quadrant.
2. `Point 2: [0.35, 0.24]` here the Point 2 will be drawn in the bottom left quadrant.

## Chart Configurations

| Parameter | Description | Default value |
| --- | --- | --- |
| chartWidth | Width of the chart | 500 |
| chartHeight | Height of the chart | 500 |
| titlePadding | Top and Bottom padding of the title | 10 |
| titleFontSize | Title font size | 20 |
| quadrantPadding | Padding outside all the quadrants | 5 |
| quadrantTextTopPadding | Quadrant text top padding when text is drawn on top ( not data points are there) | 5 |
| quadrantLabelFontSize | Quadrant text font size | 16 |
| quadrantInternalBorderStrokeWidth | Border stroke width inside the quadrants | 1 |
| quadrantExternalBorderStrokeWidth | Quadrant external border stroke width | 2 |
| xAxisLabelPadding | Top and bottom padding of x-axis text | 5 |
| xAxisLabelFontSize | X-axis texts font size | 16 |
| xAxisPosition | Position of x-axis (top, bottom) if there are points the x-axis will always be rendered in bottom | 'top' |
| yAxisLabelPadding | Left and Right padding of y-axis text | 5 |
| yAxisLabelFontSize | Y-axis texts font size | 16 |
| yAxisPosition | Position of y-axis (left, right) | 'left' |
| pointTextPadding | Padding between point and the below text | 5 |
| pointLabelFontSize | Point text font size | 12 |
| pointRadius | Radius of the point to be drawn | 5 |

## Chart Theme Variables

| Parameter | Description |
| --- | --- |
| quadrant1Fill | Fill color of the top right quadrant |
| quadrant2Fill | Fill color of the top left quadrant |
| quadrant3Fill | Fill color of the bottom left quadrant |
| quadrant4Fill | Fill color of the bottom right quadrant |
| quadrant1TextFill | Text color of the top right quadrant |
| quadrant2TextFill | Text color of the top left quadrant |
| quadrant3TextFill | Text color of the bottom left quadrant |
| quadrant4TextFill | Text color of the bottom right quadrant |
| quadrantPointFill | Points fill color |
| quadrantPointTextFill | Points text color |
| quadrantXAxisTextFill | X-axis text color |
| quadrantYAxisTextFill | Y-axis text color |
| quadrantInternalBorderStrokeFill | Quadrants inner border color |
| quadrantExternalBorderStrokeFill | Quadrants outer border color |
| quadrantTitleFill | Title color |

## Example on config and theme

##### Code:

```
mermaid---
config:
  quadrantChart:
    chartWidth: 400
    chartHeight: 400
  themeVariables:
    quadrant1TextFill: "ff0000"
---
quadrantChart
  x-axis Urgent --> Not Urgent
  y-axis Not Important --> "Important ❤"
  quadrant-1 Plan
  quadrant-2 Do
  quadrant-3 Delegate
  quadrant-4 Delete
```

### Point styling

Points can either be styled directly or with defined shared classes

1. Direct styling
1. Classes styling

#### Available styles:

| Parameter | Description |
| --- | --- |
| color | Fill color of the point |
| radius | Radius of the point |
| stroke-width | Border width of the point |
| stroke-color | Border color of the point (useless when stroke-width is not specified) |

INFO

Order of preference:

1. Direct styles
2. Class styles
3. Theme styles

## Example on styling

##### Code:

```
mermaidquadrantChart
  title Reach and engagement of campaigns
  x-axis Low Reach --> High Reach
  y-axis Low Engagement --> High Engagement
  quadrant-1 We should expand
  quadrant-2 Need to promote
  quadrant-3 Re-evaluate
  quadrant-4 May be improved
  Campaign A: [0.9, 0.0] radius: 12
  Campaign B:::class1: [0.8, 0.1] color: #ff3300, radius: 10
  Campaign C: [0.7, 0.2] radius: 25, color: #00ff33, stroke-color: #10f0f0
  Campaign D: [0.6, 0.3] radius: 15, stroke-color: #00ff0f, stroke-width: 5px ,color: #ff33f0
  Campaign E:::class2: [0.5, 0.4]
  Campaign F:::class3: [0.4, 0.5] color: #0000ff
  classDef class1 color: #109060
  classDef class2 color: #908342, radius : 10, stroke-color: #310085, stroke-width: 10px
  classDef class3 color: #f00fff, radius : 10
```