import re
from typing import Dict, Any, Optional, Tuple


class NLPParser:
    """Parses natural-language and Roman Urdu shopping queries into structured filters."""

    # Roman Urdu indicator terms
    ROMAN_URDU_KEYWORDS = [
        "chahiye", "kam", "zyada", "ziada", "se", "tak", "sasta", "saste",
        "mehanga", "joote", "jootay", "wala", "wali", "wale", "karo", "dikhao",
        "batao", "mujhe", "mein", "pe", "par", "hai", "hain", "achi", "acha"
    ]

    COMMON_BRANDS = [
        "nike", "adidas", "samsung", "apple", "sony", "service", "ndure",
        "borjan", "bata", "outfitters", "champion", "xiaomi", "redmi", "infinix"
    ]

    COMMON_COLORS = [
        "black", "white", "blue", "red", "green", "grey", "gray", "kala",
        "neela", "safed", "chitta", "laal"
    ]

    def detect_language(self, text: str) -> str:
        """Detect whether input is Urdu script, Roman Urdu, or English."""
        # Check for Arabic / Urdu Unicode block (\u0600 - \u06FF)
        if re.search(r"[\u0600-\u06FF]", text):
            return "urdu"

        text_lower = text.lower()
        words = set(re.findall(r"\b\w+\b", text_lower))

        # Check for Roman Urdu markers
        if any(w in words for w in self.ROMAN_URDU_KEYWORDS):
            return "roman_urdu"

        # Default to English
        return "english"

    def parse_query(self, text: str) -> Dict[str, Any]:
        """Parse natural language query into structured filters and check if clarification needed."""
        lang = self.detect_language(text)
        text_lower = text.lower()

        max_price: Optional[float] = None
        min_price: Optional[float] = None
        size: Optional[str] = None
        color: Optional[str] = None
        brand: Optional[str] = None
        target_stores = []

        # 1. Price extraction (e.g., "5000 se kam", "under 60k", "50k tak", "Rs. 4000", "below 10000")
        # Match '60k', '50k' -> convert k to thousands
        k_price_match = re.search(r"(?:under|below|se kam|tak|max)?\s*(\d+(?:\.\d+)?)\s*k\b", text_lower)
        if k_price_match:
            val = float(k_price_match.group(1)) * 1000.0
            max_price = val

        if max_price is None:
            # Match standard digits: "5000 se kam", "under 5000", "less than 5000", "5000 tak"
            max_match = re.search(r"(?:under|below|less than|se kam|tak|max)\s*(?:rs\.?|pkr)?\s*(\d+)", text_lower)
            if not max_match:
                max_match = re.search(r"(\d+)\s*(?:rs\.?|pkr)?\s*(?:se kam|tak)", text_lower)
            if max_match:
                max_price = float(max_match.group(1))

        # Match min price: "above 3000", "3000 se zyada", "min 2000"
        min_match = re.search(r"(?:above|more than|se zyada|min)\s*(?:rs\.?|pkr)?\s*(\d+)", text_lower)
        if min_match:
            min_price = float(min_match.group(1))

        # 2. Size extraction (e.g., "size 9", "size 10", "size M", "size 42")
        size_match = re.search(r"\bsize\s*[:\s]?\s*([0-9]+|[smlxl]+)\b", text_lower)
        if size_match:
            size = size_match.group(1).upper()

        # 3. Brand extraction
        for b in self.COMMON_BRANDS:
            if re.search(rf"\b{b}\b", text_lower):
                brand = b.capitalize()
                break

        # 4. Color extraction
        for c in self.COMMON_COLORS:
            if re.search(rf"\b{c}\b", text_lower):
                if c == "kala":
                    color = "Black"
                elif c == "safed" or c == "chitta":
                    color = "White"
                elif c == "neela":
                    color = "Blue"
                elif c == "laal":
                    color = "Red"
                else:
                    color = c.capitalize()
                break

        # 5. Store extraction
        if "daraz" in text_lower:
            target_stores.append("daraz")
        if "amazon" in text_lower:
            target_stores.append("amazon")

        # 6. Clean query term (remove extracted metadata keywords)
        clean_text = text_lower
        remove_patterns = [
            r"\bunder\s+\d+k?\b", r"\b\d+k?\s*se\s*kam\b", r"\b\d+k?\s*tak\b",
            r"\bse\s*kam\b", r"\bbelow\s+\d+\b", r"\bsize\s*[0-9a-z]+\b",
            r"\bchahiye\b", r"\bdikhao\b", r"\bbatao\b", r"\bmujhe\b", r"\bke\b",
            r"\bka\b", r"\bki\b", r"\bmein\b", r"\bpe\b", r"\bpar\b"
        ]
        for pat in remove_patterns:
            clean_text = re.sub(pat, " ", clean_text)
        clean_query = " ".join(clean_text.split())

        # If query becomes empty or just noise, fallback to product type
        if not clean_query:
            clean_query = text

        # Check if critical attribute is missing (e.g. shoes without size)
        # Note: Do NOT require size clarification if the intent is setting an alert or reading reviews
        is_alert_or_review = any(w in text_lower for w in ["alert", "notify", "khabar", "price drop", "review", "reviews", "kaisay", "kesa"])
        needs_clarification = False
        clarification_question = None

        is_shoes = any(w in text_lower for w in ["shoes", "running shoes", "sneakers", "joote", "jootay"])
        if is_shoes and not size and not is_alert_or_review:
            needs_clarification = True
            if lang == "roman_urdu":
                clarification_question = "Aapka shoe size kya hai? (Jaise size 8, 9 ya 10)"
            elif lang == "urdu":
                clarification_question = "آپ کا جوتے کا سائز کیا ہے؟ (جیسے 8، 9 یا 10)"
            else:
                clarification_question = "What is your shoe size? (e.g. Size 8, 9, or 10)"

        return {
            "language": lang,
            "raw_text": text,
            "clean_query": clean_query,
            "max_price": max_price,
            "min_price": min_price,
            "size": size,
            "color": color,
            "brand": brand,
            "stores": target_stores or None,
            "needs_clarification": needs_clarification,
            "clarification_question": clarification_question
        }


nlp_parser = NLPParser()
