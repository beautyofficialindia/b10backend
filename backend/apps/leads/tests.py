from django.test import TestCase
from apps.chatbot.models import ConversationSession
from apps.leads.models import Lead
from apps.leads.services.qualification_service import QualificationService
from apps.leads.services.lead_extractor import LeadExtractor


# =========================================================================
# Qualification Tests
# =========================================================================

class QualificationTests(TestCase):
    """
    Mandatory fields: full_name, email, requirements.
    All other fields are optional enrichment and must NOT block qualification.
    """

    def setUp(self):
        self.session = ConversationSession.objects.create()
        self.lead = Lead.objects.create(conversation=self.session)
        self.qual_service = QualificationService()

    # --- Core mandatory-field behaviour ---

    def test_empty_lead_is_gathering(self):
        status, missing, just_qualified = self.qual_service.calculate_status(self.lead)
        self.assertEqual(status, 'gathering')
        self.assertIn('full_name', missing)
        self.assertIn('email', missing)
        self.assertIn('requirements', missing)
        self.assertFalse(just_qualified)

    def test_missing_fields(self):
        """Alias for test_empty_lead_is_gathering — keeps backward compatibility."""
        status, missing, just_qualified = self.qual_service.calculate_status(self.lead)
        self.assertEqual(status, 'gathering')
        self.assertIn('email', missing)
        self.assertFalse(just_qualified)

    def test_qualifies_with_only_three_mandatory_fields(self):
        """A lead with full_name + email + requirements qualifies immediately."""
        self.lead.full_name = 'Test User'
        self.lead.email = 'test@test.com'
        self.lead.requirements = 'Build an inventory management system with supplier tracking.'
        self.lead.save()
        status, missing, just_qualified = self.qual_service.calculate_status(self.lead)
        self.assertEqual(status, 'qualified')
        self.assertEqual(missing, [])
        self.assertTrue(just_qualified)

    def test_qualified(self):
        """Backward-compat: fully populated lead (including optional fields) qualifies."""
        self.lead.full_name = 'Test User'
        self.lead.company_name = 'Test Company'
        self.lead.email = 'test@test.com'
        self.lead.industry = 'Tech'
        self.lead.project_type = 'Web'
        self.lead.requirements = 'Build a site'
        self.lead.save()
        status, missing, just_qualified = self.qual_service.calculate_status(self.lead)
        self.assertEqual(status, 'qualified')
        self.assertEqual(len(missing), 0)
        self.assertTrue(just_qualified)

    def test_optional_fields_do_not_block_qualification(self):
        """Company, industry, project_type absent → still qualifies."""
        self.lead.full_name = 'Jane Smith'
        self.lead.email = 'jane@example.com'
        self.lead.requirements = 'We need a mobile app for delivery tracking with real-time GPS.'
        self.lead.save()
        status, missing, _ = self.qual_service.calculate_status(self.lead)
        self.assertEqual(status, 'qualified')
        self.assertNotIn('company_name', missing)
        self.assertNotIn('industry', missing)
        self.assertNotIn('project_type', missing)

    def test_missing_email_blocks_qualification(self):
        self.lead.full_name = 'John Doe'
        self.lead.requirements = 'We need a platform for managing field service requests.'
        self.lead.save()
        status, missing, just_qualified = self.qual_service.calculate_status(self.lead)
        self.assertEqual(status, 'gathering')
        self.assertIn('email', missing)
        self.assertFalse(just_qualified)

    def test_missing_requirements_blocks_qualification(self):
        self.lead.full_name = 'John Doe'
        self.lead.email = 'john@example.com'
        self.lead.save()
        status, missing, just_qualified = self.qual_service.calculate_status(self.lead)
        self.assertEqual(status, 'gathering')
        self.assertIn('requirements', missing)
        self.assertFalse(just_qualified)

    def test_missing_name_blocks_qualification(self):
        self.lead.email = 'john@example.com'
        self.lead.requirements = 'We need an inventory tracking system with barcode scanning.'
        self.lead.save()
        status, missing, just_qualified = self.qual_service.calculate_status(self.lead)
        self.assertEqual(status, 'gathering')
        self.assertIn('full_name', missing)
        self.assertFalse(just_qualified)

    def test_name_and_company_required(self):
        """Backward-compat: verifies name is still required. Company is NOT required."""
        self.lead.email = 'test@test.com'
        self.lead.requirements = 'Build a site for managing service bookings and customer profiles.'
        self.lead.save()
        status, missing, just_qualified = self.qual_service.calculate_status(self.lead)
        self.assertEqual(status, 'gathering')
        self.assertIn('full_name', missing)
        self.assertNotIn('company_name', missing)   # company is optional
        self.assertFalse(just_qualified)

    # --- qualified_at write-once semantics ---

    def test_qualified_at_stamped_on_qualification(self):
        """qualified_at must be set when the lead first qualifies."""
        self.lead.full_name = 'Test User'
        self.lead.email = 'test@test.com'
        self.lead.requirements = 'Build a site'
        self.lead.save()
        self.qual_service.calculate_status(self.lead)
        self.lead.refresh_from_db()
        self.assertIsNotNone(self.lead.qualified_at)

    def test_qualified_at_none_when_gathering(self):
        """qualified_at must remain None for leads still gathering."""
        self.qual_service.calculate_status(self.lead)
        self.assertIsNone(self.lead.qualified_at)

    def test_just_qualified_false_on_re_evaluation(self):
        """Re-evaluating an already-qualified lead must not set just_qualified."""
        self.lead.full_name = 'Test User'
        self.lead.email = 'test@test.com'
        self.lead.requirements = 'Build a site'
        self.lead.save()
        self.qual_service.calculate_status(self.lead)          # first call — qualifies
        _, _, just_qualified = self.qual_service.calculate_status(self.lead)  # second call
        self.assertFalse(just_qualified)


# =========================================================================
# Lead Extractor Tests
# =========================================================================

class LeadExtractorTests(TestCase):

    def setUp(self):
        self.extractor = LeadExtractor()

    # --- Requirements ---

    def test_requirements_extracted_without_project_type(self):
        """Requirements must be extracted even when project type is not in the same message."""
        text = "We need inventory management, seller dashboard and payment gateway integration."
        result = self.extractor.extract(text)
        self.assertIn('requirements', result)
        self.assertEqual(result['requirements'], text)

    def test_short_message_does_not_extract_requirements(self):
        """Messages with 7 or fewer words must not produce requirements."""
        result = self.extractor.extract("Hello there, how are you?")
        self.assertNotIn('requirements', result)

    # --- Email ---

    def test_email_extraction(self):
        result = self.extractor.extract("My email is john@example.com")
        self.assertEqual(result.get('email'), 'john@example.com')

    # --- Phone ---

    def test_phone_extraction(self):
        result = self.extractor.extract("Call me at 555-123-4567 anytime")
        self.assertIn('phone', result)

    def test_phone_with_country_code_extracted(self):
        result = self.extractor.extract("My number is +91 9876543210")
        self.assertIn('phone', result)

    # --- Company Name ---

    def test_company_founder_of(self):
        result = self.extractor.extract("I'm the Founder of Acme Corp")
        self.assertEqual(result.get('company_name'), 'Acme Corp')

    def test_company_my_company_is(self):
        result = self.extractor.extract("My company is Nexus Labs")
        self.assertEqual(result.get('company_name'), 'Nexus Labs')

    def test_company_we_are(self):
        result = self.extractor.extract("We are Quantum Solutions")
        self.assertEqual(result.get('company_name'), 'Quantum Solutions')

    def test_company_colon_format(self):
        result = self.extractor.extract("Company: TechVentures")
        self.assertEqual(result.get('company_name'), 'TechVentures')

    def test_company_ceo_of(self):
        result = self.extractor.extract("I'm the CEO of BrightEdge")
        self.assertEqual(result.get('company_name'), 'BrightEdge')

    def test_company_from_city_no_false_positive(self):
        """'from' is not a company trigger — city names must not be extracted."""
        result = self.extractor.extract("I'm from Hyderabad and looking for a developer")
        self.assertNotIn('company_name', result)

    def test_company_at_no_false_positive(self):
        """'at' is not a company trigger — must not extract 'a cafe' or similar."""
        result = self.extractor.extract("I was working at a startup before")
        # 'a startup' starts with lowercase 'a', so the uppercase guard rejects it
        company = result.get('company_name')
        self.assertIsNone(company)

    # --- Budget ---

    def test_budget_inr_lakh(self):
        result = self.extractor.extract("Our budget is ₹12 lakh")
        self.assertEqual(result.get('budget_range'), '₹12 lakh')

    def test_budget_lakh_no_symbol(self):
        result = self.extractor.extract("We have 15 lakh budget for this project")
        self.assertIn('budget_range', result)
        self.assertIn('lakh', result['budget_range'])

    def test_budget_crore(self):
        result = self.extractor.extract("Budget is ₹2 crore")
        self.assertIn('budget_range', result)
        self.assertIn('crore', result['budget_range'])

    def test_budget_L_shorthand(self):
        result = self.extractor.extract("Budget: 10L")
        self.assertIn('budget_range', result)
        self.assertIn('10L', result['budget_range'])

    def test_budget_usd(self):
        result = self.extractor.extract("We have around $50,000 for this")
        self.assertIn('budget_range', result)

    def test_phone_code_not_budget(self):
        """+91 must never be classified as a budget value."""
        result = self.extractor.extract("My number is +91 9876543210")
        self.assertNotIn('budget_range', result)

    def test_k_in_word_not_budget(self):
        """The letter 'k' inside a word (e.g. 'work', 'make') must not trigger budget."""
        result = self.extractor.extract("I work at a startup and make products")
        self.assertNotIn('budget_range', result)

    # --- Timeline ---

    def test_timeline_within_months(self):
        result = self.extractor.extract("We want to launch within 4 months")
        self.assertEqual(result.get('timeline'), '3_6_months')

    def test_timeline_next_quarter(self):
        result = self.extractor.extract("We plan to go live next quarter")
        self.assertEqual(result.get('timeline'), '3_6_months')

    def test_timeline_weeks(self):
        result = self.extractor.extract("We need this in 6 weeks")
        self.assertEqual(result.get('timeline'), '1_3_months')

    def test_timeline_n_months(self):
        result = self.extractor.extract("Timeline is about 3 months")
        self.assertEqual(result.get('timeline'), '1_3_months')

    def test_timeline_asap(self):
        result = self.extractor.extract("I need this asap, it is very urgent")
        self.assertEqual(result.get('timeline'), 'immediate')

    def test_timeline_q_notation(self):
        result = self.extractor.extract("We want to launch by Q3")
        self.assertEqual(result.get('timeline'), '3_6_months')

    def test_timeline_two_weeks(self):
        result = self.extractor.extract("I need this in 2 weeks")
        self.assertEqual(result.get('timeline'), '1_2_weeks')

    def test_timeline_exploratory(self):
        result = self.extractor.extract("We are exploring options and not sure about timeline")
        self.assertEqual(result.get('timeline'), 'exploratory')

    # --- Project Type ---

    def test_project_type_no_false_ai_from_substring(self):
        """'detail', 'email', 'paid' contain 'ai' as substring — must not match AI."""
        result = self.extractor.extract(
            "I need detailed design with email notifications for paid users."
        )
        pt = result.get('project_type')
        self.assertNotEqual(pt, 'ai_powered_solutions')

    def test_project_type_web_app(self):
        result = self.extractor.extract("We need a web app for managing bookings")
        self.assertEqual(result.get('project_type'), 'web_application_development')

    def test_project_type_mobile(self):
        result = self.extractor.extract("We need an iOS and Android app for delivery tracking")
        self.assertEqual(result.get('project_type'), 'mobile_application_development')

    def test_project_type_ecommerce(self):
        result = self.extractor.extract("We want to build an ecommerce store with Shopify")
        self.assertEqual(result.get('project_type'), 'ecommerce_development')

    def test_project_type_ai_word_boundary(self):
        result = self.extractor.extract("We want an AI-powered recommendation engine")
        self.assertEqual(result.get('project_type'), 'ai_powered_solutions')

    def test_project_type_mobile_beats_web(self):
        """Mobile has higher priority than web when both signals are present."""
        result = self.extractor.extract("We need a mobile web app for Android users")
        self.assertEqual(result.get('project_type'), 'mobile_application_development')

    def test_project_type_ecommerce_beats_web(self):
        """Ecommerce has higher priority than bare web signals."""
        result = self.extractor.extract("We want an ecommerce website")
        self.assertEqual(result.get('project_type'), 'ecommerce_development')

    def test_project_type_chatbot_is_ai(self):
        result = self.extractor.extract("We need a chatbot for customer support on our platform")
        self.assertEqual(result.get('project_type'), 'ai_powered_solutions')


# =========================================================================
# Name Extraction Tests
# =========================================================================

class NameExtractionTests(TestCase):
    """
    Root-cause fix: all name patterns now use re.IGNORECASE.
    Prior bug: "I am Chotu Singh." returned None because the lowercase
    trigger 'i am' never matched the capitalised input 'I am'.
    """

    def setUp(self):
        self.extractor = LeadExtractor()

    # --- Root-cause fix ---

    def test_name_i_am_capitalised(self):
        """'I am Chotu Singh.' — the primary reported failure; must now extract correctly."""
        result = self.extractor.extract("I am Chotu Singh.")
        self.assertEqual(result.get('full_name'), 'Chotu Singh')

    def test_name_i_am_lowercase_sentence(self):
        """'i am priya sharma' — all-lowercase input must also succeed."""
        result = self.extractor.extract("i am priya sharma, i need a web app for my business")
        self.assertEqual(result.get('full_name'), 'priya sharma')

    def test_name_my_name_is_capitalised(self):
        result = self.extractor.extract("My name is Rahul Kumar")
        self.assertEqual(result.get('full_name'), 'Rahul Kumar')

    def test_name_im_apostrophe(self):
        result = self.extractor.extract("I'm Anjali Singh and I need a mobile app")
        self.assertEqual(result.get('full_name'), 'Anjali Singh')

    # --- Expanded trigger phrases ---

    def test_name_myself(self):
        """'Myself Priya Sharma' — common Indian English introduction."""
        result = self.extractor.extract("Myself Priya Sharma, looking for a developer")
        self.assertEqual(result.get('full_name'), 'Priya Sharma')

    def test_name_this_is(self):
        result = self.extractor.extract("This is Rajan Mehta, I have a project idea")
        self.assertEqual(result.get('full_name'), 'Rajan Mehta')

    def test_name_you_can_call_me(self):
        result = self.extractor.extract("You can call me Vikram, I need a CRM system")
        self.assertEqual(result.get('full_name'), 'Vikram')

    def test_name_call_me(self):
        result = self.extractor.extract("Call me Raj, I want to discuss a project for my startup")
        self.assertEqual(result.get('full_name'), 'Raj')

    def test_name_hi_im(self):
        """'Hi, I'm Chotu' — greeting-prefixed introduction."""
        result = self.extractor.extract("Hi, I'm Chotu Kumar and I need a chatbot for support")
        self.assertEqual(result.get('full_name'), 'Chotu Kumar')

    def test_name_hey_this_is(self):
        result = self.extractor.extract("Hey, this is Rahul and I need help with a web project")
        self.assertEqual(result.get('full_name'), 'Rahul')

    def test_name_here_suffix(self):
        """'Rahul here' — name-first pattern at start of message."""
        result = self.extractor.extract("Rahul here, need a mobile app for my business")
        self.assertEqual(result.get('full_name'), 'Rahul')

    def test_name_speaking_suffix(self):
        result = self.extractor.extract("Priya Sharma speaking, I have a project requirement here")
        self.assertEqual(result.get('full_name'), 'Priya Sharma')

    def test_name_with_title_dr(self):
        """Titles (Dr., Mr., Ms.) should be stripped; only the name is captured."""
        result = self.extractor.extract("I am Dr. Rajan Verma and I need a healthtech platform")
        self.assertEqual(result.get('full_name'), 'Rajan Verma')

    def test_name_single_word(self):
        """Single-word names are valid."""
        result = self.extractor.extract("My name is Priya and I need a web app for my startup")
        self.assertEqual(result.get('full_name'), 'Priya')

    # --- Stop-word guard: must NOT extract verbs, articles, adjectives ---

    def test_name_stop_word_looking(self):
        """'I am looking for a developer' must not produce a name."""
        result = self.extractor.extract("I am looking for a web developer for my project")
        self.assertIsNone(result.get('full_name'))

    def test_name_stop_word_interested(self):
        result = self.extractor.extract("I am interested in your mobile app development services")
        self.assertIsNone(result.get('full_name'))

    def test_name_stop_word_based(self):
        result = self.extractor.extract("I am based in Mumbai and need a custom ERP system")
        self.assertIsNone(result.get('full_name'))


# =========================================================================
# Expanded Company Extraction Tests
# =========================================================================

class ExpandedCompanyTests(TestCase):

    def setUp(self):
        self.extractor = LeadExtractor()

    def test_company_work_at(self):
        """'I work at TechCorp' — new trigger pattern."""
        result = self.extractor.extract("I work at TechCorp and need a CRM system for our team")
        self.assertEqual(result.get('company_name'), 'TechCorp')

    def test_company_working_at(self):
        result = self.extractor.extract("Working at BrightEdge, we need a reporting dashboard")
        self.assertEqual(result.get('company_name'), 'BrightEdge')

    def test_company_work_for(self):
        result = self.extractor.extract("I work for Nexus Solutions and handle their tech stack")
        self.assertEqual(result.get('company_name'), 'Nexus Solutions')

    def test_company_represent(self):
        result = self.extractor.extract("I represent Quantum Ventures and need a web platform")
        self.assertEqual(result.get('company_name'), 'Quantum Ventures')

    def test_company_our_startup(self):
        result = self.extractor.extract("Our startup Nexus is building a logistics platform now")
        self.assertEqual(result.get('company_name'), 'Nexus')

    def test_company_our_firm(self):
        result = self.extractor.extract("Our firm Brightway needs an HR management system built")
        self.assertEqual(result.get('company_name'), 'Brightway')

    def test_company_our_agency(self):
        result = self.extractor.extract("Our agency Pixel Studio wants a portfolio website built")
        self.assertEqual(result.get('company_name'), 'Pixel Studio')

    def test_company_organisation_colon(self):
        result = self.extractor.extract("Organisation: GlobalEdge Technologies needs a platform")
        self.assertEqual(result.get('company_name'), 'GlobalEdge Technologies')

    def test_company_work_at_lowercase_rejected(self):
        """'I work at a startup' — 'a startup' starts lowercase; proper-noun guard rejects it."""
        result = self.extractor.extract("I work at a startup and need a mobile app urgently")
        self.assertIsNone(result.get('company_name'))

    def test_company_we_are_excited_no_false_positive(self):
        """'We are excited' — 'excited' starts lowercase; proper-noun guard rejects it."""
        result = self.extractor.extract(
            "We are excited to explore your services for our next big project"
        )
        self.assertIsNone(result.get('company_name'))

    def test_company_from_city_no_false_positive(self):
        result = self.extractor.extract("I'm from Hyderabad and looking for a developer")
        self.assertIsNone(result.get('company_name'))


# =========================================================================
# Additional Project Type and Industry Tests
# =========================================================================

class AdditionalProjectTypeTests(TestCase):

    def setUp(self):
        self.extractor = LeadExtractor()

    def test_project_type_inventory_management(self):
        """'inventory management' maps to custom_software_development."""
        result = self.extractor.extract(
            "We need an inventory management system with barcode scanning and reporting"
        )
        self.assertEqual(result.get('project_type'), 'custom_software_development')

    def test_project_type_erp(self):
        result = self.extractor.extract("We want to build an ERP system for our factory floor")
        self.assertEqual(result.get('project_type'), 'custom_software_development')

    def test_project_type_flutter(self):
        result = self.extractor.extract("We need a Flutter app for both iOS and Android users")
        self.assertEqual(result.get('project_type'), 'mobile_application_development')

    def test_project_type_online_store(self):
        result = self.extractor.extract("We want to build an online store for our clothing brand")
        self.assertEqual(result.get('project_type'), 'ecommerce_development')

    def test_project_type_ai_powered_phrase(self):
        result = self.extractor.extract("We need an AI-powered fraud detection system for banking")
        self.assertEqual(result.get('project_type'), 'ai_powered_solutions')

    def test_project_type_machine_learning(self):
        result = self.extractor.extract(
            "We want machine learning models to predict customer churn accurately"
        )
        self.assertEqual(result.get('project_type'), 'ai_powered_solutions')

    def test_project_type_figma_prototype(self):
        result = self.extractor.extract("We need Figma designs and a prototype for our mobile app")
        self.assertEqual(result.get('project_type'), 'mobile_application_development')

    def test_project_type_workflow_automation(self):
        result = self.extractor.extract(
            "We need workflow automation for our approval processes and reporting"
        )
        self.assertEqual(result.get('project_type'), 'custom_software_development')

    def test_industry_hospital(self):
        result = self.extractor.extract("We run a hospital and need a patient management system")
        self.assertEqual(result.get('industry'), 'healthtech')

    def test_industry_logistics(self):
        result = self.extractor.extract(
            "We are in logistics and need real-time shipment tracking software"
        )
        self.assertEqual(result.get('industry'), 'logistics')

    def test_industry_real_estate(self):
        result = self.extractor.extract(
            "We are a real estate company looking for a property listing platform"
        )
        self.assertEqual(result.get('industry'), 'real_estate')

    def test_industry_fintech(self):
        result = self.extractor.extract("We are a fintech startup building a payment gateway")
        self.assertEqual(result.get('industry'), 'fintech')
