---
layout: post
title: "Covid WI status update: Nov 22"
hidden: true
---

### Hints of a peak
Dare I say it? There are signs that the case numbers have peaked.

In the past week, the 7-day average for the state first flattened out, then started to decline just the littlest bit. 

[State plot]

At the same time, the case positivity rate has also started to decline. This chart from the DHS is tricky because it shows positive/negative by date of test, rather than date reported like the one above, so the last two weeks of data is strictly preliminary. (More tests from those days can get reported later.) But my experience looking at this chart is that while the absolute numbers can change a lot, the positivity rate does not tend to change much as more data fills in. 

[DHS positivity plot]

If confirmed cases are flat or slightly down, and the test positivity rate is also down, then we can be pretty confident the true prevalance of the virus (the number of people who are really infected right now) is also going down.

This would be great news, though the trend is fresh and could easily change quickly. Keep in mind also that even if cases flatten or decline, it would be several more weeks before we would expect to see the deaths do the same.

This case trend is evident in most of the [state's regions](../dashboard-regional.md) as well. I don't see it yet in the Southeast or the Northwest, and the West and Madison are borderline.

[Regional plot]

### Estimates of total infected
By now, many Wisconsinites have been infected by the virus. Can we estimate just how many? 

Trevor Bedford, [made an estimate on Twitter](https://twitter.com/trvrb/status/1327437385395699713?s=20) based on using an assumed IFR, and reasoning backwards from the number recorded deaths to the number of cases. The number of deaths is much more reliable than the number of cases (though of course also subject to errors), and the IFR is known with some precision from a number of scientific studies. He used this reasoning to estimate the number of infections the country has for each confirmed case at 4 to 1, and then applied this multiplier to Wisconsin.

Nate Silver, of election site 538 fame, [made an estimate on Twitter](https://twitter.com/NateSilver538/status/1328057404722999300?s=20) based on a taking the detected cases and multiplying them by a factor that decreases with time.

Two more formal estimation projects are [covidestim](https://covidestim.org/us/WI) and Youyang Gu's [covid19-projections.com](https://covid19-projections.com/infections/us-wi), and [Oliver Wyman](https://pandemicnavigator.oliverwyman.com/forecast?mode=states&region=US_US-WI&panel=baseline), which is some kind of consulting company that runs a well-performing model.

Last, as to one untimely born, is my own estimate. Mine is simply adapting Dr. Bedford's reasoning, but adjusting it by estimating Wisconsin's specific infections-to-cases ratio, which turns out to be closer to 3-to-1. (REDO THIS)


Source | Date | % Infected
------ | ---- | ----------
Trevor Bedford | Nov 13 | 21%
Nate Silver | Nov 15 | 27%
covidestim | Nov 19 | 17%
Youyang Gu | Nov 6  | 22%
Oliver Wyman | Nov 19 | 10%
Matt Bayer | Nov 22 | 18% (???)
