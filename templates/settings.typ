#import "lib/immuknow/lib.typ" as core
#import "presentation.typ" as presentation
#import "lib/immuknow/lib.typ": notice-header, notice-section, signature-block, privacy-notice, envelope-preset, long-date, localization, url-encode, query-url, link

// Page and envelope
// Paper: keep one choice uncommented
#let paper-size = "us-letter" // Letter · 8.5 × 11 in
// #let paper-size = "us-legal" // Legal · 8.5 × 14 in
// #let paper-size = "a4" // A4 · 210 × 297 mm

#let page-margins = (top: 1cm, bottom: 2cm, left: 1.75cm, right: 2cm) // Space between the page edges and the letter
// #10 envelope: 9.5 × 4.125 in; window: 4.5 × 1.125 in, 0.875 in from left and 0.5 in from bottom.
// Compact address position; adjust y and the fold position to suit your envelope/stuffer.
// Address window: x is the distance from the left; y is the distance from the top.
#let envelope-window = (x: 63pt, y: 120pt, width: 324pt, height: 81pt, padding: 11pt) // Window position, size, and space around the address
// Other sample windows: uncomment one in place of the line above.
// #let envelope-window = (x: 1.75cm, y: 165.1pt, width: 100mm, height: 45mm, padding: 11pt) // DL
// #let envelope-window = (x: 1.75cm, y: 165.1pt, width: 90mm, height: 45mm, padding: 11pt) // C5

#let logo-width = 7cm // Logo width

// Theme
// Match your organization’s fonts and colours. Colour values can be copied from your brand guide
#let body-font = "FreeSans" // Letter typeface
#let body-size = 10pt // Letter text size
#let heading-color = black // Colour of the letter and history headings
#let link-color = rgb("#0000ee") // Colour of website and email links
#let accent-color = rgb("#005568") // Default colour of the QR code
#let title-size = 20pt // Size of the letter and history headings

// QR destination is resolved in Typst and shared by the code and its clickable link
#let qr = (
  enabled: true,
  url: notice => core.query-url("https://example.org/update", (
    client_id: notice.client_id,
    dob: notice.client_data.date_of_birth_iso,
    lang: notice.language,
  )),
  width: 3cm,
  foreground: accent-color,
  background: white,
  module-shape: "square",
  corner-style: "square",
)
// #let qr = (..qr, enabled: false)
// #let qr = (..qr, url: "https://example.org/immunization") // One destination for everyone

// Notice data and supporting imports.
#let notice = json(sys.inputs.at("data"))
#let template-filename = sys.inputs.at("notice-template")
#assert(template-filename == notice.template, message: "Selected template identity differs from the facts")
#core.check-notice(
  notice,
  version: sys.inputs.at("notice-version"),
  language: sys.inputs.at("notice-language"),
)
#let over_16 = notice.client_data.over_16
#let logo = image("assets/logo.png", width: logo-width)
#let dates = core.notice-dates(notice)
#let date_of_delivery = dates.date_of_delivery
#let date_as_of = dates.date_as_of
#let date_of_birth = dates.date_of_birth

#let letter = core.letter.with(
  notice: notice,
  language: notice.language,
  paper: paper-size,
  margins: page-margins,
  font: body-font,
  font-size: body-size,
  link-color: link-color,
)

// Shared page defaults; named options in the Template change only that page
#let notice-page = core.notice-section.with(
  logo: logo,
  logo-width: logo-width,
  title-size: title-size,
  fill: heading-color,
  heading-above: 0.2cm,
  heading-below: 0.5cm,
)

// Shared history defaults; e.g. #immuknow.immunization-history(show-age: true) changes one table
#let immunization-history = core.immunization-history.with(
  notice,
  diseases: ("Diphtheria", "Tetanus", "Pertussis", "Polio", "Hib", "Pneumococcal",
    "Rotavirus", "Measles", "Mumps", "Rubella", "Meningococcal", "Varicella"),
  ignore-agents: ("RSVAb", "VarIg", "HBIg", "RabIg", "Ig"), // Vaccines left out of the table
  include-other: true, // Include a column for other vaccines
  show-validity: false, // Show which doses count toward requirements
  omit-invalid: false, // Exclude invalid doses from the history
  show-age: false, // Add age in years and months after the vaccination date
  min-rows: 5, // Minimum number of vaccination rows
  font-size: if notice.language == "fr" { 10.6pt } else { 11pt },
  heading-size: auto, // Same size as chart text; use e.g. 11pt to override
  indicator-font: "FreeSans", // Consistent dots across letter typefaces
  indicator-size: auto, // Same size as chart text
  indicator-offset: (x: 0pt, y: 0pt), // Optical adjustment for your typeface
  labels: presentation.selected-labels(),
)

// These helpers always use this letter’s client data.
#let client-block = core.client-block.with(notice)
#let address-block = core.address-block.with(notice)
#let overdue-diseases = core.overdue-diseases.with(notice, labels: presentation.selected-labels())
#let overdue-agents = core.overdue-agents.with(notice)
#let qr-code = core.qr-code.with(notice)
#let notice-dates = core.notice-dates.with(notice)
#let check-notice = core.check-notice.with(notice)
