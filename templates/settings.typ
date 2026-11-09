#import "lib/immuknow/lib.typ" as immuknow
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
#let title-align = center // left, center or right within the heading area

// QR destination is resolved in Typst and shared by the code and its clickable link
#let qr = (
  enabled: true,
  url: notice => immuknow.query-url("https://example.org/update", (
    client_id: notice.client_id,
    dob: notice.client_data.date_of_birth_iso,
    lang: notice.language,
  )),
  width: 3cm,
  foreground: accent-color,
  background: white,
  corner-foreground: auto, // The three large finder targets inherit foreground
  alignment-foreground: auto, // Smaller alignment targets inherit foreground
  module-shape: "square", // Or "dots", "rounded", "separated"
  corner-style: "square",
)
// #let qr = (..qr, enabled: false)
// #let qr = (..qr, url: "https://example.org/immunization") // One destination for everyone

// Notice data and supporting imports.
#let notice = json(sys.inputs.at("data"))
#let template-filename = sys.inputs.at("notice-template")
#assert(template-filename == notice.template, message: "Selected template identity differs from the facts")
#immuknow.check-notice(
  notice,
  version: sys.inputs.at("notice-version"),
  language: sys.inputs.at("notice-language"),
)
#let flags = immuknow.notice-flags(notice)
#let to_student = flags.to_student
#let to_guardian = flags.to_guardian
#let no_records = flags.no_records
#let up_to_date = flags.up_to_date
#let logo = image("assets/logo.png", width: logo-width)
#let dates = immuknow.notice-dates(notice)
#let date_of_delivery = dates.date_of_delivery
#let date_as_of = dates.date_as_of
#let date_due = dates.date_due
#let date_of_suspension = dates.date_of_suspension
#let date_of_birth = dates.date_of_birth

#let letter = immuknow.letter.with(
  notice: notice,
  language: notice.language,
  paper: paper-size,
  margins: page-margins,
  font: body-font,
  font-size: body-size,
  link-color: link-color,
)

// Shared page defaults; named options in the Template change only that page
#let notice-page = immuknow.notice-section.with(
  logo: logo,
  logo-width: logo-width,
  title-size: title-size,
  title-align: title-align,
  fill: heading-color,
  heading-above: 0.2cm,
  heading-below: 0.5cm,
)

// Shared history defaults; e.g. #immuknow.immunization-history(show-age: true) changes one table
#let immunization-history = immuknow.immunization-history.with(
  notice,
  diseases: ("Diphtheria", "Tetanus", "Pertussis", "Polio", "Hib", "Pneumococcal",
    "Rotavirus", "Measles", "Mumps", "Rubella", "Meningococcal", "Varicella"),
  ignore-agents: ("RSVAb", "VarIg", "HBIg", "RabIg", "Ig"), // Vaccines left out of the table
  include-other: true, // Include a column for other vaccines
  show-validity: true, // Show which doses count toward requirements
  legend-labels: (:), // Override valid, invalid, or unspecified text for this language
  omit-invalid: false, // Exclude invalid doses from the history
  show-age: false, // Add age in years and months after the vaccination date
  min-rows: 5, // Minimum number of vaccination rows
  font-size: if notice.language == "fr" { 10.6pt } else { 11pt },
  heading-size: auto, // Same size as chart text; use e.g. 11pt to override
  indicator-font: "FreeSerif", // Contains the dot and circle markers; avoids ambient font fallback
  indicator-size: auto, // Same size as chart text
  indicator-offset: (x: 0pt, y: 0pt), // Optical adjustment for your typeface
  labels: presentation.selected-labels(),
)

// These helpers always use this letter’s client data.
#let client-block = immuknow.client-block.with(
  notice,
  show-client-id: true, // Set false to hide the assignment identifier
  show-oiid: false, // Optional Ontario Immunization ID from the CSV
  missing-oiid: none, // none: omit; "": blank value; auto: bilingual unavailable text; or custom text
  id-label: auto, oiid-label: auto, // Bilingual defaults or your own plain-text labels
)
#let address-block = immuknow.address-block.with(notice)
#let overdue-diseases = immuknow.overdue-diseases.with(notice, labels: presentation.selected-labels(), no-records: auto, ispa-only: false)
#let overdue-agents = immuknow.overdue-agents.with(notice, no-records: auto)
#let notice-flags = immuknow.notice-flags.with(notice)
#let qr-code = immuknow.qr-code.with(notice)
#let notice-dates = immuknow.notice-dates.with(notice)
#let check-notice = immuknow.check-notice.with(notice)
