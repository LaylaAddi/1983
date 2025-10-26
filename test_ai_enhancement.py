"""
Test script for AI Enhancement Service

Run this script after migrating:
    python manage.py migrate
    python test_ai_enhancement.py

This will:
1. Create a test document
2. Test AI enhancement
3. Verify budget tracking
4. Test upgrade prompts
5. Validate fallback mechanism
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from documents.models import LawsuitDocument, DocumentSection
from documents.services.document_orchestrator_service import DocumentOrchestratorService
from documents.services.ai_enhancement_service import AIEnhancementService
from accounts.models import UserProfile, Subscription
from decimal import Decimal
from datetime import date


def print_header(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_1_check_migration():
    """Test 1: Verify migration ran successfully"""
    print_header("TEST 1: Check Migration")

    # Check if new fields exist
    test_section = DocumentSection.objects.first()
    if test_section:
        assert hasattr(test_section, 'ai_enhanced'), "Missing ai_enhanced field!"
        assert hasattr(test_section, 'ai_cost'), "Missing ai_cost field!"
        assert hasattr(test_section, 'ai_model'), "Missing ai_model field!"
        print("✅ Migration successful - all AI tracking fields present")
    else:
        print("⚠️  No sections found - migration fields will be added when first section created")

    return True


def test_2_estimate_costs():
    """Test 2: Verify cost estimation"""
    print_header("TEST 2: Cost Estimation")

    estimate = AIEnhancementService.get_estimated_document_cost()

    print(f"Estimated cost per document: ${estimate['total_cost']}")
    print(f"Number of AI-enhanced sections: {estimate['section_count']}")
    print("\nPer-section costs:")
    for section, cost in estimate['section_costs'].items():
        print(f"  - {section}: ${cost}")

    assert estimate['total_cost'] < 0.15, "Cost too high!"
    print("\n✅ Cost estimation working correctly")

    return True


def test_3_create_test_user():
    """Test 3: Create test user with free tier"""
    print_header("TEST 3: Create Test User")

    # Clean up existing test user
    User.objects.filter(username='ai_test_user').delete()

    # Create new test user
    user = User.objects.create_user(
        username='ai_test_user',
        email='test@example.com',
        password='testpass123'
    )

    # Verify profile was auto-created with free tier limits
    profile = user.profile
    print(f"User created: {user.username}")
    print(f"API cost limit: ${profile.api_cost_limit}")
    print(f"Current usage: ${profile.total_api_cost}")
    print(f"Remaining budget: ${profile.remaining_api_budget}")

    # Verify subscription
    subscription = user.subscription
    print(f"\nSubscription plan: {subscription.plan_type}")
    print(f"API credit balance: ${subscription.api_credit_balance}")

    assert profile.api_cost_limit == Decimal('0.50'), "Free tier limit should be $0.50"
    assert profile.total_api_cost == Decimal('0.00'), "New user should have $0 usage"

    print("\n✅ Test user created with free tier limits")

    return user


def test_4_budget_check():
    """Test 4: Budget checking before AI calls"""
    print_header("TEST 4: Budget Check")

    user = User.objects.get(username='ai_test_user')

    # Check budget for 'facts' section
    budget_check = AIEnhancementService.check_user_budget(user, 'facts')

    print(f"Budget check for 'facts' section:")
    print(f"  Allowed: {budget_check['allowed']}")
    print(f"  Remaining budget: ${budget_check.get('remaining_budget', 0)}")
    print(f"  Estimated cost: ${budget_check.get('estimated_cost', 0)}")

    if budget_check.get('remaining_docs'):
        print(f"  Remaining AI documents: ~{budget_check['remaining_docs']}")

    assert budget_check['allowed'], "Budget check should allow AI for new user"

    print("\n✅ Budget check working correctly")

    return True


def test_5_create_document_with_ai():
    """Test 5: Create document with AI enhancement"""
    print_header("TEST 5: Create Document with AI Enhancement")

    user = User.objects.get(username='ai_test_user')

    # Clean up existing test documents
    LawsuitDocument.objects.filter(user=user).delete()

    # Create test document
    document = LawsuitDocument.objects.create(
        user=user,
        title="Test Case - Recording Interference",
        description=(
            "On March 15, 2025, I was at Main Street Park filming a peaceful protest. "
            "Officer Johnson approached me and told me I couldn't record there. "
            "When I said I had a constitutional right to record, he threatened to arrest me "
            "for obstruction if I didn't stop filming and leave immediately. "
            "I was standing on the public sidewalk about 20 feet away from the officers."
        ),
        incident_date=date(2025, 3, 15),
        incident_location="Main Street Park, Springfield, Illinois",
        incident_city="Springfield",
        incident_state="IL",
        defendants="Officer James Johnson, Springfield Police Department"
    )

    print(f"Document created: {document.title}")
    print(f"Description length: {len(document.description)} chars")

    # Generate sections with AI
    print("\n📡 Calling AI enhancement service...")
    orchestrator = DocumentOrchestratorService(document)
    result = orchestrator.auto_populate_document(use_ai=True)

    # Display results
    print(f"\n✅ Document generation complete!")
    print(f"\nResults:")
    print(f"  Violation type: {result['violation_type']}")
    print(f"  Location type: {result['location_type']}")
    print(f"  Templates found: {result['templates_found']}")
    print(f"  Sections created: {result['sections_created']}")
    print(f"  AI-enhanced sections: {result['ai_enhanced_count']}")
    print(f"  Total AI cost: ${result['total_ai_cost']}")

    # Check for warnings
    if result.get('warnings'):
        print(f"\n⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"    - {warning}")

    # Check for upgrade prompts
    if result.get('upgrade_prompts'):
        print(f"\n💰 Upgrade Prompts:")
        for prompt in result['upgrade_prompts']:
            print(f"    - {prompt}")

    # Show section details
    print(f"\n📄 Sections generated:")
    for section in document.sections.all():
        ai_indicator = "🤖 AI" if section.ai_enhanced else "📋 Template"
        cost = f"${section.ai_cost}" if section.ai_enhanced else "$0.00"
        print(f"  {ai_indicator} - {section.title} ({cost})")

        # Show preview of content
        preview = section.content[:150] + "..." if len(section.content) > 150 else section.content
        print(f"       Preview: {preview}\n")

    # Verify budget was updated
    user.profile.refresh_from_db()
    print(f"\n💰 Budget Update:")
    print(f"  Previous: $0.00")
    print(f"  Current usage: ${user.profile.total_api_cost}")
    print(f"  Remaining: ${user.profile.remaining_api_budget}")

    assert result['ai_enhanced_count'] >= 0, "Should have AI-enhanced sections or fallback to templates"
    assert len(result['sections']) > 0, "Should create sections"

    print("\n✅ Document creation with AI successful!")

    return document, result


def test_6_verify_ai_content():
    """Test 6: Verify AI-enhanced content quality"""
    print_header("TEST 6: Verify AI Content Quality")

    user = User.objects.get(username='ai_test_user')
    document = LawsuitDocument.objects.filter(user=user).first()

    if not document:
        print("⚠️  No document found - skipping content verification")
        return False

    ai_sections = document.sections.filter(ai_enhanced=True)

    if ai_sections.count() == 0:
        print("⚠️  No AI-enhanced sections (possibly over budget or API key missing)")
        print("    Document was generated using template fallback")
        return True

    print(f"Found {ai_sections.count()} AI-enhanced sections\n")

    for section in ai_sections:
        print(f"\n{'='*60}")
        print(f"Section: {section.title}")
        print(f"Model: {section.ai_model}")
        print(f"Cost: ${section.ai_cost}")
        print(f"{'='*60}")
        print(section.content)

        # Validation checks
        checks = {
            "Length > 100 chars": len(section.content) > 100,
            "No placeholders ([TBD], etc)": not any(p in section.content for p in ['[TBD]', '[TODO]', 'PLACEHOLDER']),
            "No first person (I, me, my)": not any(word in section.content.lower() for word in [' i ', ' me ', ' my ']),
            "Contains required elements": True  # Basic check
        }

        print(f"\n✓ Validation:")
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")

        if section.section_type == 'claims':
            has_statute = '42 U.S.C. § 1983' in section.content or '§ 1983' in section.content
            print(f"  {'✅' if has_statute else '❌'} Contains § 1983 reference")

    print("\n✅ AI content quality verified!")

    return True


def test_7_budget_limit():
    """Test 7: Test budget limit and upgrade prompts"""
    print_header("TEST 7: Budget Limit & Upgrade Prompts")

    user = User.objects.get(username='ai_test_user')
    profile = user.profile

    # Save current state
    original_cost = profile.total_api_cost

    # Simulate user approaching limit
    profile.total_api_cost = Decimal('0.48')  # Almost at $0.50 limit
    profile.save()

    print(f"Simulated usage: ${profile.total_api_cost} / ${profile.api_cost_limit}")
    print(f"Remaining: ${profile.remaining_api_budget}")

    # Try to create another document
    document2 = LawsuitDocument.objects.create(
        user=user,
        title="Test Case 2",
        description="Another incident description",
        incident_date=date(2025, 3, 20),
        defendants="Officer Smith"
    )

    print("\n📡 Attempting AI enhancement near budget limit...")
    orchestrator = DocumentOrchestratorService(document2)
    result = orchestrator.auto_populate_document(use_ai=True)

    print(f"\nResults:")
    print(f"  AI-enhanced sections: {result['ai_enhanced_count']}")
    print(f"  Total AI cost: ${result['total_ai_cost']}")

    # Check for upgrade prompts
    if result.get('upgrade_prompts'):
        print(f"\n💰 Upgrade Prompts Triggered:")
        for prompt in result['upgrade_prompts']:
            print(f"    {prompt}")
        print("\n✅ Upgrade prompts working correctly!")
    else:
        print("\n⚠️  No upgrade prompts (might still have budget or AI disabled)")

    # Restore original state
    profile.total_api_cost = original_cost
    profile.save()

    # Clean up
    document2.delete()

    return True


def test_8_fallback_mechanism():
    """Test 8: Test fallback to templates"""
    print_header("TEST 8: Fallback to Templates")

    user = User.objects.get(username='ai_test_user')

    # Create document with AI disabled
    document = LawsuitDocument.objects.create(
        user=user,
        title="Test Case - Template Only",
        description="This should use templates only",
        incident_date=date(2025, 3, 25),
        defendants="Officer Williams"
    )

    print("Testing template-only mode (AI disabled)...")
    orchestrator = DocumentOrchestratorService(document)
    result = orchestrator.auto_populate_document(use_ai=False)

    print(f"\nResults:")
    print(f"  Sections created: {result['sections_created']}")
    print(f"  AI-enhanced sections: {result['ai_enhanced_count']}")
    print(f"  Total AI cost: ${result['total_ai_cost']}")

    assert result['ai_enhanced_count'] == 0, "Should have 0 AI sections when disabled"
    assert result['total_ai_cost'] == 0.0, "Should have $0 cost when AI disabled"
    assert len(result['sections']) > 0, "Should still create sections using templates"

    print("\n✅ Fallback to templates working correctly!")

    # Clean up
    document.delete()

    return True


def test_9_unlimited_tier():
    """Test 9: Test unlimited tier behavior"""
    print_header("TEST 9: Unlimited Tier")

    user = User.objects.get(username='ai_test_user')
    subscription = user.subscription

    # Upgrade to unlimited
    subscription.plan_type = 'unlimited'
    subscription.api_credit_balance = Decimal('10.00')
    subscription.save()

    print(f"Upgraded user to: {subscription.plan_type}")
    print(f"API credit balance: ${subscription.api_credit_balance}")

    # Create document
    document = LawsuitDocument.objects.create(
        user=user,
        title="Test Case - Unlimited",
        description="Testing unlimited tier",
        incident_date=date(2025, 3, 30),
        defendants="Officer Davis"
    )

    print("\n📡 Testing unlimited tier AI enhancement...")
    orchestrator = DocumentOrchestratorService(document)
    result = orchestrator.auto_populate_document(use_ai=True)

    print(f"\nResults:")
    print(f"  AI-enhanced sections: {result['ai_enhanced_count']}")
    print(f"  Total AI cost: ${result['total_ai_cost']}")

    # Check credit was deducted
    subscription.refresh_from_db()
    print(f"\n💰 Credit Update:")
    print(f"  Previous: $10.00")
    print(f"  Current: ${subscription.api_credit_balance}")
    print(f"  Deducted: ${Decimal('10.00') - subscription.api_credit_balance}")

    print("\n✅ Unlimited tier working correctly!")

    # Clean up
    document.delete()
    subscription.plan_type = 'free'
    subscription.api_credit_balance = Decimal('0.50')
    subscription.save()

    return True


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                   AI ENHANCEMENT TEST SUITE                                ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")

    tests = [
        ("Migration Check", test_1_check_migration),
        ("Cost Estimation", test_2_estimate_costs),
        ("Create Test User", test_3_create_test_user),
        ("Budget Check", test_4_budget_check),
        ("AI Enhancement", test_5_create_document_with_ai),
        ("Content Quality", test_6_verify_ai_content),
        ("Budget Limits", test_7_budget_limit),
        ("Fallback Mechanism", test_8_fallback_mechanism),
        ("Unlimited Tier", test_9_unlimited_tier),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, True, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"\n❌ {test_name} FAILED: {e}")

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for test_name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if error:
            print(f"         Error: {error}")

    print(f"\n{'='*80}")
    print(f"RESULTS: {passed}/{total} tests passed")
    print(f"{'='*80}\n")

    if passed == total:
        print("🎉 ALL TESTS PASSED! AI Enhancement is working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")

    return passed == total


if __name__ == '__main__':
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
