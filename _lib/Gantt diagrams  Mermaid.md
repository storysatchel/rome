## Gantt diagrams

> A Gantt chart is a type of bar chart, first developed by Karol Adamiecki in 1896, and independently by Henry Gantt in the 1910s, that illustrates a project schedule and the amount of time it would take for any one project to finish. Gantt charts illustrate number of days between the start and finish dates of the terminal elements and summary elements of a project.

## A note to users

Gantt Charts will record each scheduled task as one continuous bar that extends from the left to the right. The x axis represents time and the y records the different tasks and the order in which they are to be completed.

It is important to remember that when a date, day, or collection of dates specific to a task are "excluded", the Gantt Chart will accommodate those changes by extending an equal number of days, towards the right, not by creating a gap inside the task. As shown here ![](https://mermaid.ai/open-source/assets/Gantt-excluded-days-within.CnbiXDeL.png)

However, if the excluded dates are between two tasks that are set to start consecutively, the excluded dates will be skipped graphically and left blank, and the following task will begin after the end of the excluded dates. As shown here ![](https://mermaid.ai/open-source/assets/Gantt-long-weekend-look.Dnhs3MQQ.png)

A Gantt chart is useful for tracking the amount of time it would take before a project is finished, but it can also be used to graphically represent "non-working days", with a few tweaks.

Mermaid can render Gantt diagrams as SVG, PNG or a MarkDown link that can be pasted into docs.

<svg id="mermaid-26" width="100%" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1912 196" style="max-width: 1912px;" role="graphics-document document" aria-roledescription="gantt"><g></g><g class="grid" transform="translate(75, 146)" fill="none" font-size="10" font-family="sans-serif" text-anchor="middle"><path class="domain" stroke="currentColor" d="M0.5,-111V0.5H1762.5V-111"></path><g class="tick" opacity="1" transform="translate(141.5,0)"><line stroke="currentColor" y2="-111"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-05</text></g> <g class="tick" opacity="1" transform="translate(388.5,0)"><line stroke="currentColor" y2="-111"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-12</text></g> <g class="tick" opacity="1" transform="translate(634.5,0)"><line stroke="currentColor" y2="-111"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-19</text></g> <g class="tick" opacity="1" transform="translate(881.5,0)"><line stroke="currentColor" y2="-111"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-26</text></g> <g class="tick" opacity="1" transform="translate(1128.5,0)"><line stroke="currentColor" y2="-111"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-02-02</text></g> <g class="tick" opacity="1" transform="translate(1374.5,0)"><line stroke="currentColor" y2="-111"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-02-09</text></g> <g class="tick" opacity="1" transform="translate(1621.5,0)"><line stroke="currentColor" y2="-111"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-02-16</text></g></g> <g><rect x="0" y="48" width="1874.5" height="24" class="section section0"></rect><rect x="0" y="96" width="1874.5" height="24" class="section section1"></rect><rect x="0" y="120" width="1874.5" height="24" class="section section1"></rect><rect x="0" y="72" width="1874.5" height="24" class="section section0"></rect></g><g><rect id="mermaid-26-a1" rx="3" ry="3" x="75" y="50" width="1057" height="20" transform-origin="603.5px 60px" class="task task0 "></rect><rect id="mermaid-26-task2" rx="3" ry="3" x="463" y="98" width="423" height="20" transform-origin="674.5px 108px" class="task task1 "></rect><rect id="mermaid-26-task3" rx="3" ry="3" x="886" y="122" width="845" height="20" transform-origin="1308.5px 132px" class="task task1 "></rect><rect id="mermaid-26-task1" rx="3" ry="3" x="1132" y="74" width="705" height="20" transform-origin="1484.5px 84px" class="task task0 "></rect><text id="mermaid-26-a1-text" font-size="11" x="603.5" y="63.5" text-height="20" class=" taskText taskText0  width-34.099998474121094">A task </text><text id="mermaid-26-task2-text" font-size="11" x="674.5" y="111.5" text-height="20" class=" taskText taskText1  width-79.18333435058594">Task in Another </text><text id="mermaid-26-task3-text" font-size="11" x="1308.5" y="135.5" text-height="20" class=" taskText taskText1  width-64.06666564941406">another task </text><text id="mermaid-26-task1-text" font-size="11" x="1484.5" y="87.5" text-height="20" class=" taskText taskText0  width-65.28333282470703">Another task </text></g><g><text dy="0em" x="10" y="74" font-size="11" class="sectionTitle sectionTitle0"><tspan alignment-baseline="central" x="10">Section</tspan></text> <text dy="0em" x="10" y="122" font-size="11" class="sectionTitle sectionTitle1"><tspan alignment-baseline="central" x="10">Another</tspan></text></g> <g class="today"><line x1="165484" x2="165484" y1="25" y2="171" class="today"></line></g><text x="956" y="25" class="titleText">A Gantt Diagram</text></svg>

##### Code:

```
mermaidgantt
    title A Gantt Diagram
    dateFormat YYYY-MM-DD
    section Section
        A task          :a1, 2014-01-01, 30d
        Another task    :after a1, 20d
    section Another
        Task in Another :2014-01-12, 12d
        another task    :24d
```

## Syntax

<svg id="mermaid-30" width="100%" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1912 508" style="max-width: 1912px;" role="graphics-document document" aria-roledescription="gantt"><g></g><g><rect id="mermaid-30-exclude-2014-01-11" x="475" y="35" width="161" height="423" transform-origin="515.5px 254px" class="exclude-range"></rect><rect id="mermaid-30-exclude-2014-01-18" x="1036" y="35" width="160" height="423" transform-origin="1076px 278px" class="exclude-range"></rect><rect id="mermaid-30-exclude-2014-01-25" x="1597" y="35" width="160" height="423" transform-origin="1637px 302px" class="exclude-range"></rect></g><g class="grid" transform="translate(75, 458)" fill="none" font-size="10" font-family="sans-serif" text-anchor="middle"><path class="domain" stroke="currentColor" d="M0.5,-423V0.5H1762.5V-423"></path><g class="tick" opacity="1" transform="translate(80.5,0)"><line stroke="currentColor" y2="-423"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-07</text></g> <g class="tick" opacity="1" transform="translate(240.5,0)"><line stroke="currentColor" y2="-423"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-09</text></g> <g class="tick" opacity="1" transform="translate(400.5,0)"><line stroke="currentColor" y2="-423"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-11</text></g> <g class="tick" opacity="1" transform="translate(561.5,0)"><line stroke="currentColor" y2="-423"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-13</text></g> <g class="tick" opacity="1" transform="translate(721.5,0)"><line stroke="currentColor" y2="-423"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-15</text></g> <g class="tick" opacity="1" transform="translate(881.5,0)"><line stroke="currentColor" y2="-423"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-17</text></g> <g class="tick" opacity="1" transform="translate(1041.5,0)"><line stroke="currentColor" y2="-423"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-19</text></g> <g class="tick" opacity="1" transform="translate(1201.5,0)"><line stroke="currentColor" y2="-423"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-21</text></g> <g class="tick" opacity="1" transform="translate(1362.5,0)"><line stroke="currentColor" y2="-423"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-23</text></g> <g class="tick" opacity="1" transform="translate(1522.5,0)"><line stroke="currentColor" y2="-423"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-25</text></g> <g class="tick" opacity="1" transform="translate(1682.5,0)"><line stroke="currentColor" y2="-423"></line><text fill="#000" y="3" dy="1em" style="text-anchor: middle;" stroke="none" font-size="10">2014-01-27</text></g></g> <g><rect x="0" y="48" width="1874.5" height="24" class="section section0"></rect><rect x="0" y="144" width="1874.5" height="24" class="section section1"></rect><rect x="0" y="168" width="1874.5" height="24" class="section section1"></rect><rect x="0" y="312" width="1874.5" height="24" class="section section2"></rect><rect x="0" y="72" width="1874.5" height="24" class="section section0"></rect><rect x="0" y="192" width="1874.5" height="24" class="section section1"></rect><rect x="0" y="336" width="1874.5" height="24" class="section section2"></rect><rect x="0" y="360" width="1874.5" height="24" class="section section2"></rect><rect x="0" y="96" width="1874.5" height="24" class="section section0"></rect><rect x="0" y="216" width="1874.5" height="24" class="section section1"></rect><rect x="0" y="384" width="1874.5" height="24" class="section section3"></rect><rect x="0" y="408" width="1874.5" height="24" class="section section3"></rect><rect x="0" y="432" width="1874.5" height="24" class="section section3"></rect><rect x="0" y="120" width="1874.5" height="24" class="section section0"></rect><rect x="0" y="240" width="1874.5" height="24" class="section section1"></rect><rect x="0" y="264" width="1874.5" height="24" class="section section1"></rect><rect x="0" y="288" width="1874.5" height="24" class="section section1"></rect></g><g><rect id="mermaid-30-des1" rx="3" ry="3" x="75" y="50" width="160" height="20" transform-origin="155px 60px" class="task done0 "></rect><rect id="mermaid-30-task1" rx="3" ry="3" x="75" y="146" width="80" height="20" transform-origin="115px 156px" class="task doneCrit1 "></rect><rect id="mermaid-30-task2" rx="3" ry="3" x="235" y="170" width="160" height="20" transform-origin="315px 180px" class="task doneCrit1 "></rect><rect id="mermaid-30-a1" rx="3" ry="3" x="235" y="314" width="240" height="20" transform-origin="435.5px 324px" class="task active2 "></rect><rect id="mermaid-30-des2" rx="3" ry="3" x="315" y="74" width="401" height="20" transform-origin="515.5px 84px" class="task active0 "></rect><rect id="mermaid-30-task3" rx="3" ry="3" x="395" y="194" width="401" height="20" transform-origin="595.5px 204px" class="task activeCrit1 "></rect><rect id="mermaid-30-task7" rx="3" ry="3" x="636" y="338" width="66" height="20" transform-origin="669px 348px" class="task task2 "></rect><rect id="mermaid-30-doc1" rx="3" ry="3" x="636" y="362" width="160" height="20" transform-origin="716px 372px" class="task task2 "></rect><rect id="mermaid-30-des3" rx="3" ry="3" x="716" y="98" width="560" height="20" transform-origin="996px 108px" class="task task0 "></rect><rect id="mermaid-30-task4" rx="3" ry="3" x="796" y="218" width="560" height="20" transform-origin="1076px 228px" class="task crit1 "></rect><rect id="mermaid-30-task8" rx="3" ry="3" x="796" y="386" width="240" height="20" transform-origin="996px 396px" class="task task3 "></rect><rect id="mermaid-30-task9" rx="3" ry="3" x="1196" y="410" width="67" height="20" transform-origin="1229.5px 420px" class="task task3 "></rect><rect id="mermaid-30-task10" rx="3" ry="3" x="1263" y="434" width="160" height="20" transform-origin="1343px 444px" class="task task3 "></rect><rect id="mermaid-30-des4" rx="3" ry="3" x="1276" y="122" width="561" height="20" transform-origin="1556.5px 132px" class="task task0 "></rect><rect id="mermaid-30-task5" rx="3" ry="3" x="1356" y="242" width="161" height="20" transform-origin="1436.5px 252px" class="task task1 "></rect><rect id="mermaid-30-task6" rx="3" ry="3" x="1517" y="266" width="80" height="20" transform-origin="1637px 276px" class="task task1 "></rect><rect id="mermaid-30-isadded" rx="3" ry="3" x="1587" y="290" width="20" height="20" transform-origin="1597px 300px" class="task milestone  task1 "></rect><text id="mermaid-30-des1-text" font-size="11" x="155" y="63.5" text-height="20" class=" taskText taskText0  doneText0 width-79.96666717529297">Completed task </text><text id="mermaid-30-task1-text" font-size="11" x="160" y="159.5" text-height="20" class=" taskTextOutsideRight taskTextOutside1  doneCritText1 width-163.8333282470703">Completed task in the critical line </text><text id="mermaid-30-task2-text" font-size="11" x="315" y="183.5" text-height="20" class=" taskText taskText1  doneCritText1 width-135.71665954589844">Implement parser and jison </text><text id="mermaid-30-a1-text" font-size="11" x="355" y="327.5" text-height="20" class=" taskText taskText2 activeText2 width-109.30000305175781">Describe gantt syntax </text><text id="mermaid-30-des2-text" font-size="11" x="515.5" y="87.5" text-height="20" class=" taskText taskText0 activeText0 width-56.71666717529297">Active task </text><text id="mermaid-30-task3-text" font-size="11" x="595.5" y="207.5" text-height="20" class=" taskText taskText1 activeCritText1 critText1 width-112.78333282470703">Create tests for parser </text><text id="mermaid-30-task7-text" font-size="11" x="707" y="351.5" text-height="20" class=" taskTextOutsideRight taskTextOutside2  width-163.21665954589844">Add gantt diagram to demo page </text><text id="mermaid-30-doc1-text" font-size="11" x="801" y="375.5" text-height="20" class=" taskTextOutsideRight taskTextOutside2  width-176.06666564941406">Add another diagram to demo page </text><text id="mermaid-30-des3-text" font-size="11" x="996" y="111.5" text-height="20" class=" taskText taskText0  width-58.54999923706055">Future task </text><text id="mermaid-30-task4-text" font-size="11" x="1076" y="231.5" text-height="20" class=" taskText taskText1  critText1 width-124.08333587646484">Future task in critical line </text><text id="mermaid-30-task8-text" font-size="11" x="916" y="399.5" text-height="20" class=" taskText taskText3  width-109.30000305175781">Describe gantt syntax </text><text id="mermaid-30-task9-text" font-size="11" x="1268" y="423.5" text-height="20" class=" taskTextOutsideRight taskTextOutside3  width-163.21665954589844">Add gantt diagram to demo page </text><text id="mermaid-30-task10-text" font-size="11" x="1428" y="447.5" text-height="20" class=" taskTextOutsideRight taskTextOutside3  width-176.06666564941406">Add another diagram to demo page </text><text id="mermaid-30-des4-text" font-size="11" x="1556.5" y="135.5" text-height="20" class=" taskText taskText0  width-64.16666412353516">Future task2 </text><text id="mermaid-30-task5-text" font-size="11" x="1436.5" y="255.5" text-height="20" class=" taskText taskText1  width-123.18333435058594">Create tests for renderer </text><text id="mermaid-30-task6-text" font-size="11" x="1602" y="279.5" text-height="20" class=" taskText taskText1  width-80.68333435058594">Add to mermaid </text><text id="mermaid-30-isadded-text" font-size="11" x="1612" y="303.5" text-height="20" class=" taskTextOutsideRight taskTextOutside1  milestoneText width-98.43333435058594">Functionality added </text></g><g><text dy="0em" x="10" y="98" font-size="11" class="sectionTitle sectionTitle0"><tspan alignment-baseline="central" x="10">A section</tspan></text> <text dy="0em" x="10" y="230" font-size="11" class="sectionTitle sectionTitle1"><tspan alignment-baseline="central" x="10">Critical tasks</tspan></text> <text dy="0em" x="10" y="350" font-size="11" class="sectionTitle sectionTitle2"><tspan alignment-baseline="central" x="10">Documentation</tspan></text> <text dy="0em" x="10" y="422" font-size="11" class="sectionTitle sectionTitle3"><tspan alignment-baseline="central" x="10">Last section</tspan></text></g> <g class="today"><line x1="375604" x2="375604" y1="25" y2="483" class="today"></line></g><text x="956" y="25" class="titleText">Adding GANTT diagram functionality to mermaid</text></svg>

##### Code:

```
mermaidgantt
    dateFormat  YYYY-MM-DD
    title       Adding GANTT diagram functionality to mermaid
    excludes    weekends
    %% (\`excludes\` accepts specific dates in YYYY-MM-DD format, days of the week ("sunday") or "weekends", but not the word "weekdays".)

    section A section
    Completed task            :done,    des1, 2014-01-06,2014-01-08
    Active task               :active,  des2, 2014-01-09, 3d
    Future task               :         des3, after des2, 5d
    Future task2              :         des4, after des3, 5d

    section Critical tasks
    Completed task in the critical line :crit, done, 2014-01-06,24h
    Implement parser and jison          :crit, done, after des1, 2d
    Create tests for parser             :crit, active, 3d
    Future task in critical line        :crit, 5d
    Create tests for renderer           :2d
    Add to mermaid                      :until isadded
    Functionality added                 :milestone, isadded, 2014-01-25, 0d

    section Documentation
    Describe gantt syntax               :active, a1, after des1, 3d
    Add gantt diagram to demo page      :after a1  , 20h
    Add another diagram to demo page    :doc1, after a1  , 48h

    section Last section
    Describe gantt syntax               :after doc1, 3d
    Add gantt diagram to demo page      :20h
    Add another diagram to demo page    :48h
```

Tasks are by default sequential. A task start date defaults to the end date of the preceding task.

A colon, `:`, separates the task title from its metadata. Metadata items are separated by a comma, `,`. Valid tags are `active`, `done`, `crit`, and `milestone`. Tags are optional, but if used, they must be specified first. After processing the tags, the remaining metadata items are interpreted as follows:

1. If a single item is specified, it determines when the task ends. It can either be a specific date/time or a duration. If a duration is specified, it is added to the start date of the task to determine the end date of the task, taking into account any exclusions.
2. If two items are specified, the last item is interpreted as in the previous case. The first item can either specify an explicit start date/time (in the format specified by `dateFormat`) or reference another task using `after <otherTaskID> [[otherTaskID2 [otherTaskID3]]...]`. In the latter case, the start date of the task will be set according to the latest end date of any referenced task.
3. If three items are specified, the last two will be interpreted as in the previous case. The first item will denote the ID of the task, which can be referenced using the `later <taskID>` syntax.

| Metadata syntax | Start date | End date | ID |
| --- | --- | --- | --- |
| `<taskID>, <startDate>, <endDate>` | `startdate` as interpreted using `dateformat` | `endDate` as interpreted using `dateformat` | `taskID` |
| `<taskID>, <startDate>, <length>` | `startdate` as interpreted using `dateformat` | Start date + `length` | `taskID` |
| `<taskID>, after <otherTaskId>, <endDate>` | End date of previously specified task `otherTaskID` | `endDate` as interpreted using `dateformat` | `taskID` |
| `<taskID>, after <otherTaskId>, <length>` | End date of previously specified task `otherTaskID` | Start date + `length` | `taskID` |
| `<taskID>, <startDate>, until <otherTaskId>` | `startdate` as interpreted using `dateformat` | Start date of previously specified task `otherTaskID` | `taskID` |
| `<taskID>, after <otherTaskId>, until <otherTaskId>` | End date of previously specified task `otherTaskID` | Start date of previously specified task `otherTaskID` | `taskID` |
| `<startDate>, <endDate>` | `startdate` as interpreted using `dateformat` | `enddate` as interpreted using `dateformat` | n/a |
| `<startDate>, <length>` | `startdate` as interpreted using `dateformat` | Start date + `length` | n/a |
| `after <otherTaskID>, <endDate>` | End date of previously specified task `otherTaskID` | `enddate` as interpreted using `dateformat` | n/a |
| `after <otherTaskID>, <length>` | End date of previously specified task `otherTaskID` | Start date + `length` | n/a |
| `<startDate>, until <otherTaskId>` | `startdate` as interpreted using `dateformat` | Start date of previously specified task `otherTaskID` | n/a |
| `after <otherTaskId>, until <otherTaskId>` | End date of previously specified task `otherTaskID` | Start date of previously specified task `otherTaskID` | n/a |
| `<endDate>` | End date of preceding task | `enddate` as interpreted using `dateformat` | n/a |
| `<length>` | End date of preceding task | Start date + `length` | n/a |
| `until <otherTaskId>` | End date of preceding task | Start date of previously specified task `otherTaskID` | n/a |

INFO

Support for keyword `until` was added in (v10.9.0+). This can be used to define a task which is running until some other specific task or milestone starts.

#### Duration format

When specifying a `<length>`, use a number followed by one of these unit suffixes:

| Unit | Suffix | Example |
| --- | --- | --- |
| Milliseconds | `ms` | `500ms` |
| Seconds | `s` | `30s` |
| Minutes | `m` | `30m` |
| Hours | `h` | `4h` |
| Days | `d` | `3d` |
| Weeks | `w` | `2w` |
| Months | `M` | `1M` |
| Years | `y` | `1y` |

Decimal values are also supported (e.g., `1.5d`). Invalid duration tokens (e.g., `3dX`) will be ignored and the task will default to zero duration.

For simplicity, the table does not show the use of multiple tasks listed with the `after` keyword. Here is an example of how to use it and how it's interpreted:

##### Code:

```
mermaidgantt
    apple :a, 2017-07-20, 1w
    banana :crit, b, 2017-07-23, 1d
    cherry :active, c, after b a, 1d
    kiwi   :d, 2017-07-20, until b c
```

The `title` is an *optional* string to be displayed at the top of the Gantt chart to describe the chart as a whole.

### Excludes

The `excludes` is an *optional* attribute that accepts specific dates in YYYY-MM-DD format, days of the week ("sunday") or "weekends", but not the word "weekdays". These date will be marked on the graph, and be excluded from the duration calculation of tasks. Meaning that if there are excluded dates during a task interval, the number of 'skipped' days will be added to the end of the task to ensure the duration is as specified in the code.

Multiple `excludes` lines are supported and their tokens are concatenated, so long exclusion lists can be split across grouped lines with comments:

#### Weekend (v\\11.0.0+)

When excluding weekends, it is possible to configure the weekends to be either Friday and Saturday or Saturday and Sunday. By default weekends are Saturday and Sunday. To define the weekend start day, there is an *optional* attribute `weekend` that can be added in a new line followed by either `friday` or `saturday`.

##### Code:

```
mermaidgantt
    title A Gantt Diagram Excluding Fri - Sat weekends
    dateFormat YYYY-MM-DD
    excludes weekends
    weekend friday
    section Section
        A task          :a1, 2024-01-01, 30d
        Another task    :after a1, 20d
```

### Section statements

You can divide the chart into various sections, for example to separate different parts of a project like development and documentation.

To do so, start a line with the `section` keyword and give it a name. (Note that unlike with the [title for the entire chart](https://mermaid.ai/open-source/syntax/#title), this name is *required*.

### Milestones

You can add milestones to the diagrams. Milestones differ from tasks as they represent a single instant in time and are identified by the keyword `milestone`. Below is an example on how to use milestones. As you may notice, the exact location of the milestone is determined by the initial date for the milestone and the "duration" of the task this way: *initial date* + *duration* /2.

##### Code:

```
mermaidgantt
    dateFormat HH:mm
    axisFormat %H:%M
    Initial milestone : milestone, m1, 17:49, 2m
    Task A : 10m
    Task B : 5m
    Final milestone : milestone, m2, 18:08, 4m
```

### Vertical Markers

The `vert` keyword lets you add vertical lines to your Gantt chart, making it easy to highlight important dates like deadlines, events, or checkpoints. These markers extend across the entire chart and are positioned based on the date you provide. Unlike milestones, vertical markers don’t take up a row. They’re purely visual reference points that help break up the timeline and make important moments easier to spot.

##### Code:

```
mermaidgantt
    dateFormat HH:mm
    axisFormat %H:%M
    Initial vert : vert, v1, 17:30, 2m
    Task A : 3m
    Task B : 8m
    Final vert : vert, v2, 17:58, 4m
```

## Setting dates

`dateFormat` defines the format of the date **input** of your gantt elements. How these dates are represented in the rendered chart **output** are defined by `axisFormat`.

### Input date format

The default input date format is `YYYY-MM-DD`. You can define your custom `dateFormat`.

```markdown
markdowndateFormat YYYY-MM-DD
```

The following formatting options are supported:

| Input | Example | Description |
| --- | --- | --- |
| `YYYY` | 2014 | 4 digit year |
| `YY` | 14 | 2 digit year |
| `Q` | 1..4 | Quarter of year. Sets month to first month in quarter. |
| `M MM` | 1..12 | Month number |
| `MMM MMMM` | January..Dec | Month name in locale set by `dayjs.locale()` |
| `D DD` | 1..31 | Day of month |
| `Do` | 1st..31st | Day of month with ordinal |
| `DDD DDDD` | 1..365 | Day of year |
| `X` | 1410715640.579 | Unix timestamp |
| `x` | 1410715640579 | Unix ms timestamp |
| `H HH` | 0..23 | 24 hour time |
| `h hh` | 1..12 | 12 hour time used with `a A`. |
| `a A` | am pm | Post or ante meridiem |
| `m mm` | 0..59 | Minutes |
| `s ss` | 0..59 | Seconds |
| `S` | 0..9 | Tenths of a second |
| `SS` | 0..99 | Hundreds of a second |
| `SSS` | 0..999 | Thousandths of a second |
| `Z ZZ` | +12:00 | Offset from UTC as +-HH:mm, +-HHmm, or Z |

More info in: [https://day.js.org/docs/en/parse/string-format/](https://day.js.org/docs/en/parse/string-format/)

### Output date format on the axis

The default output date format is `YYYY-MM-DD`. You can define your custom `axisFormat`, like `2020-Q1` for the first quarter of the year 2020.

```markdown
markdownaxisFormat %Y-%m-%d
```

The following formatting strings are supported:

| Format | Definition |
| --- | --- |
| %a | abbreviated weekday name |
| %A | full weekday name |
| %b | abbreviated month name |
| %B | full month name |
| %c | date and time, as "%a %b %e %H:%M:%S %Y" |
| %d | zero-padded day of the month as a decimal number \[01,31\] |
| %e | space-padded day of the month as a decimal number \[ 1,31\]; equivalent to %\_d |
| %H | hour (24-hour clock) as a decimal number \[00,23\] |
| %I | hour (12-hour clock) as a decimal number \[01,12\] |
| %j | day of the year as a decimal number \[001,366\] |
| %m | month as a decimal number \[01,12\] |
| %M | minute as a decimal number \[00,59\] |
| %L | milliseconds as a decimal number \[000, 999\] |
| %p | either AM or PM |
| %S | second as a decimal number \[00,61\] |
| %U | week number of the year (Sunday as the first day of the week) as a decimal number \[00,53\] |
| %w | weekday as a decimal number \[0(Sunday),6\] |
| %W | week number of the year (Monday as the first day of the week) as a decimal number \[00,53\] |
| %x | date, as "%m/%d/%Y" |
| %X | time, as "%H:%M:%S" |
| %y | year without century as a decimal number \[00,99\] |
| %Y | year with century as a decimal number |
| %Z | time zone offset, such as "-0700" |
| %% | a literal "%" character |

More info in: [https://github.com/d3/d3-time-format/tree/v4.0.0#locale\_format](https://github.com/d3/d3-time-format/tree/v4.0.0#locale_format)

### Axis ticks (v10.3.0+)

The default output ticks are auto. You can custom your `tickInterval`, like `1day` or `1week`.

```markdown
markdowntickInterval 1day
```

The pattern is:

```javascript
javascript/^([1-9][0-9]*)(millisecond|second|minute|hour|day|week|month)$/;
```

More info in: [https://github.com/d3/d3-time#interval\_every](https://github.com/d3/d3-time#interval_every)

Week-based `tickInterval` s start the week on sunday by default. If you wish to specify another weekday on which the `tickInterval` should start, use the `weekday` option:

##### Code:

```
mermaidgantt
  tickInterval 1week
  weekday monday
```

WARNING

`millisecond` and `second` support was added in v10.3.0

## Output in compact mode

The compact mode allows you to display multiple tasks in the same row. Compact mode can be enabled for a gantt chart by setting the display mode of the graph via preceding YAML settings.

##### Code:

```
mermaid---
displayMode: compact
---
gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD

    section Section
    A task           :a1, 2014-01-01, 30d
    Another task     :a2, 2014-01-20, 25d
    Another one      :a3, 2014-02-10, 20d
```

Comments can be entered within a gantt chart, which will be ignored by the parser. Comments need to be on their own line and must be prefaced with `%%` (double percent signs). Any text after the start of the comment to the next newline will be treated as a comment, including any diagram syntax.

##### Code:

```
mermaidgantt
    title A Gantt Diagram
    %% This is a comment
    dateFormat YYYY-MM-DD
    section Section
        A task          :a1, 2014-01-01, 30d
        Another task    :after a1, 20d
    section Another
        Task in Another :2014-01-12, 12d
        another task    :24d
```

## Styling

Styling of the Gantt diagram is done by defining a number of CSS classes. During rendering, these classes are extracted from the file located at src/diagrams/gantt/styles.js

### Classes used

| Class | Description |
| --- | --- |
| grid.tick | Styling for the Grid Lines |
| grid.path | Styling for the Grid's borders |
| .taskText | Task Text Styling |
| .taskTextOutsideRight | Styling for Task Text that exceeds the activity bar towards the right. |
| .taskTextOutsideLeft | Styling for Task Text that exceeds the activity bar, towards the left. |
| todayMarker | Toggle and Styling for the "Today Marker" |

### Sample stylesheet

## Today marker

You can style or hide the marker for the current date. To style it, add a value for the `todayMarker` key.

```
todayMarker stroke-width:5px,stroke:#0f0,opacity:0.5
```

To hide the marker, set `todayMarker` to `off`.

```
todayMarker off
```

## Configuration

It is possible to adjust the margins for rendering the gantt diagram.

This is done by defining the `ganttConfig` part of the configuration object. How to use the CLI is described in the [mermaidCLI](https://mermaid.ai/open-source/config/mermaidCLI.html) page.

mermaid.ganttConfig can be set to a JSON string with config parameters or the corresponding object.

```javascript
javascriptmermaid.ganttConfig = {

  titleTopMargin: 25, // Margin top for the text over the diagram

  barHeight: 20, // The height of the bars in the graph

  barGap: 4, // The margin between the different activities in the gantt diagram

  topPadding: 75, // Margin between title and gantt diagram and between axis and gantt diagram.

  rightPadding: 75, // The space allocated for the section name to the right of the activities

  leftPadding: 75, // The space allocated for the section name to the left of the activities

  gridLineStartPadding: 10, // Vertical starting position of the grid lines

  fontSize: 12, // Font size

  sectionFontSize: 24, // Font size for sections

  numberSectionStyles: 1, // The number of alternating section styles

  axisFormat: '%d/%m', // Date/time format of the axis

  tickInterval: '1week', // Axis ticks

  topAxis: true, // When this flag is set, date labels will be added to the top of the chart

  displayMode: 'compact', // Turns compact mode on

  weekday: 'sunday', // On which day a week-based interval should start

};
```

### Possible configuration params:

| Param | Description | Default value |
| --- | --- | --- |
| mirrorActor | Turns on/off the rendering of actors below the diagram as well as above it | false |
| bottomMarginAdj | Adjusts how far down the graph ended. Wide borders styles with css could generate unwanted clipping which is why this config param exists. | 1 |

It is possible to bind a click event to a task. The click can lead to either a javascript callback or to a link which will be opened in the current browser tab. **Note**: This functionality is disabled when using `securityLevel='strict'` and enabled when using `securityLevel='loose'`.

- taskId is the id of the task
- callback is the name of a javascript function defined on the page displaying the graph, the function will be called with the taskId as the parameter if no other arguments are specified.

Beginner's tip—a full example using interactive links in an HTML context:

## Examples

### Bar chart (using gantt chart)

##### Code:

```
mermaidgantt
    title Git Issues - days since last update
    dateFormat X
    axisFormat %s
    section Issue19062
    71   : 0, 71
    section Issue19401
    36   : 0, 36
    section Issue193
    34   : 0, 34
    section Issue7441
    9    : 0, 9
    section Issue1300
    5    : 0, 5
```

##### Code:

```
mermaid---
    # Frontmatter config, YAML comments
    title: Ignored if specified in chart
    displayMode: compact     #gantt specific setting but works at this level too
    config:
#        theme: forest
#        themeCSS: " #item36 { fill: CadetBlue } "
        themeCSS: " // YAML supports multiline strings using a newline markers: \n
            #item36 { fill: CadetBlue }       \n

            // Custom marker workaround CSS from forum (below)    \n
            rect[id^=workaround] { height: calc(100% - 50px) ; transform: translate(9px, 25px); y: 0; width: 1.5px; stroke: none; fill: red; }   \n
            text[id^=workaround] { fill: red; y: 100%; font-size: 15px;}
        "
        gantt:
            useWidth: 400
            rightPadding: 0
            topAxis: true  #false
            numberSectionStyles: 2
---
gantt
    title Timeline - Gantt Sampler
    dateFormat YYYY
    axisFormat %y
    %% this next line doesn't recognise 'decade' or 'year', but will silently ignore
    tickInterval 1decade

    section Issue19062
    71   :            item71, 1900, 1930
    section Issue19401
    36   :            item36, 1913, 1935
    section Issue1300
    94   :            item94, 1910, 1915
    5    :            item5,  1920, 1925
    0    : milestone, item0,  1918, 1s
    9    : vert,              1906, 1s   %% not yet official
    64   : workaround,        1923, 1s   %% custom CSS object https://github.com/mermaid-js/mermaid/issues/3250
```