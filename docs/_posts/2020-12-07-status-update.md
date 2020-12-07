---
layout: post
title: "Covid WI status update: Dec 7"
hidden: true
---

Wisconsin's case load is now declining, and now I think deaths have also peaked. The Thanksgiving weekend is making the data difficult to intepret, but I do not think there's any sign of a Thanksgiving surge.

### Past the peak
Two weeks ago I [wrote that Wisconsin's cases had peaked](../2020-11-22-status-update.md), and thankfully that has been confirmed by about a 1/3 decline in daily new cases since then. New hospitalizations have also declined. The trend is roughly similar in all regions of the state, although Milwaukee's decline is flatter than the rest. 

I believe the rate of reported deaths may be at its peak right now, based on fitting a delay and ratio of deaths to cases (case fatality rate or CFR) to the case curve. Since it takes a few weeks for a new case to progress to death, we expect the death curve to have a similar shape to the case curve, just delayed. And over the short term of a single wave, it's reasonable to assume a constant case fatality rate. (Even though over the long term it could change, for example from diagnosing more cases due to more testing availability.) 

![Cases and delayed deaths](../assets/Cases-Deaths-WI_2020-12-06.png)

I'm taking the idea for this comparison from [scientist Trevor Bedford](https://twitter.com/trvrb/status/1331780099490807808), who uses a CFR of 1.8% and delay of 22 days to model the United States as a whole. For Wisconsin, I found that a CFR of 1.0% and delay of 12 days seems to match the data better. This implies that Wisconsin is detecting a higher proportion of cases than the country as a whole, and that it has a shorter time period between reporting a case and reporting a death.

### Thanksgiving

You may object that the previous plot showed a huge dip in the deaths average right where I claim that it should be peaking. I think this dip is purely a result of delayed data reporting over Thanksgiving weekend. If not for the holiday, the 7-day average of deaths *would have* peaked this past week; instead, it will peak this coming week as the low-reporting days drop out of the average, and then decline.

This holiday delay is a problem that appears in all the tracking data right now. As another example, consider the positivity rate, the percent of tests that come back positive for the virus. The DHS plot for positivity of cases vs. new people tested shows a particularly strong discontinuity. The four days following Thanksgiving all have much lower numbers of test results, and much higher positivity, so that the 7-day average takes a strong turn upward starting at Thanksgiving. But on December 3, exactly 7 days after Thanksgiving, the 7-day average turns right back around and starts going down again.

![DHS positivity new people tested](../assets/Positivity-DHS_2020-12-06.jpg)

I think this is all an artifact of lower testing availability and possibly delayed reporting on the four days of Thanksgiving weekend. Since many testing locations were closed over the weekend, it's likely that the tests that did occur were more urgent and more likely positive than average. Once testing returns to its normal availability, the positivity rate returns to its previous trend.

A similar artifact appears in the 7-day average case plots. When a single day is an outlier, with unusually low case numbers, the 7-day average unsurprisingly dives downward on that day. It's easy to forget, however, that the 7-day average will then also shoot upward on the day that outlier is removed from the average, 7 days later. 

To illustrate, I marked two of these instances in the plot below. The pair on the right is the result of Thanksgiving - the Friday after had very low cases, decreasing the average and creating a mirror-image spike on December 4. That spike was only a quirk of the averaging method, not a sign of a Thanksgiving surge. The very same thing happened in October, when no cases were reported on October 17 due to DHS system maintenance, and the average spiked 7 days later on October 24.

![7-day average artifact](../assets/Cases-7day-artifact.jpg)

All these irregularities make it very difficult to tell if Thanksgiving itself has caused any kind of surge in the virus. Now that all the Thanksgiving weekend days have worked out of the averages, though, next week's trend should be reliable.

My intuition is actually that Thanksgiving will not have a large effect on the numbers. I would guess most families took a similar level of precaution about Thanksgiving to what they were taking in the rest of their lives. And can one day, even a celebratory get-together, really count so much compared to all the work, school, and socializing over weeks of regular life? But that's just a guess; to find out I'll watch the numbers next week.

