# documents/management/commands/create_templates.py
from django.core.management.base import BaseCommand
from documents.models import LegalTemplate


class Command(BaseCommand):
    help = 'Create legal templates for document generation (idempotent - safe to run multiple times)'

    def handle(self, *args, **options):
        self.stdout.write('Creating legal templates...')
        
        templates = [
            # THREATENED ARREST TEMPLATES
            {
                'violation_type': 'threatened_arrest_public',
                'location_type': 'traditional_public_forum',
                'section_type': 'jurisdiction',
                'template_text': 'This Court has jurisdiction over this action pursuant to 28 U.S.C. §§ 1331 and 1343(a)(3), as this action arises under the Constitution and laws of the United States, specifically 42 U.S.C. § 1983. Venue is proper in this district under 28 U.S.C. § 1391(b)(2) because a substantial part of the events occurred in this judicial district.'
            },
            {
                'violation_type': 'threatened_arrest_public',
                'location_type': 'traditional_public_forum',
                'section_type': 'claims',
                'template_text': 'COUNT I - VIOLATION OF FIRST AMENDMENT RIGHTS (42 U.S.C. § 1983)\n\nDefendants violated Plaintiff\'s First Amendment rights by imposing a prior restraint on protected speech and newsgathering activities. The threat of arrest constitutes a prior restraint, which is presumptively unconstitutional. The location constitutes a traditional public forum where Plaintiff has clearly established rights to engage in protected speech and press activities.'
            },
            {
                'violation_type': 'threatened_arrest_public',
                'location_type': 'traditional_public_forum',
                'section_type': 'prayer',
                'template_text': 'WHEREFORE, Plaintiff respectfully requests that this Court:\n\na) Enter declaratory judgment that Defendants\' actions violated Plaintiff\'s First and Fourteenth Amendment rights;\nb) Award compensatory damages for violation of constitutional rights;\nc) Award punitive damages against individual Defendants;\nd) Award attorney\'s fees and costs pursuant to 42 U.S.C. § 1988;\ne) Grant such other relief as this Court deems just and proper.'
            },
            
            # RECORDING INTERFERENCE TEMPLATES
            {
                'violation_type': 'interference_recording',
                'location_type': 'traditional_public_forum',
                'section_type': 'jurisdiction',
                'template_text': 'This Court has jurisdiction over this action pursuant to 28 U.S.C. §§ 1331 and 1343(a)(3), as this action arises under the Constitution and laws of the United States, specifically 42 U.S.C. § 1983. Venue is proper in this district under 28 U.S.C. § 1391(b)(2) because the constitutional violations occurred within this judicial district.'
            },
            {
                'violation_type': 'interference_recording',
                'location_type': 'traditional_public_forum',
                'section_type': 'facts',
                'template_text': 'On {{incident_date}}, Plaintiff was lawfully present at {{incident_location}}, a traditional public forum, exercising the clearly established constitutional right to record public officials in the performance of their duties.\n\nDefendants interfered with Plaintiff\'s recording activities without legal justification, violating Plaintiff\'s clearly established First Amendment rights.\n\nThe right to record police and public officials in public spaces was clearly established at the time of Defendants\' conduct.'
            },
            {
                'violation_type': 'interference_recording',
                'location_type': 'traditional_public_forum',
                'section_type': 'claims',
                'template_text': 'COUNT I - VIOLATION OF FIRST AMENDMENT RIGHT TO RECORD (42 U.S.C. § 1983)\n\nDefendants violated Plaintiff\'s clearly established First Amendment right to record police officers and public officials performing their duties in public. The right to record public officials is protected by the First Amendment. See Glik v. Cunniffe, 655 F.3d 78 (1st Cir. 2011); Turner v. Driver, 848 F.3d 678 (5th Cir. 2017); Fields v. City of Philadelphia, 862 F.3d 353 (3d Cir. 2017).\n\nDefendants\' interference constituted a content-based restriction on protected speech in a traditional public forum, subject to strict scrutiny, which Defendants cannot satisfy.'
            },
            {
                'violation_type': 'interference_recording',
                'location_type': 'traditional_public_forum',
                'section_type': 'prayer',
                'template_text': 'WHEREFORE, Plaintiff respectfully requests that this Court:\n\na) Enter declaratory judgment that Defendants\' interference with Plaintiff\'s right to record violated the First and Fourteenth Amendments;\nb) Enter permanent injunctive relief prohibiting Defendants from interfering with the constitutional right to record in public spaces;\nc) Award compensatory damages for the violation of clearly established constitutional rights;\nd) Award punitive damages against individual Defendants for their deliberate indifference to constitutional rights;\ne) Award reasonable attorney\'s fees and costs pursuant to 42 U.S.C. § 1988;\nf) Grant such other relief as this Court deems just and proper.'
            },
            
            # FORCED REMOVAL TEMPLATES
            {
                'violation_type': 'forced_to_leave_public',
                'location_type': 'traditional_public_forum',
                'section_type': 'jurisdiction',
                'template_text': 'This Court has jurisdiction over this action pursuant to 28 U.S.C. §§ 1331 and 1343(a)(3), as this action arises under the Constitution and laws of the United States, specifically 42 U.S.C. § 1983. Venue is proper in this district under 28 U.S.C. § 1391(b)(2) because the unlawful exclusion occurred within this judicial district.'
            },
            {
                'violation_type': 'forced_to_leave_public',
                'location_type': 'traditional_public_forum',
                'section_type': 'facts',
                'template_text': 'On {{incident_date}}, Plaintiff was lawfully present at {{incident_location}}, a traditional public forum, engaging in constitutionally protected activities including speech, assembly, and newsgathering.\n\nWithout lawful justification, Defendants forced Plaintiff to leave the public area, thereby excluding Plaintiff from a traditional public forum based on the content and viewpoint of Plaintiff\'s protected activities.\n\nPlaintiff\'s activities were peaceful, lawful, and posed no threat to public safety or substantial interference with other lawful uses of the forum.'
            },
            {
                'violation_type': 'forced_to_leave_public',
                'location_type': 'traditional_public_forum',
                'section_type': 'claims',
                'template_text': 'COUNT I - EXCLUSION FROM PUBLIC FORUM (42 U.S.C. § 1983)\n\nDefendants violated Plaintiff\'s First Amendment rights by excluding Plaintiff from a traditional public forum without compelling justification. Traditional public forums are subject to the highest level of First Amendment protection, and content-based exclusions must survive strict scrutiny.\n\nDefendants\' exclusion was based on disapproval of Plaintiff\'s protected speech and press activities, constituting impermissible viewpoint discrimination.'
            },
            {
                'violation_type': 'forced_to_leave_public',
                'location_type': 'traditional_public_forum',
                'section_type': 'prayer',
                'template_text': 'WHEREFORE, Plaintiff respectfully requests that this Court:\n\na) Enter declaratory judgment that Defendants\' exclusion of Plaintiff from public property violated the First and Fourteenth Amendments;\nb) Enter permanent injunctive relief prohibiting Defendants from excluding individuals from public forums based on protected speech activities;\nc) Award compensatory damages including damages for the violation of constitutional rights and emotional distress;\nd) Award punitive damages against individual Defendants;\ne) Award reasonable attorney\'s fees and costs pursuant to 42 U.S.C. § 1988;\nf) Grant such other relief as this Court deems just and proper.'
            },
            
            # RETALIATION TEMPLATES
            {
                'violation_type': 'retaliation_protected_speech',
                'location_type': 'traditional_public_forum',
                'section_type': 'jurisdiction',
                'template_text': 'This Court has jurisdiction over this action pursuant to 28 U.S.C. §§ 1331 and 1343(a)(3), as this action arises under the Constitution and laws of the United States, specifically 42 U.S.C. § 1983. Venue is proper in this district under 28 U.S.C. § 1391(b)(2) because the retaliatory conduct occurred within this judicial district.'
            },
            {
                'violation_type': 'retaliation_protected_speech',
                'location_type': 'traditional_public_forum',
                'section_type': 'facts',
                'template_text': 'Plaintiff previously engaged in constitutionally protected speech and press activities. Subsequently, Defendants retaliated against Plaintiff because of these protected First Amendment activities.\n\nDefendants\' retaliatory conduct was taken in direct response to Plaintiff\'s exercise of constitutional rights and was intended to deter future protected activity.\n\nDefendants\' conduct would chill a person of ordinary firmness from continuing to engage in protected speech activities.'
            },
            {
                'violation_type': 'retaliation_protected_speech',
                'location_type': 'traditional_public_forum',
                'section_type': 'claims',
                'template_text': 'COUNT I - FIRST AMENDMENT RETALIATION (42 U.S.C. § 1983)\n\nDefendants violated Plaintiff\'s First Amendment rights by retaliating against Plaintiff for engaging in protected speech activities. To establish a First Amendment retaliation claim, Plaintiff must show: (1) constitutionally protected conduct, (2) retaliatory action that would deter a person of ordinary firmness from continuing the conduct, and (3) a causal connection between the protected conduct and the retaliatory action.\n\nPlaintiff\'s speech and press activities were constitutionally protected. Defendants\' retaliatory actions would deter a person of ordinary firmness from continuing such activities. The temporal proximity and circumstances establish the causal connection.'
            },
            {
                'violation_type': 'retaliation_protected_speech',
                'location_type': 'traditional_public_forum',
                'section_type': 'prayer',
                'template_text': 'WHEREFORE, Plaintiff respectfully requests that this Court:\n\na) Enter declaratory judgment that Defendants\' retaliation for protected speech violated the First Amendment;\nb) Enter permanent injunctive relief prohibiting Defendants from retaliating against individuals for engaging in protected speech activities;\nc) Award compensatory damages for the violation of constitutional rights and resulting harm;\nd) Award punitive damages against individual Defendants for their deliberate indifference to clearly established rights;\ne) Award reasonable attorney\'s fees and costs pursuant to 42 U.S.C. § 1988;\nf) Grant such other relief as this Court deems just and proper.'
            },
            
            # DESIGNATED PUBLIC FORUM VARIANTS
            {
                'violation_type': 'interference_recording',
                'location_type': 'designated_public_forum',
                'section_type': 'claims',
                'template_text': 'COUNT I - VIOLATION OF FIRST AMENDMENT RIGHT TO RECORD (42 U.S.C. § 1983)\n\nDefendants violated Plaintiff\'s clearly established First Amendment right to record in a designated public forum. The government has opened this location for public access and speech activities, creating a designated public forum subject to First Amendment protection.\n\nAny restrictions on recording in designated public forums must be content-neutral and narrowly tailored to serve significant governmental interests. Defendants\' interference was content-based and not narrowly tailored.'
            },
            {
                'violation_type': 'forced_to_leave_public',
                'location_type': 'designated_public_forum',
                'section_type': 'claims',
                'template_text': 'COUNT I - EXCLUSION FROM DESIGNATED PUBLIC FORUM (42 U.S.C. § 1983)\n\nDefendants violated Plaintiff\'s First Amendment rights by excluding Plaintiff from a designated public forum. The government has opened this location for public access and use, creating a designated public forum entitled to significant First Amendment protection.\n\nExclusions from designated public forums must be reasonable and viewpoint-neutral. Defendants\' exclusion was based on hostility toward Plaintiff\'s protected activities and constituted impermissible viewpoint discrimination.'
            }
        ]
        
        created_count = 0
        existing_count = 0
        
        # Create templates using get_or_create to avoid duplicates
        for template_data in templates:
            template, created = LegalTemplate.objects.get_or_create(
                violation_type=template_data['violation_type'],
                location_type=template_data['location_type'],
                section_type=template_data['section_type'],
                defaults={'template_text': template_data['template_text']}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created: {template_data["section_type"]} for '
                        f'{template_data["violation_type"]} in {template_data["location_type"]}'
                    )
                )
            else:
                existing_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Template creation complete! '
                f'Created: {created_count}, Already existed: {existing_count}'
            )
        )