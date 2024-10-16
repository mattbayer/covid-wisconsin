---
layout: dashboard
title: Dashboard
---

<div style="max-width: 48rem; margin-left: -2rem; margin-right: -2rem">
  {% include plotly/Pos-Positivity-WI.html %}
</div>

Source: WI DHS. ([Plot](https://bi.wisconsin.gov/t/DHS/views/PercentPositivebyTestPersonandaComparisonandTestCapacity/PercentPositivebyTestDashboard?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link) and [main page](https://www.dhs.wisconsin.gov/covid-19/data.htm).)

<div style="max-width: 48rem; margin-left: -2rem; margin-right: -2rem">
  {% include plotly/Map-CaseChange-WI.html %}
</div>

Blue inner circles show the current 7-day average for cases. Counties with a significant increasing trend show outer purple circles with size equal to the current cases plus the increase over the latest 14-day period. Counties with a significant decreasing trend show outer transparent circles with size equal to the case average from 14 days ago. Source: WI DHS [downloaded county data](https://data.dhsgis.wi.gov/datasets/wi-dhs::covid-19-historical-data-by-county-1/about).

<div style="max-width: 48rem; margin-left: -2rem; margin-right: -2rem">
  {% include plotly/Cases-Positivity-Region.html %}
</div>

Source: WI DHS [downloaded county data](https://data.dhsgis.wi.gov/datasets/wi-dhs::covid-19-historical-data-by-county-v2/about).

