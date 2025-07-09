#!/usr/bin/env python3
"""
Unit Tests for Core Anki Diff Functions
Tests individual functions in isolation with comprehensive scenarios
"""

import pytest
import os
import sys
import tempfile
import json
from unittest.mock import patch, mock_open

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.anki_differ.core.diff import (
    load_anki_export, 
    parse_anki_export
)
from src.anki_differ.web.app import (
    compare_exports, 
    generate_anki_export
)
from tests.fixtures.test_data_factory import TestDataFactory, DatasetSize, ScenarioType, TestFixtures

class TestLoadAnkiExport:
    """Test the load_anki_export function"""
    
    def test_load_valid_file(self):
        """Test loading a valid Anki export file"""
        test_content = "#separator:tab\n#html:true\nQuestion 1\tAnswer 1\nQuestion 2\tAnswer 2\n"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_path = f.name
        
        try:
            lines = load_anki_export(temp_path)
            assert len(lines) == 4
            assert lines[0].strip() == "#separator:tab"
            assert lines[1].strip() == "#html:true"
            assert "Question 1\tAnswer 1" in lines[2]
            assert "Question 2\tAnswer 2" in lines[3]
        finally:
            os.unlink(temp_path)
    
    def test_load_empty_file(self):
        """Test loading an empty file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            temp_path = f.name
        
        try:
            lines = load_anki_export(temp_path)
            assert lines == []
        finally:
            os.unlink(temp_path)
    
    def test_load_unicode_file(self):
        """Test loading file with Unicode characters"""
        test_content = "#separator:tab\n#html:true\n你好\t世界\nPython\tProgramming\n"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_path = f.name
        
        try:
            lines = load_anki_export(temp_path)
            assert "你好\t世界" in lines[2]
        finally:
            os.unlink(temp_path)
    
    def test_load_nonexistent_file(self):
        """Test loading a non-existent file"""
        with pytest.raises(FileNotFoundError):
            load_anki_export("/nonexistent/file.txt")
    
    def test_load_large_file(self):
        """Test loading a large file with many cards"""
        large_dataset = TestDataFactory.create_dataset(DatasetSize.LARGE, ScenarioType.NORMAL)
        file1_content, _ = TestDataFactory.dataset_to_anki_files(large_dataset)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(file1_content)
            temp_path = f.name
        
        try:
            lines = load_anki_export(temp_path)
            # Should have headers + all cards
            file1_total = len(large_dataset.identical_cards) + len(large_dataset.different_cards) + len(large_dataset.unique_file1)
            expected_lines = 2 + file1_total  # 2 headers + cards
            assert len(lines) >= expected_lines - 10  # Allow some variance
        finally:
            os.unlink(temp_path)

class TestParseAnkiExport:
    """Test the parse_anki_export function"""
    
    def test_parse_valid_export(self):
        """Test parsing valid Anki export format"""
        lines = [
            "#separator:tab\n",
            "#html:true\n", 
            "Question 1\tAnswer 1\n",
            "Question 2\tAnswer 2\n",
            "\n",  # Empty line should be ignored
            "Question 3\tAnswer 3\n"
        ]
        
        headers, cards = parse_anki_export(lines)
        
        assert headers == {"separator": "tab", "html": "true"}
        assert len(cards) == 3
        assert ("Question 1", "Answer 1") in cards
        assert ("Question 2", "Answer 2") in cards
        assert ("Question 3", "Answer 3") in cards
    
    def test_parse_malformed_multiline(self):
        """Test parsing malformed multi-line content"""
        lines = [
            "#separator:tab\n",
            "Question without answer\n",
            "Continuation of question\tAnswer\n",
            "Normal question\tNormal answer\n"
        ]
        
        headers, cards = parse_anki_export(lines)
        
        # Should handle malformed lines - exact behavior may vary
        assert len(cards) >= 1  # At least the normal question should be parsed
        assert ("Normal question", "Normal answer") in cards
    
    def test_parse_no_headers(self):
        """Test parsing export without headers"""
        lines = [
            "Question 1\tAnswer 1\n",
            "Question 2\tAnswer 2\n"
        ]
        
        headers, cards = parse_anki_export(lines)
        
        assert headers == {}
        assert len(cards) == 2
    
    def test_parse_empty_lines(self):
        """Test parsing with various empty lines"""
        lines = [
            "#separator:tab\n",
            "\n",
            "Question 1\tAnswer 1\n",
            "   \n",  # Whitespace only
            "Question 2\tAnswer 2\n",
            "\n"
        ]
        
        headers, cards = parse_anki_export(lines)
        
        assert len(cards) == 2
        assert ("Question 1", "Answer 1") in cards
        assert ("Question 2", "Answer 2") in cards
    
    def test_parse_special_characters(self):
        """Test parsing with special characters"""
        lines = [
            "#separator:tab\n",
            "Question with \"quotes\"\tAnswer with 'apostrophes'\n",
            "HTML <b>question</b>\t<i>HTML</i> answer\n",
            "Unicode 你好\tUnicode 世界\n"
        ]
        
        headers, cards = parse_anki_export(lines)
        
        assert len(cards) == 3
        assert any("quotes" in card[0] and "apostrophes" in card[1] for card in cards)
        assert any("<b>question</b>" in card[0] and "<i>HTML</i>" in card[1] for card in cards)
        assert any("你好" in card[0] and "世界" in card[1] for card in cards)

class TestCompareExports:
    """Test the compare_exports function"""
    
    def test_compare_identical_files(self):
        """Test comparing two identical files"""
        dataset = TestFixtures.tiny_normal()
        file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
        
        try:
            # Make files identical by using same content
            with open(file1_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(file2_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result = compare_exports(file1_path, file2_path)
            
            # Should have only identical cards
            assert result['stats']['different'] == 0
            assert result['stats']['only_file1'] == 0
            assert result['stats']['only_file2'] == 0
            assert result['stats']['identical'] > 0
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)
    
    def test_compare_different_files(self):
        """Test comparing files with different content"""
        dataset = TestFixtures.small_normal()
        file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
        
        try:
            result = compare_exports(file1_path, file2_path)
            
            # Verify expected structure
            assert 'identical_cards' in result
            assert 'different_cards' in result
            assert 'unique_file1' in result
            assert 'unique_file2' in result
            assert 'stats' in result
            
            # Check stats match actual data
            assert result['stats']['identical'] == len(result['identical_cards'])
            assert result['stats']['different'] == len(result['different_cards'])
            assert result['stats']['only_file1'] == len(result['unique_file1'])
            assert result['stats']['only_file2'] == len(result['unique_file2'])
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)
    
    def test_compare_no_overlap(self):
        """Test comparing files with no overlapping questions"""
        dataset = TestFixtures.no_overlap()
        file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
        
        try:
            result = compare_exports(file1_path, file2_path)
            
            # Should have no identical or different cards
            assert result['stats']['identical'] == 0
            assert result['stats']['different'] == 0
            assert result['stats']['only_file1'] > 0
            assert result['stats']['only_file2'] > 0
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)
    
    def test_compare_edge_cases(self):
        """Test comparing files with edge case content"""
        dataset = TestFixtures.edge_cases()
        file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
        
        try:
            result = compare_exports(file1_path, file2_path)
            
            # Should handle edge cases without errors
            assert 'stats' in result
            assert isinstance(result['identical_cards'], list)
            assert isinstance(result['different_cards'], list)
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)
    
    def test_compare_empty_files(self):
        """Test comparing empty files"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
            file1_path = f1.name
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
            file2_path = f2.name
        
        try:
            result = compare_exports(file1_path, file2_path)
            
            # Should handle empty files gracefully
            assert result['stats']['identical'] == 0
            assert result['stats']['different'] == 0
            assert result['stats']['only_file1'] == 0
            assert result['stats']['only_file2'] == 0
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)

class TestGenerateAnkiExport:
    """Test the generate_anki_export function"""
    
    def test_generate_basic_export(self):
        """Test generating a basic Anki export"""
        dataset = TestFixtures.small_normal()
        comparison_data = TestDataFactory.dataset_to_comparison_data(dataset)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_path = f.name
        
        try:
            generate_anki_export(comparison_data, output_path)
            
            # Verify file was created and has content
            assert os.path.exists(output_path)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should have headers
            assert "#separator:tab" in content
            assert "#html:true" in content
            
            # Should have tab-separated cards
            lines = content.strip().split('\n')
            card_lines = [line for line in lines if not line.startswith('#') and '\t' in line]
            assert len(card_lines) > 0
            
            # Each card line should have exactly one tab
            for line in card_lines:
                assert line.count('\t') == 1
                
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_generate_with_selections(self):
        """Test generating export with specific selections"""
        dataset = TestFixtures.small_normal()
        comparison_data = TestDataFactory.dataset_to_comparison_data(dataset)
        
        # Modify selections
        if comparison_data['different_cards']:
            comparison_data['different_cards'][0]['selected'] = 'file2'
        
        if comparison_data['unique_file1']:
            comparison_data['unique_file1'][0]['selected'] = False
        
        if comparison_data['unique_file2']:
            comparison_data['unique_file2'][0]['selected'] = False
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_path = f.name
        
        try:
            generate_anki_export(comparison_data, output_path)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should respect selections
            lines = content.strip().split('\n')
            card_lines = [line for line in lines if not line.startswith('#') and '\t' in line]
            
            # Should have fewer cards due to deselection
            total_selected = (
                len(comparison_data['identical_cards']) +
                len(comparison_data['different_cards']) +
                sum(1 for card in comparison_data['unique_file1'] if card['selected']) +
                sum(1 for card in comparison_data['unique_file2'] if card['selected'])
            )
            
            assert len(card_lines) == total_selected
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_generate_unicode_content(self):
        """Test generating export with Unicode content"""
        dataset = TestFixtures.edge_cases()
        comparison_data = TestDataFactory.dataset_to_comparison_data(dataset)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_path = f.name
        
        try:
            generate_anki_export(comparison_data, output_path)
            
            # Should handle Unicode without errors
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should preserve Unicode characters
            assert len(content) > 0
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_generate_empty_export(self):
        """Test generating export with no selected cards"""
        comparison_data = {
            "headers": {"separator": "tab", "html": "true"},
            "identical_cards": [],
            "different_cards": [],
            "unique_file1": [],
            "unique_file2": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_path = f.name
        
        try:
            generate_anki_export(comparison_data, output_path)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should have only headers
            lines = content.strip().split('\n')
            assert all(line.startswith('#') for line in lines if line.strip())
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

class TestIntegrationScenarios:
    """Test complete workflows combining multiple functions"""
    
    def test_full_workflow_normal_case(self):
        """Test complete workflow with normal data"""
        dataset = TestFixtures.small_normal()
        file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
        
        try:
            # 1. Load files
            lines1 = load_anki_export(file1_path)
            lines2 = load_anki_export(file2_path)
            
            assert len(lines1) > 0
            assert len(lines2) > 0
            
            # 2. Parse files
            headers1, cards1 = parse_anki_export(lines1)
            headers2, cards2 = parse_anki_export(lines2)
            
            assert len(cards1) > 0
            assert len(cards2) > 0
            
            # 3. Compare files
            comparison_data = compare_exports(file1_path, file2_path)
            
            assert 'stats' in comparison_data
            
            # 4. Generate export
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                output_path = f.name
            
            generate_anki_export(comparison_data, output_path)
            
            # 5. Verify output
            output_lines = load_anki_export(output_path)
            output_headers, output_cards = parse_anki_export(output_lines)
            
            assert len(output_cards) > 0
            assert output_headers == headers1  # Should preserve file1 headers
            
            os.unlink(output_path)
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)
    
    def test_full_workflow_edge_cases(self):
        """Test complete workflow with edge case data"""
        dataset = TestFixtures.edge_cases()
        file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
        
        try:
            # Complete workflow should handle edge cases without errors
            comparison_data = compare_exports(file1_path, file2_path)
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                output_path = f.name
            
            generate_anki_export(comparison_data, output_path)
            
            # Should complete without errors
            assert os.path.exists(output_path)
            
            os.unlink(output_path)
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)

if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v", "--tb=short"])