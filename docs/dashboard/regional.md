---
layout: dashboard
title: Dashboard - Regional
---

<head>
  <style>
    .plotly-graph-div.js-plotly-plot {height: 550px !important}
  </style>
</head>

<div style="max-width: 48rem; margin-left: -2rem; margin-right: -2rem">
  {% include plotly/Cases-Tests-Region.html %}
  {% include plotly/Deaths-Hosp-Region.html %}
  {% include plotly/Map-Region.html %}
</div>
