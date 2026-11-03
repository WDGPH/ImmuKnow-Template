// Essential setup: keep these opening lines.
// @immuknow-settings: settings.typ
#import "setup.typ": *
#show: immuknow.letter // Apply the letter layout

// Page 1: the letter. Each if/else below chooses wording for the client or their parent
// to_student and to_guardian identify the intended reader; the final else is neutral.
#immuknow.notice-page("Demande de dossier d'immunisation")[
#immuknow.client-block(window: envelope-window) // Mailing address and client details
#v(0.3cm) // Space before the message

#if not no_records [En date du *#date_as_of*, nos dossiers indiquent que #if to_student [vous n'avez] else if to_guardian [votre enfant n'a] else [la personne nommée n'a] pas reçu les immunisations suivantes :]

#strong(immuknow.overdue-agents(columns: 1))

Veuillez examiner le dossier d'immunisation à la page 2 et mettre à jour #if to_student [votre dossier] else if to_guardian [le dossier de votre enfant] else [le dossier de la personne nommée] en utilisant l'une des options suivantes :

1. En visitant #immuknow.link("https://example.org/immunization")
2. En envoyant un courriel à #immuknow.link("mailto:records@example.org")
3. En envoyant par la poste une photocopie #if to_student [de votre dossier d'immunisation] else if to_guardian [du dossier d'immunisation de votre enfant] else [du dossier d'immunisation de la personne nommée] à Cedar Ridge Health Unit, 123 Example Street, Demo City, ON N0N 0N0
4. Par téléphone : #immuknow.link("tel:1-800-555-0100")

Veuillez informer la Santé publique#if to_guardian [ et votre centre de garde d'enfants] chaque fois que #if to_student [vous recevez] else if to_guardian [votre enfant reçoit] else [la personne nommée reçoit] un vaccin.

#grid(
  columns: (1fr, auto),
  gutter: 10pt,
  [*Si vous choisissez de ne pas #if to_student [vous faire vacciner] else if to_guardian [immuniser votre enfant] else [immuniser la personne nommée]*, une exemption médicale valide ou une déclaration de conscience ou de croyance religieuse doit être remplie et soumise à la Santé publique. Les liens vers ces formulaires se trouvent à #immuknow.link("https://example.org/exemptions"). Veuillez noter que cette exemption est uniquement pour la garde d'enfants et qu'une nouvelle exemption sera requise lors de l'inscription à l'école primaire.],
  [#immuknow.qr-code(..qr)]
)

En cas d'éclosion, les enfants qui ne sont pas adéquatement immunisés peuvent être exclus du centre de garde d'enfants.

Si vous avez des questions sur #if to_student [vos vaccins] else if to_guardian [les vaccins de votre enfant] else [les vaccins de la personne nommée], veuillez appeler le #immuknow.link("tel:1-800-555-0100") pour parler à une infirmière de la Santé publique.

  Sincères salutations,

#immuknow.signature-block(
  signature: image("assets/signature.png", width: 4.5cm), // Change width; height follows the image’s aspect ratio.
  name: "Dr. Annie Body",
  title: "Médecin hygiéniste adjoint",
)

]

#immuknow.notice-page("Dossier d’immunisation")[
  Pour votre référence, les immunisations enregistrées auprès de la Santé publique sont les suivantes :

  #immuknow.immunization-history()
  #align(center)[Fin du dossier d'immunisation]
]

// Privacy notice: edit wording and contact details here
#immuknow.privacy-notice[
  Les renseignements figurant dans cet avis ont été recueillis en vertu de la _Loi sur la protection et la promotion de la santé_, conformément à la _Loi sur l’accès à l’information municipale et la protection de la vie privée_ et à la _Loi sur la protection des renseignements personnels sur la santé_. Ces renseignements servent à la prestation de programmes et de services de santé publique, à l’administration de l’organisme ainsi qu’à la tenue de bases de données et de registres de santé et aux recherches connexes, dans le respect des exigences légales et réglementaires. Toute question concernant la gestion de ces renseignements doit être adressée au responsable de la protection de la vie privée au #immuknow.link("tel:+18005550100;ext=1234")[1-800-555-0100, poste 1234], ou à #immuknow.link("mailto:privacy@example.org").
]
