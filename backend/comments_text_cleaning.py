import spacy
import emoji
import re
nlp = spacy.load('en_core_web_sm')


def remove_emoji(comment):

    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002702-\U000027B0"  # Dingbats
                               u"\U000024C2-\U0001F251" 
                               "]+", flags=re.UNICODE)

    comment = emoji_pattern.sub('', comment)
    return comment


def remove_stopwords(comment):
    comment = nlp(comment)
    return " ".join(token.text for token in comment if not token.is_stop)


def clean_comments_text(comments):
    cleaned_comments = []
    for items in comments:
        _id = list(items.keys())[0]
        comment = list(items.values())[0]
        comment = remove_emoji(comment)
        # comment = remove_stopwords(comment)
        items[_id] = comment
        cleaned_comments.append(items)
    return cleaned_comments
