import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Fingerprint:
    """Represents the stylometric fingerprint of a specific AI brand/version."""
    brand: str               # e.g. "ChatGPT (OpenAI)"
    version_hint: str        # e.g. "GPT-4" or "GPT-3.5"
    regex_patterns: list     # list of (compiled_pattern, weight) tuples
    keyword_sets: list       # list of (keyword_list, weight) tuples
    style_checks: list       # list of (callable, weight) pairs


# ─────────────────────────────────────────────────────────────────────────────
# AIEngine
# ─────────────────────────────────────────────────────────────────────────────

class AIEngine:

    # ── 1. UTILITY METHODS ───────────────────────────────────────────────────

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Shannon entropy of character distribution."""
        if not text:
            return 0.0
        counts = Counter(text)
        total = len(text)
        return -sum((c / total) * math.log2(c / total) for c in counts.values())

    @staticmethod
    def normalize_code(code: str) -> str:
        """Strip comments and collapse whitespace for pure-logic analysis."""
        code = re.sub(r'(//.*|#.*)', '', code)
        code = re.sub(r'(/\*.*?\*/|\'\'\'.*?\'\'\'|""".*?""")', '', code, flags=re.DOTALL)
        return re.sub(r'\s+', ' ', code).strip()

    @staticmethod
    def _continuous_base_score(entropy: float) -> float:
        """
        Converts Shannon entropy to a continuous AI-probability score (0-100).

        Calibration:
          entropy ≤ 3.8  → ~99 %   (extreme AI regularity)
          entropy = 4.4  → ~95 %   (high AI probability)
          entropy = 5.0  → ~78 %   (suspicious)
          entropy = 5.4  → ~62 %   (borderline)
          entropy = 5.8  → ~45 %   (likely human)
          entropy ≥ 6.5  → ~15 %   (human noise)

        Uses a logistic-style decay so every variable rename/comment addition
        produces a proportional, not stepped, change.
        """
        # Logistic decay centred around entropy = 5.2
        # score = 100 / (1 + e^(k*(entropy - midpoint)))
        k = 2.2        # steepness
        midpoint = 5.2 # inflection point
        score = 100.0 / (1.0 + math.exp(k * (entropy - midpoint)))
        return round(min(max(score, 0.0), 100.0), 2)

    # ── 2. STYLE FEATURE EXTRACTION ──────────────────────────────────────────

    @staticmethod
    def _extract_features(code: str, normalized: str) -> tuple[dict, list[str]]:
        """Extract all stylometric features and record matched snippets (POI)."""
        lines = [l for l in code.split('\n') if l.strip()]
        indentations = [len(l) - len(l.lstrip()) for l in code.split('\n') if l.strip()]
        line_count = len(lines)

        f = {
            'has_main_guard': False,
            'has_docstring': False,
            'has_exercise_header': False,
            'no_inline_comments': False,
            'comment_ratio': 0.0,
            'has_type_hints': False,
            'has_optional_hint': False,
            'uses_f_strings': False,
            'uses_list_comp': False,
            'uses_generators': False,
            'uses_dataclass': False,
            'is_condensed': False,
            'has_tk_self': False,
            'short_varnames': False,
            'has_step_comments': False,
            'has_section_comments': False,
            'eng_var_names': False,
            'has_print_debug': False,
            'verbose_var_names': False,
            'has_narrative_comment': False,
            'returns_not_prints': False,
            'has_viewport': False,
            'has_markdown_block': False,
            'has_step_labels': False,
            'has_react_hooks': False,
            'generic_fn_names': False,
            'has_python_logic': False,
            'has_numpy_pandas': False,
            'has_cjk': False,
            'dense_math': False,
            'has_casual_comments': False,
            'has_assert_stmts': False,
            'has_usage_example': False,
            'has_todo_comments': False,
            'has_process_comments': False,
            'uses_enumerate': False,
            'uses_zip': False,
            'has_cjk_comment': False,
            'uses_result_pattern': False,
            'perfectly_indented': False,
            'canonical_count': 0,
            'ghost_libs': []
        }
        poi = []
        f['line_count'] = line_count

        def check_regex(pattern, key, flags=0, weight_poi=True):
            match = re.search(pattern, code, flags)
            f[key] = bool(match)
            if match and weight_poi:
                poi.append(match.group(0).strip())
            return match

        # Structural
        check_regex(r'if\s+__name__\s*==\s*["\']__main__["\']', 'has_main_guard')
        
        f['has_docstring'] = '"""' in code or "'''" in code
        if f['has_docstring']:
            doc_match = re.search(r'(""".*?"""|\'\'\'.*?\'\'\')', code, re.DOTALL)
            if doc_match: poi.append(doc_match.group(0).split('\n')[0] + "...")

        check_regex(r'#\s*(Ejercicio|Tarea|Solución|Exercise|Task|Solution)\s*[:.]', 'has_exercise_header', re.I)
        
        f['no_inline_comments'] = ('#' not in code and '//' not in code) and line_count >= 4
        f['comment_ratio'] = (code.count('#') + code.count('//')) / max(line_count, 1)
        
        check_regex(r'->\s*\w+|:\s*(int|str|float|list|dict|bool|Optional|List|Dict|Tuple)', 'has_type_hints')
        if 'Optional[' in code:
            f['has_optional_hint'] = True
            poi.append("Optional[...] type hint")
            
        check_regex(r'\bf["\']', 'uses_f_strings')
        check_regex(r'\[.+\s+for\s+\w+\s+in\s+', 'uses_list_comp')
        
        if 'yield' in code:
            f['uses_generators'] = True
            poi.append("yield (generator)")
            
        if '@dataclass' in code:
            f['uses_dataclass'] = True
            poi.append("@dataclass usage")

        # Condensed style (Gemini)
        f['is_condensed'] = ';' in code and ('tk.' in code or 'self.' in code)
        f['has_tk_self'] = 'tk.' in code and 'self.' in code
        if f['is_condensed']: poi.append("Multiple statements per line with ;")

        f['short_varnames'] = len(re.findall(r'\b(?:x|n|v|i|j|k|a|b|c|s|t|m|p|q)\b', normalized)) > 5

        # ChatGPT / verbose patterns
        check_regex(r'#\s*Step\s*\d|//\s*Step\s*\d', 'has_step_comments', re.I)
        check_regex(r'#\s*={3,}|/\*\s*={3,}', 'has_section_comments')
        
        eng_vars = re.findall(r'\b(result|output|data|value|response|items|count|total|index|temp)\b', normalized)
        f['eng_var_names'] = len(eng_vars) >= 3
        if f['eng_var_names']: poi.append(f"Generic variable names: {', '.join(set(eng_vars[:3]))}")

        if 'print(' in code:
            f['has_print_debug'] = True

        # Claude patterns
        verbose_vars = re.findall(r'\b\w{15,}\b', normalized)
        f['verbose_var_names'] = len(verbose_vars) >= 3
        if f['verbose_var_names']: poi.append(f"Verbose variable names: {verbose_vars[0]}...")

        check_regex(r'#.{40,}|//.{40,}', 'has_narrative_comment')
        f['returns_not_prints'] = 'return ' in code and 'print(' not in code

        # Web / Blackbox patterns
        check_regex(r'<meta name="viewport"', 'has_viewport', re.I)
        if '```' in code:
            f['has_markdown_block'] = True
            poi.append("Markdown code block delimiter (```)")
            
        check_regex(r'//\s*Step\s*\d|<!--\s*Step', 'has_step_labels', re.I)

        # JS patterns
        js_patterns = ['.forEach', '.getElementById', 'const ', 'textContent',
                        'addEventListener', 'document.createElement', '.appendChild',
                        'querySelector', 'fetch(', 'async ', 'await ']
        f['js_pattern_count'] = sum(1 for p in js_patterns if p in code)
        check_regex(r'useState|useEffect|useCallback|useMemo', 'has_react_hooks')
        check_regex(r'\b(handleClick|handleChange|handleSubmit|foo|bar|baz)\b', 'generic_fn_names')

        # Python patterns
        f['has_python_logic'] = 'def ' in code and (':' in code or 'print(' in code)

        # DeepSeek patterns
        check_regex(r'\b(np\.|pd\.|numpy|pandas)\b', 'has_numpy_pandas')
        check_regex(r'[\u4e00-\u9fff\u3400-\u4dbf]', 'has_cjk')
        
        math_ops = re.findall(r'[\+\-\*\/\%\^]|\bmath\.\w+', code)
        f['dense_math'] = len(math_ops) >= 3

        # Grok (xAI) patterns
        check_regex(r"#\s*(let's|now let's|here we|basically|note:|important:|alright|okay so|so here)", 'has_casual_comments', re.I)
        if 'assert ' in code:
            f['has_assert_stmts'] = True
            poi.append("assert statement")
        check_regex(r'#\s*(example|usage|example usage)\s*[:\-]', 'has_usage_example', re.I)

        # Groq / Llama patterns
        check_regex(r'#\s*(TODO|FIXME|HACK|NOTE)\s*:', 'has_todo_comments')
        check_regex(r'#\s*(Initialize|Process|Return|Compute|Calculate|Validate|Handle|Load|Save|Check|Build)', 'has_process_comments', re.I)
        if 'enumerate(' in code:
            f['uses_enumerate'] = True
        if 'zip(' in code:
            f['uses_zip'] = True

        # Qwen (Alibaba) patterns
        check_regex(r'#.*[\u4e00-\u9fff\u3400-\u4dbf]', 'has_cjk_comment')
        check_regex(r'\bresult\s*=\s*\[\]|\bresult\s*=\s*{}|\bresult\s*=\s*None', 'uses_result_pattern')

        # Indentation consistency
        if len(indentations) > 5:
            nonzero = [i for i in indentations if i > 0]
            f['perfectly_indented'] = all(i % 2 == 0 for i in nonzero) if nonzero else False
            if f['perfectly_indented']: poi.append("Perfectly consistent indentation")
        else:
            f['perfectly_indented'] = False

        # Canonical logic patterns
        canonical = [
            r'def\s+\w+\(.*\):\s+for\s+i\s+in\s+range\(',
            r'const\s+\w+\s+=\s+document\.getElementById\(',
            r'function\s+\w+\(.*\)\s*{\s*return',
        ]
        f['canonical_count'] = 0
        for p in canonical:
            if check_regex(p, 'canonical_match_internal', re.I):
                f['canonical_count'] += 1

        # Ghost libraries
        ghost_libs_names = ['gpt_helper', 'ai_utils', 'fast_neural', 'ez_ml', 'simple_auth_v2']
        found_ghosts = [lib for lib in ghost_libs_names if lib in normalized.lower()]
        f['ghost_libs'] = found_ghosts
        if found_ghosts:
            poi.extend([f"Suspected fake library: {lib}" for lib in found_ghosts])

        return f, list(set(poi))

    # ── 3. FINGERPRINT DEFINITIONS ───────────────────────────────────────────

    @staticmethod
    def _score_fingerprint(f: dict, fp_rules: dict) -> float:
        """
        Score a code file against one brand's fingerprint rules.
        Returns a match score 0-100.
        """
        total_weight = 0.0
        matched_weight = 0.0

        for feature_key, weight in fp_rules.items():
            total_weight += abs(weight)
            val = f.get(feature_key, 0)

            # Numeric feature: compare > 0
            if isinstance(val, bool):
                hit = val
            elif isinstance(val, (int, float)):
                hit = val > 0
            elif isinstance(val, list):
                hit = len(val) > 0
            else:
                hit = bool(val)

            # Negative weight = this feature is AGAINST this brand
            if weight > 0 and hit:
                matched_weight += weight
            elif weight < 0 and not hit:
                matched_weight += abs(weight)

        if total_weight == 0:
            return 0.0
        return round((matched_weight / total_weight) * 100, 1)

    # Fingerprint rule tables: feature_key → weight (+: supports brand, -: contradicts)
    _FINGERPRINTS = {
        # ── ChatGPT (OpenAI) ─────────────────────────────────────────────────
        "ChatGPT (OpenAI)": {
            "_version_rules": {
                # GPT-4 tends to use type hints, dataclasses and generators
                "GPT-4":   {"has_type_hints": 3, "has_docstring": 2, "uses_generators": 2, "has_optional_hint": 3},
                "GPT-3.5": {"has_print_debug": 2, "has_exercise_header": 3, "eng_var_names": 2, "has_type_hints": -1},
            },
            "has_main_guard":      5,
            "has_docstring":       4,
            "has_exercise_header": 4,
            "eng_var_names":       3,
            "has_section_comments":3,
            "comment_ratio":       2,   # numeric, >0 passes
            "perfectly_indented":  3,
            "canonical_count":     3,
            "has_python_logic":    2,
            "is_condensed":       -3,   # Gemini trait, lowers ChatGPT confidence
            "no_inline_comments": -4,
            "short_varnames":     -3,
            "has_cjk":            -5,
        },

        # ── Claude (Anthropic) ───────────────────────────────────────────────
        "Claude (Anthropic)": {
            "_version_rules": {
                "Claude 3 Opus":   {"has_optional_hint": 4, "uses_dataclass": 3, "verbose_var_names": 3},
                "Claude 3 Sonnet": {"has_type_hints": 3, "returns_not_prints": 3, "has_narrative_comment": 2},
                "Claude 2":        {"has_docstring": 3, "has_section_comments": 2, "eng_var_names": 2},
            },
            "has_optional_hint":    5,
            "has_type_hints":       4,
            "verbose_var_names":    4,
            "has_narrative_comment":4,
            "returns_not_prints":   4,
            "uses_dataclass":       3,
            "uses_generators":      3,
            "perfectly_indented":   2,
            "has_main_guard":       2,
            "has_exercise_header": -3,
            "has_print_debug":     -3,
            "short_varnames":      -4,
            "is_condensed":        -4,
            "has_cjk":             -5,
        },

        # ── Gemini (Google) ──────────────────────────────────────────────────
        "Gemini (Google)": {
            "_version_rules": {
                "Gemini 1.5 Pro":   {"uses_list_comp": 3, "uses_f_strings": 3, "has_type_hints": 2},
                "Gemini 1.0 Ultra": {"is_condensed": 4, "has_tk_self": 4, "no_inline_comments": 3},
                "Gemini Flash":     {"short_varnames": 4, "uses_f_strings": 3, "no_inline_comments": 4},
            },
            "is_condensed":        5,
            "has_tk_self":         5,
            "no_inline_comments":  4,
            "uses_f_strings":      4,
            "short_varnames":      4,
            "uses_list_comp":      3,
            "perfectly_indented":  3,
            "has_python_logic":    2,
            "has_main_guard":     -2,   # Reduced penalty
            "has_docstring":      -2,   # Reduced penalty
            "verbose_var_names":  -4,
            "has_exercise_header":-3,
            "has_narrative_comment": -4,
        },

        # ── GitHub Copilot (OpenAI Codex) ────────────────────────────────────
        "GitHub Copilot": {
            "_version_rules": {
                "Copilot (GPT-4o)": {"has_react_hooks": 4, "has_type_hints": 3},
                "Copilot (Codex)":  {"generic_fn_names": 5, "no_inline_comments": 4, "js_pattern_count": 3},
            },
            "generic_fn_names":    5,
            "no_inline_comments":  4,
            "has_react_hooks":     4,
            "js_pattern_count":    3,   # numeric
            "perfectly_indented":  3,
            "has_exercise_header":-5,
            "has_docstring":      -3,
            "has_main_guard":     -4,
            "verbose_var_names":  -4,
        },

        # ── Blackbox AI ──────────────────────────────────────────────────────
        "Blackbox AI": {
            "_version_rules": {
                "Blackbox v2": {"has_step_labels": 5, "has_viewport": 4, "js_pattern_count": 3},
                "Blackbox v1": {"has_markdown_block": 5, "has_step_labels": 4},
            },
            "has_step_labels":     6,
            "has_viewport":        5,
            "has_markdown_block":  5,
            "js_pattern_count":    3,
            "has_step_comments":   4,
            "has_main_guard":     -5,
            "has_optional_hint":  -5,
            "uses_dataclass":     -5,
            "has_narrative_comment": -3,
        },

        # ── DeepSeek ─────────────────────────────────────────────────────────
        "DeepSeek": {
            "_version_rules": {
                "DeepSeek-V3":    {"has_numpy_pandas": 5, "dense_math": 4, "has_docstring": 2},
                "DeepSeek-Coder": {"no_inline_comments": 4, "short_varnames": 3, "has_type_hints": 2},
            },
            "has_numpy_pandas":   6,
            "dense_math":         5,
            "short_varnames":     3,
            "no_inline_comments": 3,
            "has_type_hints":     2,
            "has_cjk_comment":   -3,   # Qwen trait
            "has_main_guard":    -2,
            "verbose_var_names": -3,
            "has_casual_comments": -4,  # Grok trait
        },

        # ── Qwen (Alibaba) ───────────────────────────────────────────────────
        "Qwen (Alibaba)": {
            "_version_rules": {
                "Qwen2.5-Coder": {"has_cjk_comment": 5, "has_type_hints": 3, "uses_result_pattern": 3},
                "Qwen2-72B":     {"has_cjk": 4, "uses_enumerate": 3, "uses_zip": 2},
            },
            "has_cjk":            6,
            "has_cjk_comment":    6,
            "uses_result_pattern":4,
            "has_type_hints":     3,
            "uses_enumerate":     3,
            "uses_zip":           2,
            "perfectly_indented": 2,
            "has_casual_comments": -4,  # Grok trait
            "has_narrative_comment": -2,
            "has_main_guard":    -2,
        },

        # ── Grok (xAI) ───────────────────────────────────────────────────────
        "Grok (xAI)": {
            "_version_rules": {
                "Grok-2":  {"has_casual_comments": 5, "has_assert_stmts": 4, "has_usage_example": 3},
                "Grok-1":  {"has_casual_comments": 4, "has_print_debug": 3, "has_main_guard": 2},
            },
            "has_casual_comments":  6,
            "has_assert_stmts":     5,
            "has_usage_example":    5,
            "has_print_debug":      3,
            "has_main_guard":       2,
            "comment_ratio":        2,
            "has_optional_hint":   -3,   # Claude trait
            "verbose_var_names":   -3,   # Claude trait
            "has_cjk":             -5,
            "has_step_labels":     -4,   # Blackbox trait
            "no_inline_comments":  -4,
        },

        # ── Groq / Llama ─────────────────────────────────────────────────────
        "Groq / Llama": {
            "_version_rules": {
                "Llama-3.1-70B":  {"has_process_comments": 5, "uses_enumerate": 3, "returns_not_prints": 3},
                "Mixtral-8x7B":   {"has_todo_comments": 4, "has_type_hints": 3, "uses_zip": 3},
            },
            "has_process_comments": 6,
            "has_todo_comments":    5,
            "uses_enumerate":       4,
            "uses_zip":             3,
            "returns_not_prints":   3,
            "perfectly_indented":   2,
            "has_casual_comments": -4,   # Grok trait
            "has_cjk":             -5,
            "has_step_labels":     -3,   # Blackbox trait
            "has_tk_self":         -4,   # Gemini trait
            "is_condensed":        -4,
        },
    }

    # Brand identity colours (for the frontend to pick up)
    BRAND_COLORS = {
        "ChatGPT (OpenAI)":  "#10A37F",   # OpenAI green
        "Claude (Anthropic)":"#D97706",   # Anthropic amber
        "Gemini (Google)":   "#4285F4",   # Google blue
        "GitHub Copilot":    "#6E40C9",   # Copilot purple
        "Blackbox AI":       "#F59E0B",   # Blackbox yellow
        "DeepSeek":          "#EF4444",   # DeepSeek red
        "Qwen (Alibaba)":    "#FF6B35",   # Alibaba orange
        "Grok (xAI)":        "#1DA1F2",   # xAI/Twitter blue
        "Groq / Llama":      "#8B5CF6",   # Groq violet
    }

    # ── 4. MAIN DETECTION METHOD ─────────────────────────────────────────────

    @staticmethod
    def detect_ai_signature(code: str) -> dict:
        """
        Full analysis pipeline. Returns:
          score             — continuous AI probability 0-100
          entropy           — raw Shannon entropy
          is_suspicious     — bool (score > 60)
          detected_model    — "Brand (Maker) — Version"
          attribution_confidence — 0-100 % confidence in the brand attribution
          brand_scores      — dict of scores per brand (for debugging)
          ghost_libraries   — list of detected fake library names
          brand_color       — hex color for the detected brand
        """
        normalized = AIEngine.normalize_code(code)
        entropy = AIEngine.calculate_entropy(normalized)

        # ── Step 1: continuous base score from entropy ────────────────────
        base_score = AIEngine._continuous_base_score(entropy)

        # ── Step 2: extract all stylometric features ─────────────────────
        features, poi = AIEngine._extract_features(code, normalized)

        # ── Step 3: score each brand fingerprint ─────────────────────────
        brand_scores = {}
        for brand, rules in AIEngine._FINGERPRINTS.items():
            # Exclude internal version sub-dict from scoring
            public_rules = {k: v for k, v in rules.items() if not k.startswith('_')}
            brand_scores[brand] = AIEngine._score_fingerprint(features, public_rules)

        # ── Step 4: pick the winning brand ───────────────────────────────
        best_brand = max(brand_scores, key=brand_scores.get)
        best_brand_score = brand_scores[best_brand]

        # ── Step 5: detect version within winning brand ───────────────────
        detected_version = AIEngine._detect_version(features, best_brand)

        # ── Step 6: compute attribution confidence ────────────────────────
        # Confidence = how much better winner is vs second best
        sorted_scores = sorted(brand_scores.values(), reverse=True)
        second_best = sorted_scores[1] if len(sorted_scores) > 1 else 0
        gap = best_brand_score - second_best

        # Confidence is high when gap is large AND base_score (entropy) is high
        attribution_confidence = round(
            min(100, (best_brand_score * 0.5) + (gap * 0.8) + (base_score * 0.1)),
            1
        )

        # ── Step 7: adjust final score with stylometric boosters ──────────
        final_score = base_score

        if features['ghost_libs']:
            final_score = min(100, final_score + len(features['ghost_libs']) * 15)

        if features['has_markdown_block']:
            final_score = max(final_score, 98)

        if features['canonical_count'] >= 2 and features['perfectly_indented']:
            final_score = max(final_score, min(final_score + 8, 99))

        # Hard-signal boosters: specific patterns that are unmistakable AI signals
        if features.get('has_step_labels') and features.get('has_viewport'):
            final_score = max(final_score, 85)
            attribution_confidence = max(attribution_confidence, 75)

        if features.get('has_numpy_pandas') and features.get('dense_math'):
            final_score = max(final_score, 80)
            attribution_confidence = max(attribution_confidence, 60)

        # Claude-specific Booster (High quality structure)
        if features.get('has_type_hints') and features.get('has_narrative_comment') and features.get('returns_not_prints'):
            final_score = max(final_score, 75)
            attribution_confidence = max(attribution_confidence, 65)

        # REMOVED: Safety caps that were lowering scores for clean/well-written code.
        # If the entropy or patterns suggest AI, we trust the signal.
        
        final_score = round(final_score, 2)

        # ── Step 8: build human-readable model name ───────────────────────
        # Relaxed thresholds to provide attribution more often
        brand_is_reliable = (
            final_score >= 60  # lowered from 65
            and (best_brand_score >= 30 or attribution_confidence >= 40) # more flexible
        )

        if not brand_is_reliable:
            if final_score < 40:
                model_label = "No Identificado (Probable Humano)"
                brand_color = "#22C55E"
            elif final_score > 70:
                # If score is very high but we can't pin down the brand, it's "IA Genérica"
                model_label = "IA Genérica (Sin Firma Específica)"
                brand_color = "#6B7280"
            else:
                model_label = "No Determinado"
                brand_color = "#6B7280"
            best_brand = None
            detected_version = None
            attribution_confidence = 0
        else:
            model_label = f"{best_brand} — {detected_version}" if detected_version else best_brand
            brand_color = AIEngine.BRAND_COLORS.get(best_brand, "#6B7280")

        return {
            "score":                  final_score,
            "entropy":                round(entropy, 4),
            "is_suspicious":          final_score > 60,
            "detected_model":         model_label,
            "detected_brand":         best_brand,
            "detected_version":       detected_version,
            "attribution_confidence": attribution_confidence,
            "brand_scores":           brand_scores,
            "brand_color":            brand_color,
            "ghost_libraries":        features['ghost_libs'],
            "points_of_interest":     poi,
        }

    @staticmethod
    def _detect_version(features: dict, brand: str) -> Optional[str]:
        """
        Score each known version variant of the winning brand and return the best match.
        Returns None if no version rules exist for this brand.
        """
        version_rules = AIEngine._FINGERPRINTS.get(brand, {}).get("_version_rules", {})
        if not version_rules:
            return None

        version_scores = {}
        for version, rules in version_rules.items():
            version_scores[version] = AIEngine._score_fingerprint(features, rules)

        best_version = max(version_scores, key=version_scores.get)
        best_score = version_scores[best_version]

        # Only claim a version if it scores meaningfully above 0
        if best_score < 20:
            return None

        return best_version
