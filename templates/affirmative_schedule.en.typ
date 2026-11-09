// Essential setup: keep these opening lines.
// @immuknow-settings: settings.typ
#import "setup.typ": *
#show: immuknow.letter // Apply the letter layout
#assert(up_to_date, message: "This affirmative notice requires no overdue diseases.")

// Page 1: the letter. Each if/else below chooses wording for the client or their parent
// to_student and to_guardian identify the intended reader; the final else is neutral.
#immuknow.notice-page("Request for Immunization Record")[
#if date_of_delivery != "" [#align(right)[#date_of_delivery]]
#immuknow.client-block(window: envelope-window) // Mailing address and client details
#v(0.3cm) // Space before the message

As of *#date_as_of* our files show that #if to_student [you are] else if to_guardian [your child is] else [the named client is] up-to-date for #if to_student [your] else if to_guardian [their] else [the client's] immunization(s)! #if to_student [Your] else if to_guardian [Their] else [The client's] Immunization Record can be viewed on page 2.

For any future received vaccines, you can update #if to_student [your record] else if to_guardian [your child's record] else [the client's record] by using one of the following options:

1. By visiting #immuknow.link("https://example.org/immunization")
2. By emailing #immuknow.link("mailto:records@example.org")
3. By mailing a photocopy of #if to_student [your] else if to_guardian [your child's] else [the client's] immunization record to Cedar Ridge Health Unit, 123 Example Street, Demo City, ON N0N 0N0
4. By Phone: #immuknow.link("tel:1-800-555-0100")

Please update Public Health#if to_guardian [ and your childcare centre] every time #if to_student [you receive] else if to_guardian [your child receives] else [the client receives] a vaccine.

If you have any questions, please call #immuknow.link("tel:1-800-555-0100").

Thank you for helping to keep our children safe.

  Sincerely,

#immuknow.signature-block(
  signature: image("assets/signature.png", width: 4.5cm), // Change width; height follows the image’s aspect ratio.
  name: "Dr. Annie Body",
  title: "Associate Medical Officer of Health",
)

]

#immuknow.notice-page("Immunization Record")[
  For your reference, the immunization(s) on file with Public Health are as follows:

  #immuknow.immunization-history()
  #align(center)[End of immunization record]
]

// Privacy notice: edit wording and contact details here
#immuknow.privacy-notice[
  The information in this notice was collected under the authority of the _Health Protection and Promotion Act_ in accordance with the _Municipal Freedom of Information and Protection of Privacy Act_ and the _Personal Health Information Protection Act_. This information is used for the delivery of public health programs and services; the administration of the agency; and the maintenance of healthcare databases, registries and related research, in compliance with legal and regulatory requirements. Any questions about the management of this information should be addressed to the Chief Privacy Officer at #immuknow.link("tel:+18005550100;ext=1234")[1-800-555-0100 ext. 1234] or #immuknow.link("mailto:privacy@example.org").
]
