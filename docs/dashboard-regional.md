---
layout: page
title: Dashboard - Regional
---

<head>
  <style>
    .plotly-graph-div.js-plotly-plot {height: 550px !important}
  </style>
</head>

<div style="max-width: 48rem; margin-left: -2rem; margin-right: -2rem">
  {% include_relative assets/plotly/Map-Region.html %}
  {% include_relative assets/plotly/Cases-Tests-Region.html %}
  {% include_relative assets/plotly/Deaths-Hosp-Region.html %}
</div>
