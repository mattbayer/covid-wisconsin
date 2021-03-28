---
layout: post
title: "Covid WI status update: Mar&nbsp;28"
hidden: true
---

### Dammit
Cases are trending upwards again. DHS has been doing some data cleaning in the last several weeks, so there have been a couple bumps in reported cases over the last month that I didn't think had any larger significance. Over the last week, however, more indicators have lined up to show that there is a small increase going on. First, there is the test positivity rate:

![DHS test positivity]

Second, the cases by date of test are just perceptibly trending upwards. This plot is always incomplete for the most recent days, so as data fills in it the upward trend will become more clear.

![DHS cases]

### Don't freak out
I had really hoped we would not see another wave before this was truly over, so this is discouraging. I'm particularly concerned for 

On the other hand, our advantages over the virus have not gone away. We still have vaccination progressing well, a mass of people with natural immunity, and the oncoming summer season working in our favor. So I would expect this last wave to be small. 

Try this analogy. We're the Packers, up five points with two minutes left. (Say the virus is... the Seahawks.) There's no reason we shouldn't put this thing away. Unless...

![Onside kick](../assets/onsidekick.gif)

### What's the cause?
My best guess for the cause of the uptick is a combination of people somewhat lowering their personal precautions (laying no blame, I have done it too), and the more transmissible B.1.1.7 variant gaining a foothold.

First, if I pull an update of the Google mobility data, it does show that retail/recreation activity has increased substantially from a low in January. 

![Mobility data]

I'm focused on retail/recreation not to blame everything on those activities, but more as an index of how cautious people are being with their discretionary activities. Infections are way down, and vaccinations are up, so it's not surprising that people have eased up on precautions. But I'm guessing it is contributing to the uptick.

The second item is the B.1.1.7 variant, which experts expect to gradually spread through the country and increase virus transmission overall, in a race with vaccinations. I have been able to get some idea of where this stands in Wisconsin through something called the [GISAID database](https://www.gisaid.org/), which is a scientific effort that collects genetic sequences for coronavirus and flu submitted by labs and researchers all over the world. Genetic sequencing can differentiate B.1.1.7 samples from other coronavirus lineages. In Wisconsin, places like UW-Madison and the state laboratory are submitting their data to GISAID. If I download all the sequences from Wisconsin and chart what percentage are B.1.1.7 over time, I get the following plot.

![B.1.1.7 from GISAID]

It appears to take about a month after collection for sequences to show up in this database.

The B.1.1.7 variant is increasing in frequency, as would be predicted from having higher transmissibility. If we project this forward, it might make up 20%(?) of cases in Wisconsin right now. This is enough to start having an effect on our infection numbers, though obviously not enough to be dominant. As it becomes dominant, the overall virus transmissibility will gradually get higher in the state.



This assumes that the sequences in the database are representative of the state, which is a pretty big assumption. I have not been able to find much information about Wisconsin's sequencing effort and which samples get sequenced and submitted to this database. I might expect researchers to be preferentially sequencing samples they suspected of being B.1.1.7 - some PCR tests can imperfectly differentiate them, apparently - so this data might be biased high.

