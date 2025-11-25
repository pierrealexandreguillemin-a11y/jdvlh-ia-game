"""
Content Filter for JDVLH IA Game - Teen Safety (PEGI 16)

Based on French PEGI classification standards:
- Target: PEGI 16 (teens 16+ years)
- Violence: Realistic violence allowed, extreme gore filtered
- Language: Strong profanity allowed, extreme sexual insults filtered
- Fear: Intense horror allowed
- Drugs: Tobacco/alcohol references allowed
- Sex: Sexual innuendo allowed, explicit content filtered

Sources:
- https://pegi.info/fr
- https://cerjep.fr/classification-des-jeux-video-par-age-et-descripteurs/
- https://www.interieur.gouv.fr/ (jeux-video-choisissez-sereinement-avec-pegi)
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class ContentCategory(Enum):
    """PEGI content descriptor categories"""

    VIOLENCE = "violence"
    LANGUAGE = "language"
    FEAR = "fear"
    DRUGS = "drugs"
    SEX = "sex"
    DISCRIMINATION = "discrimination"
    GAMBLING = "gambling"


class Severity(Enum):
    """Content severity levels mapped to PEGI ratings"""

    SAFE = 0  # PEGI 3 - All ages
    MILD = 1  # PEGI 7 - Mild content (our target)
    MODERATE = 2  # PEGI 12 - Would filter
    HIGH = 3  # PEGI 16 - Must filter
    EXTREME = 4  # PEGI 18 - Must filter


@dataclass
class FilterResult:
    """Result of content filtering"""

    is_safe: bool
    original_text: str
    filtered_text: str
    violations: List[Dict] = field(default_factory=list)
    severity: Severity = Severity.SAFE

    def to_dict(self) -> Dict:
        return {
            "is_safe": self.is_safe,
            "filtered_text": self.filtered_text,
            "violation_count": len(self.violations),
            "severity": self.severity.name,
            "categories": list(set(v["category"] for v in self.violations)),
        }


class ContentFilter:
    """
    Multi-layer content filter for teen safety (PEGI 16 compliance)

    Filters:
    1. Input (player choices) - prevent prompt injection & inappropriate input
    2. Output (AI responses) - ensure appropriate narrative content

    Based on French PEGI 16 standards:
    - Realistic violence OK, extreme torture/mutilation filtered
    - Strong profanity OK, extreme sexual insults filtered
    - Horror and intense fear OK
    - Alcohol/tobacco references OK
    - Sexual innuendo OK, explicit pornographic content filtered
    - Discrimination always filtered
    """

    def __init__(self, target_age: int = 16, strict_mode: bool = True):
        """
        Initialize content filter

        Args:
            target_age: Target audience age (default 10)
            strict_mode: If True, err on side of caution
        """
        self.target_age = target_age
        self.strict_mode = strict_mode
        self._init_patterns()
        self._init_word_lists()

    def _init_patterns(self):
        """Initialize regex patterns for detection - PEGI 16 (permissive)"""

        # PEGI 16: Violence réaliste OK, torture/mutilation extrême filtrée
        self.violence_patterns = [
            # Extreme torture/mutilation only (PEGI 18)
            r"\b(tortur\w*.{0,20}(détail|longuement|lentement))\b",
            r"\b(évisc\w*.{0,10}(vivant|conscient))\b",
            r"\b(écorch\w*.{0,10}vif)\b",
            # Snuff/real violence glorification
            r"\b(snuff|gore.{0,10}réel)\b",
        ]

        # PEGI 16: Grossièretés OK, insultes sexuelles extrêmes filtrées
        self.language_patterns = [
            # Only extreme degrading sexual insults (PEGI 18)
            r"\b(pédophil\w*|viole?r?.{0,10}(enfant|mineur))\b",
        ]

        # PEGI 16: Horreur intense OK - rien à filtrer
        self.fear_patterns = []

        # PEGI 16: Références alcool/drogues OK, glorification filtrée
        self.drugs_patterns = [
            # Only drug use glorification/instructions (PEGI 18)
            r"\b(inject\w*.{0,15}(héroïne|drogue))\b",
            r"\b(comment.{0,10}(fabriquer|produire).{0,10}drogue)\b",
        ]

        # PEGI 16: Insinuations OK, pornographie explicite filtrée
        self.sex_patterns = [
            # Explicit pornographic content only (PEGI 18)
            r"\b(pornographi\w*|porno)\b",
            r"\b(pénis|vagin|orgasme|éjacul\w*|sodomie)\b",
            r"\b(porn|xxx|hardcore)\b",
            r"\b(pénétr\w*.{0,10}(sexuel|vagin|anal))\b",
        ]

        # PEGI 16+: Discrimination TOUJOURS filtrée
        self.discrimination_patterns = [
            r"\b(racis\w*|nazi\w*|fascis\w*|hitler)\b",
            r"\b(nègre|bougnoule|youpin|chinetoque)\b",
            r"\b(homophob\w*|pédé|gouine|tapette)\b",
            r"\b(antisémit\w*|xénophob\w*)\b",
        ]

        # Compile all patterns
        self._compiled_patterns = {
            ContentCategory.VIOLENCE: [
                re.compile(p, re.IGNORECASE) for p in self.violence_patterns
            ],
            ContentCategory.LANGUAGE: [
                re.compile(p, re.IGNORECASE) for p in self.language_patterns
            ],
            ContentCategory.FEAR: [
                re.compile(p, re.IGNORECASE) for p in self.fear_patterns
            ],
            ContentCategory.DRUGS: [
                re.compile(p, re.IGNORECASE) for p in self.drugs_patterns
            ],
            ContentCategory.SEX: [
                re.compile(p, re.IGNORECASE) for p in self.sex_patterns
            ],
            ContentCategory.DISCRIMINATION: [
                re.compile(p, re.IGNORECASE) for p in self.discrimination_patterns
            ],
        }

    def _init_word_lists(self):
        """Initialize word lists for fast lookup - PEGI 16 (permissive)"""

        # Blacklist: Only PEGI 18 / illegal content
        self.blacklist: Set[str] = {
            # Extreme illegal content
            "pédophile",
            "pédophilie",
            # Explicit pornography terms
            "pornographique",
            "porno",
            "xxx",
            # Discrimination (always blocked)
            "nazi",
            "hitler",
            "nègre",
            "bougnoule",
            "youpin",
        }

        # Graylist: Not used for PEGI 16 (most content allowed)
        self.graylist: Set[str] = set()

        # Whitelist: Not needed for PEGI 16 (most content allowed)
        self.whitelist: Set[str] = set()

        # Safe replacements for filtered content (only for PEGI 18 content)
        self.safe_replacements = {
            # Discrimination replacements
            "nazi": "ennemi",
            "hitler": "tyran",
            # Explicit content replacements
            "pornographique": "inapproprié",
            "porno": "contenu adulte",
        }

    def filter_input(self, text: str) -> FilterResult:
        """
        Filter player input before sending to AI

        This prevents:
        - Prompt injection attempts
        - Inappropriate requests
        - Content that could lead AI to generate unsafe responses

        Args:
            text: Player's input/choice

        Returns:
            FilterResult with sanitized text
        """
        if not text or not text.strip():
            return FilterResult(
                is_safe=True,
                original_text=text,
                filtered_text=text,
                severity=Severity.SAFE,
            )

        violations = []
        filtered_text = text
        max_severity = Severity.SAFE

        # Check for prompt injection attempts
        injection_patterns = [
            r"ignore.*instructions",
            r"oublie.*règles",
            r"tu es maintenant",
            r"nouveau.*rôle",
            r"système.*prompt",
            r"</?(system|user|assistant)",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(
                    {
                        "category": "INJECTION",
                        "pattern": pattern,
                        "severity": Severity.EXTREME.name,
                    }
                )
                max_severity = Severity.EXTREME
                # Replace entire input for injection attempts
                filtered_text = "Je continue mon aventure."

        # If injection detected, return immediately
        if max_severity == Severity.EXTREME:
            logger.warning(f"Prompt injection attempt blocked: {text[:50]}...")
            return FilterResult(
                is_safe=False,
                original_text=text,
                filtered_text=filtered_text,
                violations=violations,
                severity=max_severity,
            )

        # Standard content filtering
        return self._filter_content(text, is_input=True)

    def filter_output(self, text: str) -> FilterResult:
        """
        Filter AI-generated content before showing to child

        This ensures:
        - PEGI 7 compliance
        - No inappropriate content slipped through
        - Safe narrative for children

        Args:
            text: AI-generated narrative text

        Returns:
            FilterResult with filtered text
        """
        if not text or not text.strip():
            return FilterResult(
                is_safe=True,
                original_text=text,
                filtered_text=text,
                severity=Severity.SAFE,
            )

        return self._filter_content(text, is_input=False)

    def _filter_content(self, text: str, is_input: bool = False) -> FilterResult:
        """
        Core content filtering logic

        Args:
            text: Text to filter
            is_input: True if filtering player input

        Returns:
            FilterResult
        """
        violations = []
        filtered_text = text
        max_severity = Severity.SAFE

        text_lower = text.lower()

        # Step 1: Check blacklist (fast lookup with word boundaries)
        for word in self.blacklist:
            # Use word boundary regex to avoid false positives (e.g., "ass" in "passage")
            pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
            if pattern.search(text_lower):
                # Check if it's actually in the whitelist context
                if not self._is_whitelisted_context(text_lower, word):
                    violations.append(
                        {
                            "category": "BLACKLIST",
                            "word": word,
                            "severity": Severity.HIGH.name,
                        }
                    )
                    max_severity = max(
                        max_severity, Severity.HIGH, key=lambda x: x.value
                    )

                    # Apply replacement if available
                    replacement = self.safe_replacements.get(word, "...")
                    filtered_text = pattern.sub(replacement, filtered_text)

        # Step 2: Check regex patterns by category
        # Categories that should NEVER be whitelisted by context
        never_whitelist = {
            ContentCategory.LANGUAGE,
            ContentCategory.SEX,
            ContentCategory.DISCRIMINATION,
            ContentCategory.DRUGS,
        }

        for category, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                for match in matches:
                    match_str = match if isinstance(match, str) else match[0]

                    # Skip if whitelisted (but never for certain categories)
                    if category not in never_whitelist:
                        if self._is_whitelisted_context(text_lower, match_str.lower()):
                            continue

                    severity = self._get_category_severity(category)
                    violations.append(
                        {
                            "category": category.value,
                            "match": match_str,
                            "pattern": pattern.pattern,
                            "severity": severity.name,
                        }
                    )
                    max_severity = max(max_severity, severity, key=lambda x: x.value)

                    # Apply safe replacement
                    replacement = self.safe_replacements.get(match_str.lower(), "...")
                    filtered_text = re.sub(
                        rf"\b{re.escape(match_str)}\b",
                        replacement,
                        filtered_text,
                        flags=re.IGNORECASE,
                    )

        # Step 3: Final safety check
        is_safe = max_severity.value <= Severity.MILD.value

        # If not safe and strict mode, use fallback
        if not is_safe and self.strict_mode:
            if is_input:
                filtered_text = "Je continue mon aventure prudemment."
            else:
                filtered_text = "L'aventure continue de manière paisible..."

        # Log violations for monitoring
        if violations:
            logger.info(
                f"Content filtered: {len(violations)} violations, severity={max_severity.name}"
            )

        return FilterResult(
            is_safe=is_safe,
            original_text=text,
            filtered_text=filtered_text,
            violations=violations,
            severity=max_severity,
        )

    def _is_whitelisted_context(self, text: str, word: str) -> bool:
        """
        Check if a word appears in a safe/whitelisted context

        For PEGI 16: Most content is allowed, only check for educational/historical context
        for discrimination terms.

        Args:
            text: Full text (lowercase)
            word: Word to check (lowercase)

        Returns:
            True if context is safe (educational/historical)
        """
        # For PEGI 16, only whitelist discrimination in educational context
        word_pos = text.find(word)
        if word_pos == -1:
            return False

        context_start = max(0, word_pos - 80)
        context_end = min(len(text), word_pos + len(word) + 80)
        context = text[context_start:context_end]

        # Educational/historical contexts for discrimination terms
        educational_contexts = [
            "histoire",
            "historique",
            "guerre mondiale",
            "leçon",
            "apprendre",
            "comprendre",
            "éviter",
            "combattre",
            "résistance",
            "libération",
        ]

        return any(ctx in context for ctx in educational_contexts)

    def _get_category_severity(self, category: ContentCategory) -> Severity:
        """
        Get default severity for a content category

        Based on PEGI 16 guidelines:
        - PEGI 16 allows: realistic violence, profanity, horror, drugs/alcohol refs
        - PEGI 16 filters: extreme torture, explicit porn, discrimination
        """
        severity_map = {
            ContentCategory.VIOLENCE: Severity.MODERATE,  # Only extreme torture
            ContentCategory.LANGUAGE: Severity.MILD,  # Most OK, extreme filtered
            ContentCategory.FEAR: Severity.SAFE,  # Horror allowed
            ContentCategory.DRUGS: Severity.MILD,  # Refs OK, glorification filtered
            ContentCategory.SEX: Severity.HIGH,  # Explicit porn filtered
            ContentCategory.DISCRIMINATION: Severity.EXTREME,  # Always filter
            ContentCategory.GAMBLING: Severity.SAFE,  # Allowed for PEGI 16
        }
        return severity_map.get(category, Severity.MILD)

    def is_safe(self, text: str) -> bool:
        """
        Quick check if text is safe (for backward compatibility)

        Args:
            text: Text to check

        Returns:
            True if safe for PEGI 7
        """
        result = self.filter_output(text)
        return result.is_safe

    def get_safe_text(self, text: str) -> str:
        """
        Get filtered safe version of text

        Args:
            text: Text to filter

        Returns:
            Safe/filtered text
        """
        result = self.filter_output(text)
        return result.filtered_text

    def validate_for_children(self, text: str) -> Tuple[bool, str, List[str]]:
        """
        Validate content is appropriate for children

        Returns:
            Tuple of (is_safe, filtered_text, list_of_issues)
        """
        result = self.filter_output(text)
        issues = [
            f"{v['category']}: {v.get('word') or v.get('match')}"
            for v in result.violations
        ]
        return result.is_safe, result.filtered_text, issues


# Singleton instance
_filter_instance: Optional[ContentFilter] = None


def get_content_filter(target_age: int = 16, strict_mode: bool = True) -> ContentFilter:
    """
    Get or create the global ContentFilter instance

    Args:
        target_age: Target audience age
        strict_mode: If True, err on side of caution

    Returns:
        ContentFilter instance
    """
    global _filter_instance
    if _filter_instance is None:
        _filter_instance = ContentFilter(target_age=target_age, strict_mode=strict_mode)
        logger.info(
            f"ContentFilter initialized: target_age={target_age}, strict={strict_mode}"
        )
    return _filter_instance


def reset_filter():
    """Reset the singleton filter (useful for testing)"""
    global _filter_instance
    _filter_instance = None
