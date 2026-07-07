import re


class LeadExtractor:
    """
    Extracts structured lead fields from free-form conversation text.

    Design principles:
    - Email/phone:     deterministic regex (structurally invariant formats)
    - Name/company:    trigger-phrase anchored with re.IGNORECASE + proper-noun guard;
                       expanded to cover "I am Chotu Singh", "Myself Priya", "Rahul here", etc.
    - Budget:          requires an explicit budget/currency signal; phone country codes guarded
    - Timeline:        normalised bucket values (immediate / 1_2_weeks / 1_3_months /
                       3_6_months / 6_12_months / exploratory) for reliable CRM filtering
    - Project type:    word-boundary regex, priority-ordered; ecommerce is a first-class type;
                       AI requires \\bai\\b to prevent substring false positives on 'email',
                       'detail', 'paid', etc.
    - Industry:        exact keyword match on a controlled vocabulary
    - Requirements:    any substantive message (>7 words); write-once semantics in LeadService
    """

    # ------------------------------------------------------------------ #
    #  Industry                                                            #
    # ------------------------------------------------------------------ #
    _INDUSTRY_MAP = {
        'healthcare':   'healthtech',
        'health tech':  'healthtech',
        'healthtech':   'healthtech',
        'hospital':     'healthtech',
        'clinic':       'healthtech',
        'education':    'edtech',
        'edtech':       'edtech',
        'school':       'edtech',
        'university':   'edtech',
        'ecommerce':    'ecommerce',
        'e-commerce':   'ecommerce',
        'saas':         'saas',
        'marketplace':  'marketplaces',
        'enterprise':   'enterprise',
        'finance':      'finance',
        'banking':      'finance',
        'insurance':    'finance',
        'fintech':      'fintech',
        'retail':       'retail',
        'logistics':    'logistics',
        'supply chain': 'logistics',
        'real estate':  'real_estate',
        'property':     'real_estate',
        'travel':       'travel',
        'hospitality':  'hospitality',
        'restaurant':   'hospitality',
        'food':         'food_and_beverage',
        'manufacturing':'manufacturing',
        'media':        'media',
    }

    # ------------------------------------------------------------------ #
    #  Project Type — ordered by priority (first match wins)              #
    #  Uses word-boundary patterns to avoid substring false positives.    #
    # ------------------------------------------------------------------ #
    _PROJECT_TYPE_RULES = [
        ('mobile_application_development', [
            r'\bmobile\s+app\b',
            r'\bmobile\s+application\b',
            r'\bios\s+app\b',
            r'\bandroid\s+app\b',
            r'\bios\b',
            r'\bandroid\b',
            r'\bflutter\b',
            r'\breact\s+native\b',
            r'\bkotlin\b',
            r'\bswift\b',
            r'\bmobile\b',
        ]),
        ('ecommerce_development', [
            r'\becommerce\b',
            r'\be-commerce\b',
            r'\bonline\s+store\b',
            r'\bonline\s+shop\b',
            r'\bonline\s+marketplace\b',
            r'\bshopify\b',
            r'\bwoocommerce\b',
            r'\bmagento\b',
            r'\bselling\s+online\b',
            r'\bproduct\s+catalog\b',
            r'\bshopping\s+cart\b',
        ]),
        ('web_application_development', [
            # Bare 'web' excluded — requires compound phrases that clearly indicate a web project
            r'\bweb\s+app\b',
            r'\bweb\s+application\b',
            r'\bweb\s+portal\b',
            r'\bweb\s+platform\b',
            r'\bwebsite\b',
            r'\bweb-based\b',
            r'\bbrowser-based\b',
            r'\bresponsive\s+(?:web\s+)?design\b',
            r'\bpwa\b',
            r'\bspa\b',                        # single page application
        ]),
        ('custom_software_development', [
            r'\bcustom\s+software\b',
            r'\bcustom\s+solution\b',
            r'\bcustom\s+platform\b',
            r'\bcrm\b',
            r'\berp\b',
            r'\bdashboard\b',
            r'\banalytics\s+(?:tool|platform|dashboard)\b',
            r'\bbackend\b',
            r'\bapi\s+(?:development|integration)\b',
            r'\bsystem\s+integration\b',
            r'\bworkflow\s+automation\b',
            r'\binventory\s+(?:management|system)\b',
            r'\bhrms?\b',
            r'\bpayroll\b',
        ]),
        ('ai_powered_solutions', [
            # \bai\b (word boundary) prevents matching 'detail', 'email', 'paid', 'paid', etc.
            r'\bai[-\s]powered\b',
            r'\bartificial\s+intelligence\b',
            r'\bmachine\s+learning\b',
            r'\bdeep\s+learning\b',
            r'\bnlp\b',
            r'\bllm\b',
            r'\bgpt\b',
            r'\bchatbot\b',
            r'\bvoice\s+assistant\b',
            r'\bcomputer\s+vision\b',
            r'\bpredictive\s+analytics\b',
            r'\brecommendation\s+engine\b',
            r'\bai\b',
        ]),
        ('ui_ux_design', [
            r'\bui/ux\b',
            r'\bui\s+ux\b',
            r'\bui\s+design\b',
            r'\bux\s+design\b',
            r'\buser\s+interface\b',
            r'\buser\s+experience\b',
            r'\bdesign\s+system\b',
            r'\bwireframe\b',
            r'\bprototype\b',
            r'\bfigma\b',
            r'\bsketch\b',
            # Bare \bui\b / \bux\b last — only matches if nothing above matched
            r'\bui\b',
            r'\bux\b',
        ]),
    ]

    # ------------------------------------------------------------------ #
    #  Timeline — normalised buckets (first match wins)                   #
    # ------------------------------------------------------------------ #
    _TIMELINE_BUCKETS = [
        ('immediate', [
            r'\basap\b',
            r'\bimmediately\b',
            r'\burgent(?:ly)?\b',
            r'\bright\s+away\b',
            r'\bright\s+now\b',
            r'\btoday\b',
        ]),
        ('1_2_weeks', [
            r'\b[1-4]\s+weeks?\b',
            r'\bone\s+(?:to\s+)?(?:two\s+)?weeks?\b',
            r'\bcouple\s+(?:of\s+)?weeks?\b',
            r'\ba\s+(?:few\s+)?weeks?\b',
        ]),
        ('1_3_months', [
            r'\b1\s*[-\u2013to]+\s*3\s+months?\b',
            r'\bone\s+to\s+three\s+months?\b',
            r'\bwithin\s+(?:a\s+)?(?:one|1|two|2|three|3)\s+months?\b',
            r'\bcouple\s+(?:of\s+)?months?\b',
            r'\b[5-8]\s+weeks?\b',            # 5–8 weeks ≈ 1–2 months
            r'\b(?:1|2|3|one|two|three)\s+months?\b',
        ]),
        ('3_6_months', [
            r'\b3\s*[-\u2013to]+\s*6\s+months?\b',
            r'\bthree\s+to\s+six\s+months?\b',
            r'\bwithin\s+(?:4|5|6|four|five|six)\s+months?\b',
            r'\b(?:4|5|6|four|five|six)\s+months?\b',
            r'\bnext\s+quarter\b',
            r'\bthis\s+quarter\b',
            r'\bQ[1-4]\b',
            r'\b[9-9]\s+weeks?\b',            # 9+ weeks ≈ ~3 months
        ]),
        ('6_12_months', [
            r'\b6\s*[-\u2013to]+\s*12\s+months?\b',
            r'\b(?:7|8|9|10|11|12|seven|eight|nine|ten|eleven|twelve)\s+months?\b',
            r'\bby\s+(?:the\s+)?end\s+of\s+(?:the\s+)?year\b',
            r'\bby\s+year\s+end\b',
            r'\bthis\s+year\b',
            r'\bby\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\b',
        ]),
        ('exploratory', [
            r'\bexplor\w*\b',
            r'\bjust\s+(?:looking|browsing|checking)\b',
            r'\bno\s+(?:fixed\s+)?timeline\b',
            r'\bnot\s+sure\s+(?:about\s+(?:the\s+)?)?timeline\b',
        ]),
    ]

    # ------------------------------------------------------------------ #
    #  Full name — expanded trigger phrases + re.IGNORECASE               #
    #                                                                      #
    #  Root cause of "I am Chotu Singh" failure:                           #
    #  The previous pattern r"\b(?:my name is|i am|i'm)\s+([A-Z]..."      #
    #  was called WITHOUT re.IGNORECASE, so "i am" never matched "I am".  #
    #  All name patterns now use re.IGNORECASE via _extract_name().        #
    # ------------------------------------------------------------------ #
    # Capture group design: matches 1–3 words that are alpha/hyphen/apostrophe only.
    # The alternation stops BEFORE conjunctions (and, or, but, for, with, from, to)
    # so 'TechCorp and need a CRM' yields 'TechCorp', not 'TechCorp and need'.
    _NAME_WORD = r"[A-Za-z][A-Za-z'\-]{0,29}"
    _NAME_CAP_WORD = r"[A-Z][A-Za-z'\-]{1,29}"
    # Up to 3 words, each separated by a space that is NOT followed by a conjunction.
    # The negative lookahead (?! and\b | or\b | but\b | for\b | with\b | from\b | to\b | the\b)
    # is applied at each word boundary to prevent runaway captures.
    _NAME_CAPTURE = (
        r"([A-Za-z][A-Za-z'\-]{0,29}"
        r"(?:\s+(?!and\b|or\b|but\b|for\b|with\b|from\b|to\b|the\b|at\b|in\b|on\b|of\b|is\b|are\b|was\b|were\b)"
        r"[A-Za-z][A-Za-z'\-]{0,29}){0,2})"
    )

    _NAME_PATTERNS = [
        # Titles FIRST: "I am Dr. Rajan Verma" / "I'm Mr. Sharma"
        # Must precede the generic 'i am' pattern to prevent 'Dr' being captured.
        r"(?:i\s+am|i'm|my\s+name\s+is)\s+(?:dr\.?|mr\.?|ms\.?|mrs\.?|prof\.?)\s+" + _NAME_CAPTURE,

        # Standard introductions: "My name is Rahul", "I am Chotu Singh", "I'm Priya"
        r"(?:my name is|i am|i'm|i am called|i'm called)\s+"
        + _NAME_CAPTURE,

        # "Myself Priya Sharma" / "Myself Rahul"
        r"\bmyself\s+" + _NAME_CAPTURE,

        # "You can call me Rahul" / "Call me Raj"
        r"(?:you\s+can\s+call\s+me|call\s+me|please\s+call\s+me)\s+" + _NAME_CAPTURE,

        # "This is Rajan" / "This is Priya Sharma speaking"
        r"\bthis\s+is\s+" + _NAME_CAPTURE,

        # Greeting-prefixed: "Hi, I'm Chotu" / "Hey, this is Rahul"
        r"(?:hi|hey|hello)[,!\s]+(?:i'?m|i\s+am|this\s+is|myself)\s+" + _NAME_CAPTURE,

        # Name-first at sentence start: "Rahul here" / "Priya Sharma speaking"
        r"^([A-Z][A-Za-z'\-]{1,29}(?:\s+[A-Z][A-Za-z'\-]{1,29}){0,2})"
        r"\s+(?:here|speaking|this\s+side|this\s+is\s+me)\b",
    ]

    # Words that look like names in context but are not proper nouns.
    # Checked against the first extracted word only.
    _NAME_STOP_WORDS = frozenset({
        'a', 'an', 'the', 'not', 'no', 'from', 'at', 'in', 'on', 'for',
        'with', 'by', 'as', 'to', 'of', 'and', 'or', 'but',
        'just', 'also', 'very', 'really', 'here', 'there', 'so',
        'looking', 'working', 'trying', 'thinking', 'planning', 'exploring',
        'interested', 'based', 'reaching', 'contacting', 'writing', 'messaging',
        'hoping', 'building', 'developing', 'creating', 'starting', 'launching',
        'happy', 'excited', 'glad', 'sure', 'okay', 'ok', 'great', 'good',
        'hello', 'hi', 'hey', 'dear', 'sir', 'madam',
        'currently', 'recently', 'actually', 'basically', 'generally',
        'sorry', 'apologies', 'thanks', 'thank',
        # Title abbreviations — prevent 'Dr' or 'Mr' from being treated as a name
        'dr', 'mr', 'ms', 'mrs', 'prof',
    })

    # ------------------------------------------------------------------ #
    #  Company — trigger-phrase anchored + re.IGNORECASE                  #
    #  'from' excluded: "I'm from Hyderabad" → no false positive          #
    #  Bare 'at' excluded: "I was at a cafe" → no false positive          #
    # ------------------------------------------------------------------ #
    # Company name capture: 1–4 title-case/proper words, stops before conjunctions.
    _COMPANY_CAPTURE = (
        r"([A-Za-z0-9][A-Za-z0-9&.'\-]*"
        r"(?:\s+(?!and\b|or\b|but\b|for\b|with\b|from\b|to\b|the\b|at\b|in\b|on\b|of\b|is\b|are\b|was\b|were\b|needs?\b|wants?\b|has\b|have\b)"
        r"[A-Za-z0-9][A-Za-z0-9&.'\-]*){0,3})"
    )

    _COMPANY_PATTERNS = [
        # "My company is Nexus" / "Company is BrightEdge" / "Company: TechCo"
        r"(?:my\s+company\s+is|our\s+company\s+is|company\s+is|company:)\s*" + _COMPANY_CAPTURE,

        # "Organisation: Nexus Labs" / "Organization: TechVentures"
        r"(?:organisation|organization)[:\s]+" + _COMPANY_CAPTURE,

        # "I'm the Founder of Acme" / "I am the CEO at BrightEdge"
        r"(?:i'?m|i\s+am)\s+(?:the\s+)?"
        r"(?:founder|ceo|cto|coo|cpo|co-?founder|director|head|vp|president|owner|md|partner)\s+"
        r"(?:of|at)\s+" + _COMPANY_CAPTURE,

        # "We are Quantum Solutions" (requires proper noun guard to avoid "We are excited")
        r"\bwe\s+are\s+" + _COMPANY_CAPTURE,

        # "I work at TechCorp" / "working at BrightEdge" / "I work for Nexus"
        r"(?:i\s+work\s+at|working\s+at|i\s+work\s+for|working\s+for)\s+" + _COMPANY_CAPTURE,

        # "I represent Nexus Solutions" / "representing BrightEdge"
        r"(?:i\s+represent|representing)\s+" + _COMPANY_CAPTURE,

        # "Our startup Nexus" / "Our firm BrightEdge" / "Our agency TechCo"
        r"\bour\s+(?:startup|firm|agency|studio|venture|brand)\s+" + _COMPANY_CAPTURE,

        # "under the brand TechVentures" / "our brand name is TechCo"
        r"(?:our\s+brand(?:\s+name)?\s+is|brand:\s*|under\s+(?:the\s+)?brand\s+)" + _COMPANY_CAPTURE,
    ]

    # ------------------------------------------------------------------ #
    #  Budget                                                              #
    # ------------------------------------------------------------------ #
    _BUDGET_TRIGGER = re.compile(
        r'\b(?:budget|lakh|lakhs|crore|crores)\b|[$₹€£]|\b(?:inr|usd|gbp|eur)\b',
        re.IGNORECASE,
    )
    _BUDGET_PATTERNS = [
        r'₹\s*\d+(?:\.\d+)?\s*(?:lakh|crore)s?',                            # ₹12 lakh, ₹5 crore
        r'\d+(?:\.\d+)?\s*(?:lakh|crore)s?',                                 # 12 lakh, 2 crore
        r'(?:INR|USD|GBP|EUR)\s*\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:lakh|crore|[kKmM]))?',  # INR 10 lakh
        r'[$€£]\s*\d+(?:,\d+)*(?:\.\d+)?(?:[kKmM])?',                       # $50,000, $50K
        r'\b\d+(?:\.\d+)?[Ll]\b',                                            # 10L, 5.5L
        r'\b\d+(?:\.\d+)?[Kk]\b',                                           # 50K
    ]

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #
    def extract(self, text):
        extracted = {}
        text_lower = text.lower()

        # 1. Email — structurally invariant; no IGNORECASE needed
        email_match = re.search(r'[\w.\-+]+@[\w.\-]+\.\w{2,}', text)
        if email_match:
            extracted['email'] = email_match.group(0).lower()

        # 2. Phone — minimum 10 digits required to exclude short codes and country codes alone
        phone_match = re.search(
            r'(?<!\d)(?:\+\d{1,3}[\s\-]?)?(?:\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}|\d{10})',
            text,
        )
        if phone_match:
            digits = re.sub(r'\D', '', phone_match.group(0))
            if len(digits) >= 10:
                extracted['phone'] = phone_match.group(0).strip()

        # 3. Industry — exact keyword match
        for keyword, normalized in self._INDUSTRY_MAP.items():
            if keyword in text_lower:
                extracted['industry'] = normalized
                break

        # 4. Project type — word-boundary, priority-ordered
        for project_type, patterns in self._PROJECT_TYPE_RULES:
            if any(re.search(p, text, re.IGNORECASE) for p in patterns):
                extracted['project_type'] = project_type
                break

        # 5. Budget — requires explicit budget signal; phone country codes guarded
        budget = self._extract_budget(text)
        if budget:
            extracted['budget_range'] = budget

        # 6. Timeline — normalised bucket
        timeline = self._extract_timeline(text)
        if timeline:
            extracted['timeline'] = timeline

        # 7. Full name — expanded patterns, all case-insensitive
        name = self._extract_name(text)
        if name:
            extracted['full_name'] = name

        # 8. Company name — trigger-phrase anchored, case-insensitive
        company = self._extract_company(text)
        if company:
            extracted['company_name'] = company

        # 9. Requirements — any substantive message (>7 words)
        # LeadService write-once guard prevents overwriting already-captured data.
        if len(text.split()) > 7:
            extracted['requirements'] = text

        return extracted

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #
    def _extract_name(self, text):
        """
        Return the first plausible full name found, or None.

        All patterns use re.IGNORECASE so triggers like 'I am', 'I AM', 'i am'
        all match. Post-capture validation uses:
          - A stop-word guard on the first word (rejects verbs, articles, etc.)
          - A length sanity check
        The uppercase guard used for company names is NOT applied here because
        many mobile users type names in lowercase (e.g. "i am priya sharma").
        """
        for pattern in self._NAME_PATTERNS:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                name = m.group(1).strip().rstrip('.,!?')
                words = name.split()[:3]          # max 3 words (first / middle / last)
                name = ' '.join(words)
                if len(name) < 2:
                    continue
                first_word = words[0].lower()
                if first_word in self._NAME_STOP_WORDS:
                    continue
                return name
        return None

    def _extract_budget(self, text):
        """Return the first budget-like value, or None if no budget signal exists."""
        if not self._BUDGET_TRIGGER.search(text):
            return None
        for pattern in self._BUDGET_PATTERNS:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                # Guard 1: reject if immediately preceded by '+' (phone country code)
                preceding = text[max(0, m.start() - 2):m.start()].strip()
                if preceding.endswith('+'):
                    continue
                # Guard 2: reject if the numeric part is long enough to be a phone number
                digits = re.sub(r'\D', '', m.group(0))
                if len(digits) > 6:
                    continue
                return m.group(0).strip()
        return None

    def _extract_timeline(self, text):
        """Return a normalised timeline bucket string, or None."""
        for bucket, patterns in self._TIMELINE_BUCKETS:
            if any(re.search(p, text, re.IGNORECASE) for p in patterns):
                return bucket
        return None

    def _extract_company(self, text):
        """Return company name extracted via trigger-phrase anchoring, or None."""
        for pattern in self._COMPANY_PATTERNS:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                company = m.group(1).strip().rstrip('.,!?')
                # Limit to first 5 words to avoid runaway captures
                company = ' '.join(company.split()[:5])
                # Require the name to start with an uppercase letter (proper noun guard).
                # This prevents "We are excited" → company = "excited" (lowercase).
                if len(company) > 2 and company[0].isupper():
                    return company
        return None
