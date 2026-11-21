import re
from typing import Dict, Any, List
from urllib.parse import urlparse


class SecurityService:
    """Detects phishing/scam shopping links, calculates granular seller trust, and gives payment safety advice."""

    # High-risk / suspicious TLDs common in Pakistani phishing campaigns
    SUSPICIOUS_TLDS = [".xyz", ".top", ".club", ".buzz", ".tk", ".cf", ".ga", ".gq", ".ml", ".icu", ".vip"]

    # Known legitimate stores
    TRUSTED_DOMAINS = ["daraz.pk", "amazon.com", "priceoye.pk", "telemart.pk", "yayvo.com"]

    def check_link_safety(self, url: str) -> Dict[str, Any]:
        """Examines URL for lookalike spoofing, urgent OTP lures, and unsafe domains."""
        reasons = []
        url_lower = url.lower().strip()
        parsed = urlparse(url if "://" in url else f"http://{url}")
        netloc = parsed.netloc or parsed.path.split("/")[0]

        # 1. IP address in URL check
        if re.search(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", netloc):
            reasons.append("URL contains a raw IP address instead of a genuine store domain.")

        # 2. Suspicious TLD check
        for tld in self.SUSPICIOUS_TLDS:
            if netloc.endswith(tld):
                reasons.append(f"Domain uses high-risk untrusted extension ({tld}).")
                break

        # 3. Lookalike spoofing checks (e.g. 'darraz.pk', 'amaz0n.com', 'daraz-promo.xyz')
        if "darraz" in netloc or "daraz-sale" in netloc or "daraz-pakistan" in netloc:
            reasons.append("Lookalike spoofing detected (impersonating Daraz).")
        if "amaz0n" in netloc or "amazon-discount" in netloc:
            reasons.append("Lookalike spoofing detected (impersonating Amazon).")

        # 4. Phishing urgency keywords
        path_lower = parsed.path.lower()
        if any(w in path_lower or w in netloc for w in ["urgent", "verify-otp", "card-verify", "bank-login", "prize-winner"]):
            reasons.append("Suspicious path asking for urgent payment or OTP verification.")

        is_safe = len(reasons) == 0
        risk_level = "safe" if is_safe else ("danger" if any("spoofing" in r or "IP address" in r for r in reasons) else "warning")

        if is_safe:
            recommendation = "Safe to visit. Genuine e-commerce URL."
        else:
            recommendation = "Khatra! Yeh link scam ya phishing ho sakta hai. Is par apni card details ya OTP hargiz share na karein."

        return {
            "url": url,
            "safe": is_safe,
            "risk_level": risk_level,
            "reasons": reasons,
            "recommendation": recommendation
        }

    def compute_seller_score(
        self,
        rating: float,
        orders_count: int,
        complaints_count: int,
        account_age_months: int,
        return_acceptance_rate: float
    ) -> Dict[str, Any]:
        """Calculates 0-100 Seller Trust Score based on verifiable metrics."""
        # Rating score (0-35 pts)
        score_rating = min(35.0, (rating / 5.0) * 35.0)

        # Orders volume score (0-25 pts)
        score_orders = min(25.0, (orders_count / 200.0) * 25.0)

        # Account age score (0-15 pts)
        score_age = min(15.0, (account_age_months / 12.0) * 15.0)

        # Return handling score (0-15 pts)
        score_returns = min(15.0, return_acceptance_rate * 15.0)

        # Complaint penalty (up to -20 pts)
        penalty = min(20.0, complaints_count * 4.0)

        total_score = max(5, min(100, int(score_rating + score_orders + score_age + score_returns - penalty)))

        reasons = []
        if rating >= 4.5:
            reasons.append(f"Aala customer rating ({rating}/5.0)")
        if orders_count > 100:
            reasons.append(f"Qabil-e-itmad sales volume ({orders_count}+ successful orders)")
        if account_age_months >= 12:
            reasons.append(f"Established seller account ({account_age_months} months old)")
        if complaints_count > 2:
            reasons.append(f"⚠️ {complaints_count} recent customer complaints reported")

        if total_score >= 80:
            verdict = "Trusted Seller"
            payment_advice = "Online Payment / Card / JazzCash bilkul safe hai."
        elif total_score >= 60:
            verdict = "Moderate Trust"
            payment_advice = "COD (Cash on Delivery) behtar option hai."
        else:
            verdict = "Low Trust / Risky"
            payment_advice = "Sirf COD select karein ya kisi certified Daraz Mall seller se khareedein."

        return {
            "trust_score": total_score,
            "verdict": verdict,
            "payment_advice": payment_advice,
            "reasons": reasons
        }


security_service = SecurityService()
