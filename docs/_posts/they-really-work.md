---
layout: post
title: Vaccines still work (continued)
hidden: true
---

DHS has begun releasing data on the rates of cases, hospitalizations, and deaths in fully-vaccinated and not-fully-vaccinated people. This gives us the most direct look yet at how the vaccines are working in the real world, and against Delta.

DHS's headline numbers are that in the past month, an unvaccinated person has been 11 times as likely to die, 9 times as likely to be hospitalized, and 4 times as likely to have a confirmed case. These are "age-adjusted" numbers. What does that mean, and what 

### Adjusting for group size
For the purposes of judging the effectiveness of the vaccine, it is not a good idea to just compare raw numbers of X deaths among the vaccinated to Y among the unvaccinated. This is because the size of the groups can be very different. Let's take the example of deaths among those over 65 in August. Here is a bar graph of the raw numbers of deaths in the vaccinated and unvaccinated groups.

![65+ raw deaths](../assets/VaxBarAge-DeathRaw-65.png)

This looks like the vaccine only reduces the risk of death by half. Now that's better than a sharp stick in the eye, but would be much worse than we've been promised. Luckily, this is not the right way to think about it at all - in fact DHS doesn't even display this data directly for that reason. It overlooks that nearly 90% of those over 65 are vaccinated, so these 48 vaccinated deaths are coming from a much larger group than the 88 not-fully-vaccinated deaths.

So here's another plot to visualize the issue better. Here the height of the bar indicates the rate of deaths per 100,000 people in each of the vaccinated or unvaccinated groups. The width of the bar is proportional to the population of the group. That means the total area of each bar is proportional to the raw number of deaths, but the height more accurately shows the risk reduction from vaccination. For this age group, this per-capita rate of deaths among the unvaccinated were 9 times higher than in the vaccinated.

![65+ death rates](../assets/VaxBarAge-Death-65.png)


### Adjusting for age
Okay, so now we now to always use per-capita numbers. Let's look at deaths again (per-capita, of course) for the whole population.

![Deaths whole population](../assets/VaxBarAge-Death-Total.png)

Now this is confusing again - the risk reduction here only appears to be a factor of 3. But that's much lower than we just saw for the over-65, which we know is the group most at risk of death. How does this make sense?

We have to realize that when compare all vaccinated against all unvaccinated people, we are comparing two groups that differ in *two* ways that we know strongly affect the death rate: vaccination status, obviously, but also *age*. In Wisconsin over 80% of people over 65 are fully vaccinated, while zero people under 12 are. The age makeup of each group is very different:

![Pie charts](../assets/VaxAgeMakeupPies.png)

So you can't make the comparison across vaccination status and draw a conclusion without accounting for age. To see this more easily, let's imagine a simpler, more extreme situation. Imagine that our entire population was half kids under 12, who are entirely unvaccinated but still vanishingly unlikely to die; and half retirees over 65, who are 100% vaccinated but still have some likelihood of dying (albeit much reduced, say by 90%). In this population 100% of Covid deaths would still occur among the vaccinated, and 0% among the unvaccinated. But that would not be because the vaccines were ineffective - it would be because the elderly were *both* more likely to be vaccinated, *and still* more likely to die of Covid.

The real situation in our state, which mirrors the rest of the country, is not so extreme, but it has the same kind of pattern. To get an accurate picture of vaccine effectiveness, we *have to* separate out data by age group, or adjust for age in some way. 

Below are three plots that do that, using DHS's August data for deaths, hospitalizations, and cases. They are similar to the second plot above in that the height of each bar shows the rate of the outcome per 100k people, showing the risk for that vax and age group, and the width indicates the population of that group. The tall narrow bar for unvaxed deaths over 65 means the group is small and the risk is high; the wide short/nonexistent bar for deaths under 12 means the group is large but the risk is small.

![Deaths age stratified](../assets/VaxBarAge-Death-StratAge.png)

![Hospitalizations age stratified]

![Cases age stratified]

Deaths and hospitalizations have very heavy skews towards older people, so it is very important to separate out the results by age group. Results for cases are more uniform.

### Age-adjusted numbers
It also allows us to compare the observed vaccine efficacy with the numbers from the clinical studies .

Outcome | Risk Vax/Unvax (age-adjusted) | Vaccine efficacy (observed)
---------- | ----------- | -----------
Cases | 4x | 75%
Hospitalizations | 9x | 89%
Deaths | 11x | 91%


---




What does it mean when these numbers get adjusted for age? 



Luckily the DHS is also now breaking out these numbers by age, and then compiling these age-stratified numbers into an "age-adjusted" number. This age-adjusted number is meant to convey the reduction in risk more accurately. 

To put it another way, I could note that the average vaccinated person is 1/3 as likely to die from Covid as an average unvaccinated person. But the average age of an average vaccinated person is XX years old, while the average of an unvaccinated person is YY years old.  If I'm making a decision about whether to get vaccinated, what I really want to know is how much it reduces the risk for me, a person with a definite certain age which is not going to change when I get the shot. That risk reduction is what the age-adjusted number is trying to estimate.


### Adjusting for natural immunity
Another confounding factor in these numbers is that some proportion of the not-fully-vaccinated bucket are partially vaccinated, and some have natural immunity from a previous infection. These individuals also have some level of risk reduction to the virus, and averaging them in with the fully non-immune gives that group a somewhat lower infection rate overall, and appears to reduce the vaccine effectiveness.

I can make a crude adjustment for this effect.





*They really really really really really really work*
