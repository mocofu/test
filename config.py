# -*- coding: utf-8 -*-
"""
NGワードフィルター設定
"""

DEFAULT_NG_WORDS = ["バカ", "アホ", "死ね", "きもい", "ウザい", "荒らし"]

def check_ng_words(text, ng_words=None):
    if ng_words is None:
        ng_words = DEFAULT_NG_WORDS
    
    found_words = []
    sanitized_text = text
    
    for word in ng_words:
        if word in text:
            found_words.append(word)
            sanitized_text = sanitized_text.replace(word, "*" * len(word))
            
    return len(found_words) > 0, found_words, sanitized_text