// Authored project labels may be edited independently of normalized disease names.
// Literal paths keep every translation dependency explicit for project export.
#let selected-labels() = (
  en_diseases_chart: json("translations/en_diseases_chart.json"),
  en_diseases_overdue: json("translations/en_diseases_overdue.json"),
  fr_diseases_chart: json("translations/fr_diseases_chart.json"),
  fr_diseases_overdue: json("translations/fr_diseases_overdue.json"),
)
