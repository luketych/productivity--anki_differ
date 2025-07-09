#!/usr/bin/env python3
"""
Text processing utilities for similarity calculations
Provides text normalization, cleaning, and preprocessing functions
"""

import re
import html
from typing import Optional, List, Dict, Any
from enum import Enum


class ContentType(Enum):
    """Types of content that can be processed"""
    PLAIN_TEXT = "plain_text"
    HTML = "html"
    MARKDOWN = "markdown"
    CLOZE = "cloze"  # Anki cloze deletion format
    MIXED = "mixed"


class TextProcessor:
    """Main text processing class for similarity calculations"""
    
    def __init__(self, 
                 case_sensitive: bool = False,
                 ignore_html: bool = True,
                 ignore_punctuation: bool = True,
                 normalize_whitespace: bool = True,
                 decode_html_entities: bool = True):
        """Initialize text processor with configuration"""
        self.case_sensitive = case_sensitive
        self.ignore_html = ignore_html
        self.ignore_punctuation = ignore_punctuation
        self.normalize_whitespace = normalize_whitespace
        self.decode_html_entities = decode_html_entities
        
        # Pre-compile regex patterns for better performance
        self._html_tag_pattern = re.compile(r'<[^>]+>')
        self._punctuation_pattern = re.compile(r'[^\w\s]')
        self._whitespace_pattern = re.compile(r'\s+')
        self._cloze_pattern = re.compile(r'\{\{c\d+::(.*?)(?:::.*?)?\}\}')
        self._anki_field_pattern = re.compile(r'\{\{[^}]+\}\}')
    
    def process_text(self, text: str, content_type: ContentType = ContentType.MIXED) -> str:
        """Process text according to configuration and content type"""
        if not text:
            return ""
        
        processed = text
        
        # Decode HTML entities first
        if self.decode_html_entities:
            processed = html.unescape(processed)
        
        # Handle specific content types
        if content_type == ContentType.HTML or content_type == ContentType.MIXED:
            processed = self._process_html_content(processed)
        
        if content_type == ContentType.CLOZE or content_type == ContentType.MIXED:
            processed = self._process_cloze_content(processed)
        
        if content_type == ContentType.MARKDOWN or content_type == ContentType.MIXED:
            processed = self._process_markdown_content(processed)
        
        # Remove HTML tags if configured
        if self.ignore_html:
            processed = self._html_tag_pattern.sub(' ', processed)
        
        # Remove punctuation if configured
        if self.ignore_punctuation:
            processed = self._punctuation_pattern.sub('', processed)
        
        # Handle case sensitivity
        if not self.case_sensitive:
            processed = processed.lower()
        
        # Normalize whitespace
        if self.normalize_whitespace:
            processed = self._whitespace_pattern.sub(' ', processed).strip()
        
        return processed
    
    def detect_content_type(self, text: str) -> ContentType:
        """Detect the likely content type of the text"""
        if not text:
            return ContentType.PLAIN_TEXT
        
        has_html = bool(self._html_tag_pattern.search(text))
        has_cloze = bool(self._cloze_pattern.search(text))
        has_markdown = self._has_markdown_syntax(text)
        
        if has_cloze:
            return ContentType.CLOZE
        elif has_html and has_markdown:
            return ContentType.MIXED
        elif has_html:
            return ContentType.HTML
        elif has_markdown:
            return ContentType.MARKDOWN
        else:
            return ContentType.PLAIN_TEXT
    
    def _process_html_content(self, text: str) -> str:
        """Process HTML-specific content"""
        # Convert common HTML entities to text equivalents
        html_replacements = {
            '&nbsp;': ' ',
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            '&#39;': "'",
            '<br>': ' ',
            '<br/>': ' ',
            '<br />': ' ',
            '<p>': ' ',
            '</p>': ' ',
            '<div>': ' ',
            '</div>': ' ',
            '<b>': ' ',
            '</b>': ' ',
            '<i>': ' ',
            '</i>': ' ',
            '<u>': ' ',
            '</u>': ' ',
            '<strong>': ' ',
            '</strong>': ' ',
            '<em>': ' ',
            '</em>': ' ',
        }
        
        processed = text
        for entity, replacement in html_replacements.items():
            processed = processed.replace(entity, replacement)
        
        return processed
    
    def _process_cloze_content(self, text: str) -> str:
        """Process Anki cloze deletion content"""
        # Extract content from cloze deletions: {{c1::answer::hint}} -> answer
        processed = self._cloze_pattern.sub(r'\1', text)
        
        # Remove remaining Anki field references
        processed = self._anki_field_pattern.sub('', processed)
        
        return processed
    
    def _process_markdown_content(self, text: str) -> str:
        """Process markdown-specific content"""
        # Remove markdown formatting but preserve content
        markdown_patterns = [
            (r'\*\*(.*?)\*\*', r'\1'),  # Bold
            (r'\*(.*?)\*', r'\1'),      # Italic
            (r'__(.*?)__', r'\1'),      # Bold
            (r'_(.*?)_', r'\1'),        # Italic
            (r'`(.*?)`', r'\1'),        # Inline code
            (r'```.*?```', ''),         # Code blocks
            (r'#+\s*', ''),             # Headers
            (r'>\s*', ''),              # Blockquotes
            (r'\[([^\]]+)\]\([^)]+\)', r'\1'),  # Links
            (r'!\[([^\]]*)\]\([^)]+\)', r'\1'), # Images
        ]
        
        processed = text
        for pattern, replacement in markdown_patterns:
            processed = re.sub(pattern, replacement, processed, flags=re.DOTALL)
        
        return processed
    
    def _has_markdown_syntax(self, text: str) -> bool:
        """Check if text contains markdown syntax"""
        markdown_indicators = [
            r'\*\*.*?\*\*',  # Bold
            r'\*.*?\*',      # Italic
            r'`.*?`',        # Inline code
            r'```',          # Code blocks
            r'^#+\s',        # Headers
            r'^\>\s',        # Blockquotes
            r'\[.*?\]\(.*?\)',  # Links
        ]
        
        for pattern in markdown_indicators:
            if re.search(pattern, text, re.MULTILINE):
                return True
        
        return False
    
    def extract_keywords(self, text: str, min_word_length: int = 3) -> List[str]:
        """Extract keywords from processed text"""
        processed = self.process_text(text)
        words = processed.split()
        
        # Filter out short words and common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her',
            'its', 'our', 'their'
        }
        
        keywords = []
        for word in words:
            if len(word) >= min_word_length and word.lower() not in stop_words:
                keywords.append(word)
        
        return keywords
    
    def get_text_stats(self, text: str) -> Dict[str, Any]:
        """Get statistics about the text"""
        processed = self.process_text(text)
        words = processed.split()
        
        return {
            'original_length': len(text),
            'processed_length': len(processed),
            'word_count': len(words),
            'unique_words': len(set(words)),
            'content_type': self.detect_content_type(text).value,
            'has_html': bool(self._html_tag_pattern.search(text)),
            'has_cloze': bool(self._cloze_pattern.search(text))
        }


def create_text_processor(case_sensitive: bool = False,
                         ignore_html: bool = True,
                         ignore_punctuation: bool = True) -> TextProcessor:
    """Create a text processor with common configuration"""
    return TextProcessor(
        case_sensitive=case_sensitive,
        ignore_html=ignore_html,
        ignore_punctuation=ignore_punctuation
    )


def preprocess_card_text(text: str, 
                        case_sensitive: bool = False,
                        ignore_html: bool = True,
                        ignore_punctuation: bool = True) -> str:
    """Convenience function to preprocess card text"""
    processor = create_text_processor(case_sensitive, ignore_html, ignore_punctuation)
    return processor.process_text(text, ContentType.MIXED)


def extract_card_keywords(text: str, min_word_length: int = 3) -> List[str]:
    """Convenience function to extract keywords from card text"""
    processor = create_text_processor()
    return processor.extract_keywords(text, min_word_length)