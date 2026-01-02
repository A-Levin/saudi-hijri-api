#!/usr/bin/env python3
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from scraper import arabic_num_to_int, MONTH_AR_TO_NUM, HIJRI_MONTHS_AR, HIJRI_MONTHS_EN, WEEKDAYS_AR
import re


class TestArabicNumToInt:
    def test_single_digit(self):
        assert arabic_num_to_int('٥') == 5

    def test_double_digit(self):
        assert arabic_num_to_int('١٤') == 14

    def test_year(self):
        assert arabic_num_to_int('١٤٤٧') == 1447

    def test_mixed_with_spaces(self):
        assert arabic_num_to_int('١٣ ') == 13


class TestDateParsing:
    def test_parse_header_14_rajab_1447(self):
        text = "السبت ١٤ رجب ١٤٤٧ - ٣ يناير ٢٠٢٦"
        weekdays_pattern = '|'.join(WEEKDAYS_AR)
        for month_ar, month_num in MONTH_AR_TO_NUM.items():
            header_pattern = rf'(?:{weekdays_pattern})\s*([٠-٩]+)\s*{month_ar}\s*([٠-٩]+)'
            match = re.search(header_pattern, text)
            if match and arabic_num_to_int(match.group(2)) > 1440:
                day = arabic_num_to_int(match.group(1))
                year = arabic_num_to_int(match.group(2))
                assert day == 14
                assert month_num == 7
                assert year == 1447
                return
        pytest.fail("Header date not found")

    def test_parse_14_rajab_1447(self):
        text = "السبت ١٤ رجب ١٤٤٧ - ٣ يناير ٢٠٢٦"
        for month_ar, month_num in MONTH_AR_TO_NUM.items():
            pattern = rf'([٠-٩]+)\s*{month_ar}\s*([٠-٩]+)'
            match = re.search(pattern, text)
            if match and arabic_num_to_int(match.group(2)) > 1440:
                day = arabic_num_to_int(match.group(1))
                year = arabic_num_to_int(match.group(2))
                assert day == 14
                assert month_num == 7
                assert year == 1447
                return
        pytest.fail("Date not found")

    def test_parse_13_rajab_1447(self):
        text = "الجمعة ١٣ رجب ١٤٤٧ - ٢ يناير ٢٠٢٦"
        for month_ar, month_num in MONTH_AR_TO_NUM.items():
            pattern = rf'([٠-٩]+)\s*{month_ar}\s*([٠-٩]+)'
            match = re.search(pattern, text)
            if match and arabic_num_to_int(match.group(2)) > 1440:
                day = arabic_num_to_int(match.group(1))
                year = arabic_num_to_int(match.group(2))
                assert day == 13
                assert month_num == 7
                assert year == 1447
                return
        pytest.fail("Date not found")

    def test_parse_1_muharram_1447(self):
        text = "١ محرم ١٤٤٧"
        for month_ar, month_num in MONTH_AR_TO_NUM.items():
            pattern = rf'([٠-٩]+)\s*{month_ar}\s*([٠-٩]+)'
            match = re.search(pattern, text)
            if match and arabic_num_to_int(match.group(2)) > 1440:
                day = arabic_num_to_int(match.group(1))
                year = arabic_num_to_int(match.group(2))
                assert day == 1
                assert month_num == 1
                assert year == 1447
                return
        pytest.fail("Date not found")


class TestJsonFallback:
    def test_parse_json_date(self):
        html = '{"date_hijri":"1447-07-14","other":"data"}'
        match = re.search(r'"date_hijri":"(\d{4})-(\d{2})-(\d{2})"', html)
        assert match is not None
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        assert year == 1447
        assert month == 7
        assert day == 14


class TestHistoryLogic:
    def test_new_day_adds_to_history(self):
        data = {
            'current': {
                'day': 13,
                'month': 7,
                'year': 1447
            },
            'history': [{'day': 13, 'month': 7, 'year': 1447}],
            'source': 'spa.gov.sa'
        }
        hijri = {'day': 14, 'month': 7, 'year': 1447}

        current = data.get('current')
        is_new_day = not current or current.get('day') != hijri['day'] or current.get('month') != hijri['month']

        assert is_new_day is True

    def test_same_day_no_duplicate(self):
        data = {
            'current': {
                'day': 14,
                'month': 7,
                'year': 1447
            },
            'history': [{'day': 14, 'month': 7, 'year': 1447}],
            'source': 'spa.gov.sa'
        }
        hijri = {'day': 14, 'month': 7, 'year': 1447}

        current = data.get('current')
        is_new_day = not current or current.get('day') != hijri['day'] or current.get('month') != hijri['month']

        assert is_new_day is False

    def test_new_month_adds_to_history(self):
        data = {
            'current': {
                'day': 30,
                'month': 6,
                'year': 1447
            },
            'history': [],
            'source': 'spa.gov.sa'
        }
        hijri = {'day': 1, 'month': 7, 'year': 1447}

        current = data.get('current')
        is_new_day = not current or current.get('day') != hijri['day'] or current.get('month') != hijri['month']

        assert is_new_day is True


class TestMonthMappings:
    def test_all_months_mapped(self):
        assert len(HIJRI_MONTHS_AR) == 12
        assert len(HIJRI_MONTHS_EN) == 12
        assert len(MONTH_AR_TO_NUM) == 12

    def test_rajab_is_month_7(self):
        assert HIJRI_MONTHS_AR[7] == 'رجب'
        assert HIJRI_MONTHS_EN[7] == 'Rajab'
        assert MONTH_AR_TO_NUM['رجب'] == 7

    def test_ramadan_is_month_9(self):
        assert HIJRI_MONTHS_AR[9] == 'رمضان'
        assert HIJRI_MONTHS_EN[9] == 'Ramadan'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
