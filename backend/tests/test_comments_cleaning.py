import pytest
from backend.comments_text_cleaning import remove_emoji, remove_stopwords, clean_comments_text


def test_remove_emoji():
    raw_comment = "Hello! 😊 I love Python! 🐍❤"
    expected_result = "Hello! I love Python!"
    assert expected_result == remove_emoji(raw_comment)


def test_remove_stopwords():
    comment_with_stopwords = "This is a test comment with some stop words."
    expected_result = "test comment stop words ."
    assert expected_result == remove_stopwords(comment_with_stopwords)


def test_clean_comments_text():
    raw_comments = [
        "Hello! 😊 I love Python! 🐍❤️",
        "This is a test comment with some stop words."
    ]
    expected_results = [
        "Hello! I love Python!",
        "test comment stop words ."
    ]
    assert clean_comments_text(raw_comments) == expected_results
