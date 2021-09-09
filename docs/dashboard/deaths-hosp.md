---
layout: dashboard
title: Dashboard
---

<div style="max-width: 48rem; margin-left: -2rem; margin-right: -2rem">
  {% include plotly/Deaths-Cases-WI.html %}
</div>

Source: WI DHS [county-level data](https://www.dhs.wisconsin.gov/covid-19/county.htm) for cases and deaths with confirmed Covid. Probable cases and deaths are not included. Deaths are plotted by date of death, cases by date of symptom onset or date of test. Both will be underestimates in recent weeks because of reporting delays, but are more accurate than plotting by date of report for past data.

<div style="max-width: 48rem; margin-left: -2rem; margin-right: -2rem">
  {% include plotly/Hosp-Cases-WI.html %}
</div>

Source: [CDC hospitalizations](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/g62h-syeh) and [WI DHS cases](https://www.dhs.wisconsin.gov/covid-19/county.htm). CDC data is for previous day hospital admission with confirmed Covid.
