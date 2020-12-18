---
layout: post
title: "Covid WI status update: Dec 21"
hidden: true
---

Cases and now deaths are declining in Wisconsin. Thanksgiving was not able to reverse this trajectory, although I think the data shows it did lead to a small increase in infections.

### Deaths and cases
Two weeks ago I predicted that [deaths had peaked](2020-12-7-status-update.md), and the intervening two weeks have confirmed it. Here is an update of the plot overlapping Wisconsin's case and death curves, showing how they follow very similar trajectories. Reported cases peaked in mid-November, and reported deaths peaked two weeks later, if you ignore the divot caused by delayed reporting over Thanksgiving weekend.

### Thanksgiving surge?
The Thanksgiving weekend caused multiple overlapping discontinuities delays in the tracking data, which makes it difficult to tell if the holiday caused any kind of surge in infections. First there were fewer tests than usual over the holiday; for tests that occurred before Thanksgiving, results probably took a bit longer than usual; and then the reporting of those results through the DHS system was certainly delayed. 

These effects create a small dip and spike in the case curve and the positivity rate that I think are primarly due these changes in reporting and testing, not spread of the virus. And in any case, the overall trend downward has now resumed, so we can conclude at least that Thanksgiving did not reverse the state's trend.

However! This does not preclude the possibility of a small effect for Thanksgiving, and I think I can cut through some of these data issues. [Milwaukee County's dashboard](https://www.arcgis.com/apps/opsdashboard/index.html#/018eedbe075046779b8062b5fe1055bf) displays cases and tests *by test date*, which means I do not have to worry about these delays between test and result, result and report. (I am sure DHS has this data as well, but it's not part of what they make available. Come on DHS, do me this favor...) I collected this data[^Brag] and looked at the last several weeks, starting November 1.

[Tests and Cases Milwaukee]

The case peak, measured by test date, occurred the second week in November. The peak in tests, interestingly, occurred the following week, while cases fell. Possibly this is because all the close contacts of the past week's positives were seeking testing; possibly it indicates that people were trying to get tested as a precaution before Thanksgiving week.

So Thanksgiving week happened in the middle of a downslope. If nothing had changed with testing, we could expect Thanksgiving week to have fewer cases than the week before, and the week after to have fewer cases yet. If a person contracted the virus around Thanksgiving, they would start showing symptoms a few days later and probably seek testing the week after the holiday.

But of course testing did change. Thanksgiving Day itself had very few tests and cases, and the following Friday was also lower than I would normally expect. Fewer tests will tend to make cases go down, and the positivity rate go up.



People took a little more risk over the Thanksgiving holiday, and we got a little more virus. Because the increase in activity was probably temporary, it did not change the overall trend.


---
[^Brag]: Milwaukee County doesn't make it available for download, but I was able to write a script to scrape it from the html of the dashboard web site.
