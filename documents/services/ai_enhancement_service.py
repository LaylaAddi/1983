# documents/services/ai_enhancement_service.py
"""
AI Enhancement Service for Legal Document Generation

Uses OpenAI GPT-4 to transform user descriptions into professional legal language
while preserving the legal accuracy of templates.

Features:
- Budget checking before API calls
- Cost estimation and tracking
- Upgrade prompts when limits reached
- Fallback to templates on failure
- Token limits per section
"""

import os
import re
from decimal import Decimal
from string import Template
from openai import OpenAI
from django.utils import timezone
from django.db import transaction


class AIEnhancementService:
    """Service to enhance legal sections using OpenAI while maintaining budget controls"""

    # Section configuration
    AI_ENHANCED_SECTIONS = {
        'facts': {
            'enabled': True,
            'priority': 'HIGH',
            'model': 'gpt-4o',
            'temperature': 0.3,
            'max_tokens': 800,
            'estimated_cost': 0.025,  # Estimated cost per call
        },
        'introduction': {
            'enabled': True,
            'priority': 'HIGH',
            'model': 'gpt-4o',
            'temperature': 0.3,
            'max_tokens': 400,
            'estimated_cost': 0.015,
        },
        'claims': {
            'enabled': True,
            'priority': 'HIGH',
            'model': 'gpt-4o',
            'temperature': 0.2,  # Very low - preserve legal accuracy
            'max_tokens': 800,
            'estimated_cost': 0.025,
        },
        'parties': {
            'enabled': True,
            'priority': 'MEDIUM',
            'model': 'gpt-4o',
            'temperature': 0.3,
            'max_tokens': 300,
            'estimated_cost': 0.012,
        },
        # These sections don't need AI - pure legal boilerplate
        'jurisdiction': {'enabled': False},
        'prayer': {'enabled': False},
        'jury_demand': {'enabled': False},
    }

    @classmethod
    def check_user_budget(cls, user, section_type):
        """
        Check if user has sufficient budget for AI enhancement.

        Returns:
            dict with keys:
            - 'allowed': bool
            - 'reason': str (if not allowed)
            - 'remaining_budget': float
            - 'estimated_cost': float
            - 'upgrade_prompt': str (if over limit)
        """
        from accounts.models import Subscription

        # Get section config
        config = cls.AI_ENHANCED_SECTIONS.get(section_type, {})
        if not config.get('enabled'):
            return {
                'allowed': False,
                'reason': 'AI not enabled for this section type',
                'fallback_to_template': True
            }

        estimated_cost = config.get('estimated_cost', 0.02)

        # Get user's subscription
        try:
            subscription = user.subscription
            profile = user.profile
        except:
            return {
                'allowed': False,
                'reason': 'User subscription not found',
                'fallback_to_template': True
            }

        # UNLIMITED PLAN - Check api_credit_balance
        if subscription.plan_type == 'unlimited' and subscription.is_active:
            if subscription.api_credit_balance >= Decimal(str(estimated_cost)):
                return {
                    'allowed': True,
                    'remaining_budget': float(subscription.api_credit_balance),
                    'estimated_cost': estimated_cost,
                    'plan_type': 'unlimited'
                }
            else:
                return {
                    'allowed': False,
                    'reason': 'Monthly API credit exhausted',
                    'remaining_budget': float(subscription.api_credit_balance),
                    'estimated_cost': estimated_cost,
                    'upgrade_prompt': f"You've used your ${subscription.monthly_credit_amount}/month AI credit. More credit will be added next month.",
                    'fallback_to_template': True
                }

        # FREE or PAY_PER_DOC PLAN - Check api_cost_limit
        remaining = profile.remaining_api_budget

        if remaining >= estimated_cost:
            # Calculate how many more AI-enhanced documents they can create
            avg_cost_per_doc = 0.06  # ~4 sections × $0.015 avg
            remaining_docs = int(remaining / avg_cost_per_doc)

            # Warn if getting low (< 2 documents remaining)
            warning = None
            if remaining < (avg_cost_per_doc * 2):
                warning = f"Low AI budget: Only ~{remaining_docs} AI-enhanced documents remaining. Upgrade to Unlimited for $10/month AI credit!"

            return {
                'allowed': True,
                'remaining_budget': remaining,
                'estimated_cost': estimated_cost,
                'remaining_docs': remaining_docs,
                'warning': warning,
                'plan_type': subscription.plan_type
            }
        else:
            # OVER LIMIT - Return upgrade prompt
            return {
                'allowed': False,
                'reason': 'API budget limit reached',
                'remaining_budget': remaining,
                'estimated_cost': estimated_cost,
                'current_usage': float(profile.total_api_cost),
                'limit': float(profile.api_cost_limit),
                'usage_percentage': profile.usage_percentage,
                'upgrade_prompt': cls._get_upgrade_prompt(subscription.plan_type),
                'fallback_to_template': True
            }

    @staticmethod
    def _get_upgrade_prompt(current_plan):
        """Generate appropriate upgrade prompt based on current plan"""
        if current_plan == 'free':
            return (
                "You've reached your free tier AI limit ($0.50). "
                "Upgrade to Unlimited ($499/month) for AI-enhanced documents with $10/month AI credit, "
                "or switch to Pay Per Document ($149 each) for professional templates."
            )
        elif current_plan == 'pay_per_doc':
            return (
                "You've reached your AI budget limit. "
                "Upgrade to Unlimited ($499/month) for AI-enhanced documents with $10/month AI credit!"
            )
        else:
            return "AI budget exhausted. Please contact support."

    @classmethod
    def enhance_section(cls, template, document, context_data, timeout=10):
        """
        Enhance a section using AI.

        Args:
            template: LegalTemplate instance
            document: LawsuitDocument instance
            context_data: dict with placeholder values
            timeout: API timeout in seconds

        Returns:
            dict with keys:
            - 'success': bool
            - 'content': str (enhanced content if success)
            - 'cost': float (actual cost)
            - 'method': str ('ai' or 'template_fallback')
            - 'error': str (if failed)
            - 'upgrade_prompt': str (if budget exceeded)
        """
        section_type = template.section_type

        # Check if AI is enabled for this section
        config = cls.AI_ENHANCED_SECTIONS.get(section_type, {})
        if not config.get('enabled'):
            return {
                'success': False,
                'reason': 'AI not enabled for this section',
                'method': 'template_fallback'
            }

        # Check user budget BEFORE calling API
        budget_check = cls.check_user_budget(document.user, section_type)

        if not budget_check['allowed']:
            return {
                'success': False,
                'reason': budget_check['reason'],
                'upgrade_prompt': budget_check.get('upgrade_prompt'),
                'remaining_budget': budget_check.get('remaining_budget', 0),
                'method': 'template_fallback'
            }

        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {
                'success': False,
                'error': 'OpenAI API key not configured',
                'method': 'template_fallback'
            }

        try:
            # Build the prompt
            prompt = cls._build_prompt(section_type, template, document, context_data)

            # Call OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=config['model'],
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are an expert legal writer specializing in federal civil rights litigation under 42 U.S.C. § 1983.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                top_p=0.9,
                frequency_penalty=0.3,
                presence_penalty=0.1,
                timeout=timeout
            )

            ai_content = response.choices[0].message.content.strip()

            # Calculate actual cost (GPT-4o pricing: $2.50/1M input, $10/1M output)
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            actual_cost = (input_tokens * 0.0000025) + (output_tokens * 0.00001)

            # Validate output
            validation = cls._validate_output(ai_content, section_type, template)

            if not validation['valid']:
                return {
                    'success': False,
                    'error': f"AI output validation failed: {validation['reason']}",
                    'cost': actual_cost,
                    'method': 'template_fallback'
                }

            # Track cost in user's profile and subscription
            cls._track_api_cost(document.user, actual_cost, budget_check['plan_type'])

            # Return success with warning if low budget
            result = {
                'success': True,
                'content': ai_content,
                'cost': actual_cost,
                'model': config['model'],
                'method': 'ai',
                'tokens_used': response.usage.total_tokens
            }

            # Add warning if user is getting low on budget
            if budget_check.get('warning'):
                result['warning'] = budget_check['warning']

            return result

        except Exception as e:
            return {
                'success': False,
                'error': f'AI enhancement error: {str(e)}',
                'method': 'template_fallback'
            }

    @classmethod
    def _build_prompt(cls, section_type, template, document, context_data):
        """Build the appropriate prompt for the section type"""

        # Get violation and location type for context
        from documents.services.violation_analysis_service import ViolationAnalysisService
        violation_type = ViolationAnalysisService.analyze_violation_type(document.description)
        location_type = ViolationAnalysisService.analyze_location_type(
            document.incident_location or ''
        )

        # Common context
        common_context = {
            'template_text': template.template_text,
            'user_description': document.description or '[No description provided]',
            'incident_date': context_data.get('incident_date', '[DATE]'),
            'incident_location': context_data.get('incident_location', '[LOCATION]'),
            'defendants': context_data.get('defendants', '[DEFENDANTS]'),
            'violation_type': violation_type,
            'location_type': location_type,
        }

        # Section-specific prompts
        prompts = {
            'facts': cls._get_facts_prompt(),
            'introduction': cls._get_introduction_prompt(),
            'claims': cls._get_claims_prompt(),
            'parties': cls._get_parties_prompt(),
        }

        prompt_template = prompts.get(section_type, '')
        return Template(prompt_template).substitute(common_context)

    @staticmethod
    def _get_facts_prompt():
        """Get prompt template for FACTS section"""
        return """You are an expert legal writer specializing in civil rights litigation under 42 U.S.C. § 1983.

TASK: Transform the user's incident description into a professional "Statement of Facts" section for a federal civil rights complaint, while maintaining strict factual accuracy.

LEGAL REQUIREMENTS:
- Use formal legal writing style appropriate for federal court filings
- Write in past tense, third person ("Plaintiff was present...")
- Present facts chronologically
- Use precise, objective language
- Do NOT add facts not present in the user's description
- Do NOT make assumptions about intent, motive, or internal states
- Do NOT use emotional or inflammatory language
- PRESERVE all specific details (names, dates, locations, quotes)

TEMPLATE FRAMEWORK (preserve this legal structure):
$template_text

USER'S INCIDENT DESCRIPTION:
$user_description

CONTEXT DATA:
- Incident Date: $incident_date
- Incident Location: $incident_location
- Defendants: $defendants
- Violation Type: $violation_type
- Location Type: $location_type

OUTPUT INSTRUCTIONS:
1. Begin with date and location using the context data
2. Transform the user's description into professional legal narrative
3. Organize facts chronologically and logically
4. Include relevant legal characterizations from the template (e.g., "traditional public forum", "acting under color of state law")
5. End with a statement about the lawful nature of plaintiff's conduct
6. Length: 3-5 paragraphs, approximately 300-500 words

CRITICAL: Only include facts explicitly stated or clearly implied in the user's description. Do NOT fabricate details.

Output only the facts section content. Do not include headers, titles, or explanatory text."""

    @staticmethod
    def _get_introduction_prompt():
        """Get prompt template for INTRODUCTION section"""
        return """You are an expert legal writer specializing in civil rights litigation under 42 U.S.C. § 1983.

TASK: Write a professional "Introduction" section for a federal civil rights complaint that summarizes the constitutional violations based on the user's incident.

LEGAL REQUIREMENTS:
- Keep it concise (2-3 sentences)
- Use formal legal writing style
- Reference the specific constitutional amendment(s) violated
- Reference 42 U.S.C. § 1983
- Do NOT add factual details beyond what the user described
- Use appropriate legal terminology

TEMPLATE FRAMEWORK:
$template_text

USER'S INCIDENT SUMMARY:
$user_description

VIOLATION TYPE: $violation_type
LOCATION TYPE: $location_type

OUTPUT INSTRUCTIONS:
1. Start with a clear statement that this is a civil rights action under § 1983
2. Identify which constitutional rights were violated (First Amendment, Fourth Amendment, etc.)
3. Briefly characterize the defendant's conduct (e.g., "unlawful interference", "retaliatory conduct", "prior restraint")
4. Mention the relief sought (damages and injunctive relief)
5. Length: 2-4 sentences maximum

CRITICAL: Be specific about which constitutional rights were violated based on the violation type, but do NOT add factual details.

Output only the introduction text. Do not include section headers or titles."""

    @staticmethod
    def _get_claims_prompt():
        """Get prompt template for CLAIMS section"""
        return """You are an expert legal writer specializing in federal civil rights litigation under 42 U.S.C. § 1983.

TASK: Enhance the "Claims for Relief" section by integrating specific facts from the user's incident into the existing legal framework and citations.

CRITICAL LEGAL REQUIREMENTS:
- PRESERVE ALL case citations exactly as provided in the template (e.g., "Glik v. Cunniffe, 655 F.3d 78 (1st Cir. 2011)")
- PRESERVE ALL legal standards and tests (e.g., "strict scrutiny", "clearly established")
- PRESERVE ALL statutory references (e.g., "42 U.S.C. § 1983")
- Do NOT add new case citations
- Do NOT change legal standards
- Do NOT fabricate legal arguments

YOUR ROLE: Weave the user's specific factual allegations into the existing legal framework.

TEMPLATE WITH LEGAL FRAMEWORK (preserve all citations and standards):
$template_text

USER'S FACTUAL ALLEGATIONS:
$user_description

CONTEXT:
- Violation Type: $violation_type
- Location Type: $location_type
- Defendants: $defendants

OUTPUT INSTRUCTIONS:
1. Keep the COUNT heading exactly as provided in template
2. Keep all case citations and legal standards from the template
3. Add 1-2 sentences referencing the specific facts from the user's description
4. Maintain the legal analysis structure from the template
5. End with the constitutional standard (e.g., strict scrutiny) from the template
6. Length: Keep similar to template length (approximately 150-300 words)

EXAMPLE INTEGRATION:
Template says: "Defendants violated Plaintiff's First Amendment rights..."
Enhanced version: "Defendants violated Plaintiff's First Amendment rights by [SPECIFIC CONDUCT FROM USER'S DESCRIPTION]..."

Output only the claims section content. Do not include section headers."""

    @staticmethod
    def _get_parties_prompt():
        """Get prompt template for PARTIES section"""
        return """You are an expert legal writer for federal civil rights complaints under 42 U.S.C. § 1983.

TASK: Write a professional "Parties" section that describes the plaintiff and defendants with appropriate legal formality.

LEGAL REQUIREMENTS:
- Identify plaintiff's citizenship and residency
- Identify defendants by name and official capacity
- Include "acting under color of state law" for government defendants
- Use formal, objective language
- Do NOT add titles, badge numbers, or details not provided by the user
- Do NOT make assumptions about defendants' roles

TEMPLATE FRAMEWORK:
$template_text

CONTEXT DATA:
- Plaintiff Name: ${context_data.get('plaintiff_name', '[NAME]')}
- Plaintiff State: ${context_data.get('plaintiff_state', '[STATE]')}
- Defendants: $defendants

OUTPUT INSTRUCTIONS:
1. First paragraph: Describe plaintiff (name, citizenship, residency)
2. Second paragraph: Describe defendants based on information provided
3. For law enforcement defendants, include "acting under color of state law"
4. If specific titles/positions are provided, use them; otherwise, use general description
5. Length: 2-3 sentences total

CRITICAL: Only use defendant information explicitly provided. Do not invent badge numbers, specific titles, or organizational details.

Output only the parties section content."""

    @classmethod
    def _validate_output(cls, content, section_type, template):
        """Validate AI output before using it"""

        # Check minimum length
        if len(content) < 100:
            return {'valid': False, 'reason': 'Output too short'}

        # Check maximum length
        if len(content) > 3000:
            return {'valid': False, 'reason': 'Output too long'}

        # Check for placeholders that shouldn't be there
        placeholder_pattern = r'\[.*?\]|\{.*?\}|TODO|TBD|PLACEHOLDER'
        if re.search(placeholder_pattern, content, re.IGNORECASE):
            return {'valid': False, 'reason': 'Contains placeholders'}

        # Check for XML/HTML tags
        if re.search(r'<[^>]+>', content):
            return {'valid': False, 'reason': 'Contains HTML/XML tags'}

        # Section-specific validation
        if section_type == 'claims':
            # Must preserve § 1983 reference
            if '42 U.S.C. § 1983' not in content and '§ 1983' not in content:
                return {'valid': False, 'reason': 'Missing required statutory reference'}

            # Should preserve case citations if template has them
            template_citations = re.findall(r'\d+ F\.\d+d \d+', template.template_text)
            content_citations = re.findall(r'\d+ F\.\d+d \d+', content)
            if template_citations and not content_citations:
                return {'valid': False, 'reason': 'Lost case citations from template'}

        if section_type == 'facts':
            # Should be mostly past tense
            # Check for first person (should be third person)
            first_person_pattern = r'\b(I|me|my|we|our)\b'
            if re.search(first_person_pattern, content, re.IGNORECASE):
                return {'valid': False, 'reason': 'Contains first person pronouns (should be third person)'}

        return {'valid': True}

    @staticmethod
    @transaction.atomic
    def _track_api_cost(user, cost, plan_type):
        """
        Track API cost in user's profile and subscription.
        Uses atomic transaction to ensure consistency.
        """
        from accounts.models import Subscription

        cost_decimal = Decimal(str(cost))

        # Always track in UserProfile.total_api_cost
        profile = user.profile
        profile.add_api_cost(cost_decimal)

        # For unlimited users, also deduct from api_credit_balance
        if plan_type == 'unlimited':
            try:
                subscription = user.subscription
                subscription.deduct_api_cost(cost_decimal)
            except Subscription.DoesNotExist:
                pass

    @classmethod
    def get_estimated_document_cost(cls, section_types=None):
        """
        Estimate the cost for AI-enhancing a document.

        Args:
            section_types: list of section types to enhance (default: all enabled sections)

        Returns:
            dict with 'total_cost', 'section_costs', 'section_count'
        """
        if section_types is None:
            section_types = [s for s, config in cls.AI_ENHANCED_SECTIONS.items()
                           if config.get('enabled')]

        section_costs = {}
        total_cost = 0.0

        for section_type in section_types:
            config = cls.AI_ENHANCED_SECTIONS.get(section_type, {})
            if config.get('enabled'):
                cost = config.get('estimated_cost', 0.02)
                section_costs[section_type] = cost
                total_cost += cost

        return {
            'total_cost': round(total_cost, 3),
            'section_costs': section_costs,
            'section_count': len(section_costs)
        }
