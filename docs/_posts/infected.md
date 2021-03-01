---
layout: post
title: True infections
usemathjax: true
hidden: true
---

### Confirmed cases

These are basically a lower bound.

### Antibody testing
Another line of evidence is antibody testing, also called serosurveys. This tests a representative population for the presence of antibodies to the coronavirus. In theory the percent of people testing positive will be equal to the proportion of the population who has had the virus.

These studies, also called serosurveys, have been performed elsewhere but this is the only one I know of in Wisconsin. If they are properly randomized and representative, these studies can give an estimate of the proportion of people in the state that had ever been infected at the time of the study.

I know of two data sources on this type of testing for Wisconsin. The first is the [Survey of the Health of Wisconsin](https://show.wisc.edu/), a research effort at UW-Madison. They tested about a thousand people from July to mid-August, and again in the fall.

This is good data, but the results are implausibly low. To me the likeliest reason for this is that the design of the survey has selected people that are conscientious and trust medical science - the kind of people willing and able to participate in a multi-year research study. Might they also be more likely to be careful about the coronavirus, follow public health guidelines, and have the kinds of jobs and financial resources that allow them to social distance (and get to their research study appointments)?

The second data source is the CDC, which has been conducting a nationwide study on blood samples that were drawn for tests that were unrelated to Covid. In theory, these blood samples would then be randomized to the presence of Covid.

This data seems more likely, but I have reservations about it as well. These blood samples, though randomized for coronavirus, are of course selected for people getting clinical blood tests, which could bias the results in some way. In addition, the patterns by state do not quite make sense. Wisconsin certainly had a bad wave in the fall, but is its total infection rate really one of the worst in the United States? 

For example, New York is currently testing at 9% prevalence, while earlier in the summer it was testing near 20%. This is probably an example of antibodies fading over time. (Note that just because antibodies cannot be detected by this test does not mean that immunity is not longer present).

Possibly if antibody fading was accounted for, and considering also the relatively wide confidence intervals, all this data hangs together.

### Deaths
A simple approach to estimating the total number of cases is just to scale the number of deaths, which we assume is much more certain, according to the infection fatality ratio (IFR). This certainly gets you in the right ballpark. Its big uncertainty is the IFR. Credible estimates vary by a factor of 2 (say 0.5 - 1.0%). We also know that the IFR varies with the population, _especially_ with age. Finally, it is likely that IFR has decreased somewhat over time as Covid treatment has improved.


### Modeling from testing rates
