# documents/management/commands/seed_data.py
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from documents.models import LawsuitDocument, DocumentSection, LegalTemplate
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with sample lawsuit documents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of users to create (default: 5)'
        )
        parser.add_argument(
            '--documents',
            type=int,
            default=15,
            help='Number of lawsuit documents to create (default: 15)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            DocumentSection.objects.all().delete()
            LawsuitDocument.objects.all().delete()
            LegalTemplate.objects.all().delete()
            from accounts.models import UserProfile
            UserProfile.objects.all().delete()
            User.objects.all().delete()

        # Create users
        users_count = options['users']
        documents_count = options['documents']
        
        self.stdout.write(f'Creating {users_count} users...')
        users = self.create_users(users_count)
        
        self.stdout.write(f'Creating {documents_count} lawsuit documents...')
        documents = self.create_lawsuit_documents(users, documents_count)
        
        self.stdout.write(f'Creating document sections...')
        self.create_document_sections(documents)
        
        self.stdout.write('Creating legal templates...')
        self.create_legal_templates()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with {users_count} users, '
                f'{documents_count} documents, and legal templates!'
            )
        )

    def create_users(self, count):
        users = []
        
        # Create the two specific users first
        specific_users = [
            {
                'username': 'driver',
                'email': 's.chesnowitz@gmail.com',
                'first_name': 'Stephen',
                'last_name': 'Chesnowitz',
                'password': 'Test1234!',
                'is_admin': True,
                'profile_data': {
                    'full_legal_name': 'Stephen Chesnowitz',
                    'street_address': '232 Alfred Station Rd',
                    'city': 'Alfred Station',
                    'state': 'NY',
                    'zip_code': '14803',
                    'phone_number': '7162380814'
                }
            },
            {
                'username': 'johnfilax',
                'email': 'johnfilax@gmail.com',
                'first_name': 'John',
                'last_name': 'Filax',
                'password': 'Test1234!',
                'is_admin': False,
                'profile_data': {
                    'full_legal_name': 'John Filax',
                    'street_address': '123 Main St',
                    'city': 'Anywhere',
                    'state': 'FL',
                    'zip_code': '62701',
                    'phone_number': '4405253893'
                }
            }
        ]
        
        # Import UserProfile
        from accounts.models import UserProfile
        
        # Create specific users
        for user_data in specific_users:
            user, user_created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            
            user.set_password(user_data['password'])
            
            if user_data['is_admin']:
                user.is_staff = True
                user.is_superuser = True
            
            user.save()
            
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_legal_name': user_data['profile_data']['full_legal_name'],
                    'street_address': user_data['profile_data']['street_address'],
                    'city': user_data['profile_data']['city'],
                    'state': user_data['profile_data']['state'],
                    'zip_code': user_data['profile_data']['zip_code'],
                    'phone_number': user_data['profile_data']['phone_number']
                }
            )
            
            users.append(user)
            admin_status = " (ADMIN)" if user_data['is_admin'] else ""
            if user_created:
                self.stdout.write(f'Created specific user: {user.email}{admin_status}')
            else:
                self.stdout.write(f'User already exists: {user.email}{admin_status}')
        
        # Create additional fake users
        remaining_count = max(0, count - len(specific_users))
        for i in range(remaining_count):
            email = fake.email()
            while User.objects.filter(email=email).exists():
                email = fake.email()
                
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='testpassword123'
            )
            
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_legal_name': f"{user.first_name} {user.last_name}",
                    'street_address': fake.street_address(),
                    'city': fake.city(),
                    'state': fake.state_abbr(),
                    'zip_code': fake.zipcode(),
                    'phone_number': fake.phone_number()
                }
            )
            
            users.append(user)
            
        return users

    def create_lawsuit_documents(self, users, count):
        # Enhanced violation scenarios for different violation types
        violation_scenarios = [
            {
                'title': 'Recording Interference at Government Building',
                'description': 'Security guard blocked my camera while I was filming in the public lobby of city hall. Officer told me to turn off camera and put it away.',
                'location': 'City Hall lobby, {city}',
                'defendants': 'Security Guard John Smith, Officer Jane Doe (Badge #5678), City of {city}',
            },
            {
                'title': 'Threatened Arrest for Photography',
                'description': 'Police officer threatened to arrest me if I continued taking pictures on the public sidewalk outside the courthouse.',
                'location': 'Public sidewalk outside courthouse, {city}',
                'defendants': 'Officer Mike Johnson (Badge #1234), City of {city}',
            },
            {
                'title': 'Forced Removal from Public Area',
                'description': 'Security escorted me out of the DMV waiting area while I was lawfully waiting for service and observing.',
                'location': 'DMV waiting area, {city}',
                'defendants': 'Security Supervisor Lisa Brown, DMV Manager Robert Wilson',
            },
            {
                'title': 'Retaliation for Previous Complaint',
                'description': 'Officer harassed me at the courthouse because I had filed a complaint about him the previous week. He targeted me for retaliation.',
                'location': 'Courthouse steps, {city}',
                'defendants': 'Officer Tom Anderson (Badge #9876), {county} County Sheriff Department',
            },
            {
                'title': 'Interference with Recording Police Activity',
                'description': 'Officers blocked my view and interfered with my recording while I was filming a traffic stop from the public sidewalk.',
                'location': 'Public sidewalk, Main Street, {city}',
                'defendants': 'Officer Sarah Davis (Badge #4567), Officer Carol White (Badge #8901), City of {city}',
            },
            {
                'title': 'Kicked Out of Public Meeting',
                'description': 'Security forced me to leave the public town hall meeting because I was recording the proceedings.',
                'location': 'Town Hall meeting room, {city}',
                'defendants': 'Security Chief Mark Thompson, City Manager David Lee, City of {city}',
            }
        ]

        youtube_urls = [
            'https://youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtube.com/watch?v=J---aiyznGQ',
            'https://youtube.com/watch?v=y6120QOlsfU',
            'https://youtube.com/watch?v=oHg5SJYRHA0',
            '',  # Some documents won't have YouTube evidence
            '',
        ]

        documents = []
        for i in range(count):
            scenario = random.choice(violation_scenarios)
            user = random.choice(users)
            
            # Generate realistic data
            city = fake.city()
            address = fake.address().replace('\n', ', ')
            county = fake.city()
            
            # Format scenario data
            title = scenario['title']
            description = scenario['description']
            location = scenario['location'].format(city=city)
            defendants = scenario['defendants'].format(city=city, county=county)
            
            document = LawsuitDocument.objects.create(
                user=user,
                title=title,
                description=description,
                incident_date=fake.date_between(start_date='-2y', end_date='today'),
                incident_location=location,
                defendants=defendants,
                youtube_url_1=random.choice(youtube_urls),
                youtube_url_2=random.choice(youtube_urls) if random.choice([True, False]) else '',
                youtube_url_3=random.choice(youtube_urls) if random.choice([True, False, False]) else '',
                youtube_url_4=random.choice(youtube_urls) if random.choice([True, False, False, False]) else '',
                additional_evidence=fake.paragraph(nb_sentences=3) if random.choice([True, False]) else '',
                status=random.choice(['draft', 'in_progress', 'completed', 'filed']),
            )
            documents.append(document)
        
        return documents

    def create_document_sections(self, documents):
        section_content_templates = {
            'introduction': [
                'Plaintiff brings this civil rights action seeking damages and injunctive relief for violations of constitutional rights under 42 U.S.C. § 1983.',
                'This action arises from defendants\' deliberate indifference to plaintiff\'s constitutional rights and seeks redress for civil rights violations.',
                'Plaintiff seeks monetary damages and declaratory relief for violations of rights guaranteed under the Constitution and federal civil rights laws.'
            ],
            'jurisdiction': [
                'This Court has jurisdiction over this action pursuant to 28 U.S.C. §§ 1331 and 1343, as this action arises under the Constitution and laws of the United States.',
                'Venue is proper in this district under 28 U.S.C. § 1391(b) as the events giving rise to this action occurred within this judicial district.',
                'This Court has supplemental jurisdiction over state law claims under 28 U.S.C. § 1367.'
            ],
            'parties': [
                'Plaintiff is a citizen of this state and was at all relevant times exercising constitutional rights.',
                'Defendants are individuals acting under color of state law and/or governmental entities responsible for the violations alleged herein.',
                'At all times relevant, defendants were acting within the scope of their official duties and under color of state law.'
            ],
            'facts': [
                'On the date in question, plaintiff was lawfully present and engaging in constitutionally protected activity.',
                'Defendants\' actions were unreasonable, excessive, and violated clearly established constitutional rights.',
                'As a direct and proximate result of defendants\' actions, plaintiff suffered damages including physical injury, emotional distress, and violation of civil rights.',
                'Defendants acted with deliberate indifference to plaintiff\'s constitutional rights and failed to follow established procedures.'
            ],
            'claims': [
                'Defendants violated plaintiff\'s rights under the Fourth Amendment to the Constitution by using excessive force.',
                'Defendants violated plaintiff\'s rights under the Fourteenth Amendment by denying equal protection under the law.',
                'Defendants\' actions constitute a violation of 42 U.S.C. § 1983 and state law claims for assault, battery, and intentional infliction of emotional distress.',
                'Defendants failed to adequately train and supervise their employees, creating a policy of deliberate indifference to constitutional rights.'
            ],
            'prayer': [
                'WHEREFORE, plaintiff respectfully requests that this Court award compensatory and punitive damages in an amount to be determined at trial.',
                'Plaintiff seeks injunctive relief requiring defendants to implement proper policies and training to prevent future violations.',
                'Plaintiff requests attorney\'s fees and costs pursuant to 42 U.S.C. § 1988 and other applicable law.',
                'Plaintiff seeks such other relief as this Court deems just and proper.'
            ],
            'jury_demand': [
                'Plaintiff hereby demands a trial by jury on all issues so triable as a matter of right.',
                'Pursuant to Federal Rule of Civil Procedure 38, plaintiff demands trial by jury of all claims presented in this complaint.',
                'Plaintiff respectfully requests a jury trial on all matters so triable.'
            ]
        }

        for document in documents:
            for section_type, _ in DocumentSection.SECTION_TYPES:
                content_options = section_content_templates.get(section_type, ['Standard legal content for this section.'])
                content = ' '.join(random.sample(content_options, min(len(content_options), random.randint(1, 3))))
                
                DocumentSection.objects.create(
                    document=document,
                    section_type=section_type,
                    title=dict(DocumentSection.SECTION_TYPES)[section_type],
                    content=content,
                    order=list(dict(DocumentSection.SECTION_TYPES).keys()).index(section_type)
                )

    def create_legal_templates(self):
        """Create comprehensive legal boilerplate templates for all violation types"""
        
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
        
        # Create templates using get_or_create to avoid duplicates
        for template_data in templates:
            template, created = LegalTemplate.objects.get_or_create(
                violation_type=template_data['violation_type'],
                location_type=template_data['location_type'],
                section_type=template_data['section_type'],
                defaults={'template_text': template_data['template_text']}
            )
            if created:
                self.stdout.write(f'Created legal template: {template_data["section_type"]} for {template_data["violation_type"]}')
            else:
                self.stdout.write(f'Template already exists: {template_data["section_type"]} for {template_data["violation_type"]}')