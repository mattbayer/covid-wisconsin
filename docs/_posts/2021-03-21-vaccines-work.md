---
layout: post
title: "The vaccines are working"
hidden: true
---

The high vaccination rate of those over 65 is now causing cases to decline faster in that age group. The vaccines are working.

Wisconsin's Covid cases peaked way back in November, due to (I believe) a combination of natural immunity and preventive behavior. Whatever the cause, it was far too early to be due to the Covid vaccines, which only began to be administered in December. I believe that the vaccines work, but is there any way to tell from the state's data? 

One way would be to compare two groups of people with different vaccination rates, and see if their case trajectories were significantly different. People over 65 provide a good test case, luckily for this blog (and for the people over 65).

In Wisconsin, vaccine eligibility was opened to anyone 65 and over starting on January 25. Before that, elibility was limited to healthcare workers and people in long-term care. (Although for Wisconsin, only nursing homes received the vaccine starting in late December, [assisted living only started administrations on January 25 as well](https://www.jsonline.com/story/news/2021/03/09/wisconsin-delayed-starting-assisted-living-covid-19-vaccine-program/4392335001/).) At the time of writing, [over 70% of seniors have received at least one dose](https://www.dhs.wisconsin.gov/covid-19/vaccine-data.htm), compared with 25% for all ages combined. Therefore, between January 25 and today, I would expect to see the Covid rates among seniors decrease faster than the rates among other age groups.

The best data to use for this is DHS's plot of weekly cases, by age group, by date of symptom onset or test result. Here is the full plot copied from the DHS website:

![DHS case rate by age](../assets/DHS-Cases-Age_2021-03-20.png)

Recently, the over-65 age group has had the lowest case rate, a fact that [the Milwaukee Journal Sentinel has linked to their high vaccination rate](https://www.jsonline.com/story/news/2021/03/19/wisconsin-residents-65-hold-lowest-level-covid-19-cases/4768868001/?utm_campaign=snd-autopilot&cid=twitter_journalsentinel). I don't think that fact alone shows much, however, beca7se this age group already7 had the second-lowest rate throughout most of the pandemic. And because the case rates for all age groups have been going down since November, it's difficult to pick out whether a particular age group has been going down faster than the others.

To be more sensitive to this kind of change, I used DHS's data and tried to normalize out the overall peaks and valleys of the pandemic. The details require some explanation,[^Plot] but the result is the plot below. It shows each age group's per-population weekly case rate, divided by an "average" case rate for everyone ages 25-65.  If an age group's value is at 1, then its case rate is equal to the average; if it is above or below, then it is higher or lower than the average. So what does it show? 

![Relative case rate by age group](../assets/CaseRateRelative-Age-Vaccine_2021-03-20.png)

It shows that the vaccines work - cases in the over-65 group have in fact decreased faster than other age groups in recent weeks. Moreover, this divergence starts after the week of February 7, two weeks after eligibility - which is telling, because the vaccine clinical trials indicated that their effectiveness begins [two weeks after the first dose].

- Older age groups have generally had lower case rates; 65+ has a lower rate (its line is lower on the plot) than 55-64, which is lower than 45-54, etc.
- The 18-24 group had a mini-surge in mid-February, which I would link to [college campuses](https://covid-wisconsin.com/2021/02/28/status-update/#a-blip-in-cases).
- The under-18 case rate, while low, has gradually increased relative to the other age groups since the fall. I could guess at several possible reasons for this, including school openings; higher availability of tests making it more common to test mild-symptom cases in kids; or buildup of natural immunity in the other age groups leading to a higher share of cases in this group.


---
[^Plot]: First I took each age group's rate of cases per 100,000 population, just as shown in the DHS plot. Then I compared those rates against the average case rate for the ages 25-64. I think these age groups represents a sort of baseline for the course of the pandemic, because their case rates tend to move up and down together. In contrast, the 18-24 group has a very different pattern due to college outbreaks, and the over-65 group is the one we want to study. The under-18 group is also interesting on its own, so I exclude it from the average as well.
