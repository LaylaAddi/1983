# documents/management/commands/seed_data.py
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from documents.models import LawsuitDocument, DocumentSection
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
            # Clear in proper order to avoid foreign key issues
            DocumentSection.objects.all().delete()
            LawsuitDocument.objects.all().delete()
            # Import UserProfile and clear it too
            from accounts.models import UserProfile
            UserProfile.objects.all().delete()
            User.objects.all().delete()
            from documents.models import LegalTemplate
            LegalTemplate.objects.all().delete()

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
                f'{documents_count} documents, and their sections!'
            )
        )

        self.stdout.write('Creating legal templates...')
        self.create_legal_templates()

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
                'is_admin': True,  # Make Stephen an admin
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
            # Use get_or_create for user
            user, user_created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['email'],  # Use email as username for email-based login
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            
            # Set password (in case user existed but password wasn't set properly)
            user.set_password(user_data['password'])
            
            # Set admin privileges
            if user_data['is_admin']:
                user.is_staff = True
                user.is_superuser = True
            
            user.save()
            
            # Create user profile with get_or_create to avoid duplicates
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
        
        # Create additional fake users (count - 2 since we created 2 specific ones)
        remaining_count = max(0, count - len(specific_users))
        for i in range(remaining_count):
            email = fake.email()
            # Ensure unique emails
            while User.objects.filter(email=email).exists():
                email = fake.email()
                
            user = User.objects.create_user(
                username=email,  # Use email as username for consistency
                email=email,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='testpassword123'
            )
            
            # Create fake user profile with get_or_create
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
    

    def create_legal_templates(self):
        """Create legal boilerplate templates"""
        templates = [
            {
                'violation_type': 'threatened_arrest_public',
                'location_type': 'traditional_public_forum',
                'section_type': 'jurisdiction',
                'template_text': 'This Court has jurisdiction over this action pursuant to 28 U.S.C. §§ 1331 and 1343(a)(3), as this action arises under the Constitution and laws of the United States, specifically 42 U.S.C. § 1983. Venue is proper in this district under 28 U.S.C. § 1391(b)(2).'
            },
            {
                'violation_type': 'threatened_arrest_public', 
                'location_type': 'traditional_public_forum',
                'section_type': 'claims',
                'template_text': 'Defendants violated Plaintiff\'s First Amendment rights by imposing a prior restraint on protected speech and newsgathering activities. The threat of arrest constitutes a prior restraint, which is presumptively unconstitutional.'
            }
        ]
        
        from documents.models import LegalTemplate
        for template_data in templates:
            template, created = LegalTemplate.objects.get_or_create(
                violation_type=template_data['violation_type'],
                location_type=template_data['location_type'], 
                section_type=template_data['section_type'],
                defaults={'template_text': template_data['template_text']}
            )
            if created:
                self.stdout.write(f'Created legal template: {template_data["section_type"]}')

    def create_legal_templates(self):
        """Create legal boilerplate templates"""
        from documents.models import LegalTemplate
        
        templates = [
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
            }
        ]
        
        for template_data in templates:
            template, created = LegalTemplate.objects.get_or_create(
                violation_type=template_data['violation_type'],
                location_type=template_data['location_type'],
                section_type=template_data['section_type'],
                defaults={'template_text': template_data['template_text']}
            )
            if created:
                self.stdout.write(f'Created legal template: {template_data["section_type"]}')

    def create_lawsuit_documents(self, users, count):
        # Civil rights violation scenarios
        violation_scenarios = [
            {
                'title': 'Police Excessive Force During Traffic Stop',
                'description': 'Officers used unnecessary force during routine traffic stop, resulting in injuries and civil rights violations.',
                'location': 'Main Street and Oak Avenue, {city}',
                'defendants': 'Officer John Smith (Badge #1234), Officer Jane Doe (Badge #5678), City of {city}',
            },
            {
                'title': 'Unlawful Search and Seizure of Property',
                'description': 'Police conducted warrantless search of home without probable cause, violating Fourth Amendment rights.',
                'location': '{address}',
                'defendants': 'Detective Mike Johnson, Sergeant Lisa Brown, {city} Police Department',
            },
            {
                'title': 'Discrimination in Public Accommodation',
                'description': 'Denied service at restaurant based on race, violating civil rights and equal protection laws.',
                'location': '{business_name} Restaurant, {address}',
                'defendants': 'Manager Robert Wilson, {business_name} LLC',
            },
            {
                'title': 'Employment Discrimination and Wrongful Termination',
                'description': 'Fired from job due to religious beliefs and practices, violating Title VII protections.',
                'location': '{company} Headquarters, {address}',
                'defendants': 'HR Director Sarah Davis, {company} Corporation',
            },
            {
                'title': 'Voting Rights Violation',
                'description': 'Denied access to polling station and prevented from exercising constitutional right to vote.',
                'location': '{city} Community Center, {address}',
                'defendants': 'Election Official Tom Anderson, {county} County Board of Elections',
            },
            {
                'title': 'Housing Discrimination Based on Disability',
                'description': 'Refused rental accommodation for service animal, violating Fair Housing Act.',
                'location': '{property_name} Apartments, {address}',
                'defendants': 'Property Manager Carol White, {property_name} Management LLC',
            }
        ]

        youtube_urls = [
            'https://youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtube.com/watch?v=J---aiyznGQ',
            'https://youtube.com/watch?v=y6120QOlsfU',
            'https://youtube.com/watch?v=dQw4w9WgXcQ',
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
            business_name = fake.company().split()[0]  # First word of company name
            company = fake.company()
            county = fake.city()  # Use as county name
            property_name = fake.street_name()
            
            # Format scenario data
            title = scenario['title']
            description = scenario['description']
            location = scenario['location'].format(
                city=city, address=address, business_name=business_name,
                company=company, property_name=property_name
            )
            defendants = scenario['defendants'].format(
                city=city, business_name=business_name, company=company,
                county=county, property_name=property_name
            )
            
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


                