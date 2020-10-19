---
layout: post
title: "How many people have really been infected?"
usemathjax: true
---
The DHS did not put out any data updates this weekend, [because of compute system maintenance](https://www.jsonline.com/story/news/2020/10/17/heres-why-wisconsin-wont-report-new-coronavirus-numbers-weekend/3697080001/). (Seems like a bad time?) Let's use this time of mystery and uncertainty to address another unknown number, the true number of infections in the state.

It is well known by now that the number of cases, infections confirmed by a positive Covid test, do not capture all of the infections in the state. Some people may be asymptomatic, some people may be sick but not get a test for various reasons. Early on, one large study estimated that only about [1 in 10](https://www.statnews.com/2020/07/21/cdc-study-actual-covid-19-cases/) infections were actually being detected as confirmed cases. That study did not look at Wisconsin, however. It was also for a period of very limited testing; we are certainly catching more cases now.

So what is the current true number of infections in Wisconsin?

### TL;DR - just times two
Here's one way to get an estimate of the true number of new infections per day.

1. Take the 7-day average of new cases.
1. Multiply by 2.

That's it! 

I think this is a plausible estimate based on two approaches I will go on to explain. It only applies to current case numbers, however. Earlier in the pandemic, we had less testing and we were not catching as many infections.

### The medium way
The next method is to extrapolate from the number of deaths and an assumed infection fatality rate, or IFR. The big advantage of this approach is that the statistics on death are more certain than the statistics on cases. We probably catch most of the Covid deaths, while we probably only confirm half or less of the cases. The disadvantages of this approach are that IFR may change over time, due to varying age distributions of cases and improvements in treatment; and that deaths lag infections by weeks, so the information is not timely.

The plot below compares daily detected cases to infections extrapolated from deaths, assuming a 0.75% IFR and a 14-day lag between positive test and death. The data in these plots are dated to the date of tests and the date of death, not the date a case or death was first reported, which is usually a few days later.

[Cases and Death-IFR estimate]

### The hard way
The final alternative is to build a model of how detected cases and number of tests relate to the true number of infections. There are a number of professional and semi-professional attempts at this, but I am going to share one I came up with because it's my blog. Consider yourself on dilettante alert. I do really think my idea here strikes a good balance of simplicity and plausibility that I have not seen anywhere else; but then I also think all my kids are above average and that my college rock band had a shot at the big time.

Anyway, here's the formula.

$$
N_{inf} = N_{cases} \sqrt{\frac{N_{pop}}{N_{tests}}}
$$

To convert this from current infections to new infections, I need to divide by an average duration $$d$$, the length of time that an infected person would test positive. 

$$
N_{new} = \frac{N_{cases}}{d} \sqrt{\frac{N_{pop}}{N_{tests}}}
$$

If I plug in $$N_{pop}$$ for Wisconsin (5.8 million people), and use a $$d$$ estimate of 7 days, I get an approximate formula

$$
N_{new} = 340 \frac{N_{cases}}{\sqrt{N_{tests}}}
$$

With daily tests averaging 30,000 (?) right now, that comes out to $$N_{new} \approx 2 N_{cases}$$.

$$
N_{inf} = \frac{N_{cases}}{d \sqrt{N_{tests}/N_{pop}}}
$$

$$
p_{inf} = \sqrt{r \cdot p_{cases}}
$$

where $$p_inf$$ is the prevalence of infections, i.e. the proportion of people who have a current infection; r is the test positivity rate, the proportion of daily tests that come back positive; and $$p_cases$$ is the prevalence of cases, the proportion of people who tested positive that day. My reasoning for this formula has to do with looking at the testing process as a kind of biased sampling...but I'm going to put that off to the end of the post. Let's look at the results first. 

