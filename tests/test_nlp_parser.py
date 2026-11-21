import pytest
from app.services.nlp_parser import nlp_parser


def test_roman_urdu_detection():
    query = "5000 se kam ke running shoes size 9"
    lang = nlp_parser.detect_language(query)
    assert lang == "roman_urdu"


def test_urdu_script_detection():
    query = "مجھے رننگ شوز چاہیے سائز 9"
    lang = nlp_parser.detect_language(query)
    assert lang == "urdu"


def test_english_detection():
    query = "running shoes under 5000 pkr size 9"
    lang = nlp_parser.detect_language(query)
    assert lang == "english"


def test_query_filter_parsing_roman_urdu():
    query = "5000 se kam ke running shoes size 9"
    parsed = nlp_parser.parse_query(query)

    assert parsed["max_price"] == 5000.0
    assert parsed["size"] == "9"
    assert "running shoes" in parsed["clean_query"]
    assert parsed["needs_clarification"] is False


def test_query_filter_parsing_k_notation():
    query = "Samsung phone under 60k"
    parsed = nlp_parser.parse_query(query)

    assert parsed["max_price"] == 60000.0
    assert parsed["brand"] == "Samsung"
    assert parsed["needs_clarification"] is False


def test_missing_size_clarification():
    query = "mujhe running shoes chahiye"
    parsed = nlp_parser.parse_query(query)

    assert parsed["needs_clarification"] is True
    assert "shoe size" in parsed["clarification_question"].lower()
