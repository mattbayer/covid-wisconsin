---
layout: page
title: Dashboard - Regional
---

<head>
  <style>
    .plotly-graph-div.js-plotly-plot {height: inherit !important}
  </style>
</head>

<div style="max-width: 48rem; margin-left: -2rem; margin-right: -2rem">
  <div style="height:480px">   {% include_relative assets/plotly/Map-Region.html %}          </div>
  <div style="height:560px">   {% include_relative assets/plotly/Cases-Tests-Region.html %}  </div>
  <div style="height:560px">   {% include_relative assets/plotly/Deaths-Hosp-Region.html %}  </div>
</div>
