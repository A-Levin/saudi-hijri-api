#!/usr/bin/env python3
import re
import json
import requests
from datetime import datetime
from pathlib import Path

HIJRI_MONTHS_AR = {
    1: 'محرم', 2: 'صفر', 3: 'ربيع الأول', 4: 'ربيع الآخر',
    5: 'جمادى الأولى', 6: 'جمادى الآخرة', 7: 'رجب', 8: 'شعبان',
    9: 'رمضان', 10: 'شوال', 11: 'ذو القعدة', 12: 'ذو الحجة'
}

HIJRI_MONTHS_EN = {
    1: 'Muharram', 2: 'Safar', 3: 'Rabi al-Awwal', 4: 'Rabi al-Thani',
    5: 'Jumada al-Ula', 6: 'Jumada al-Thani', 7: 'Rajab', 8: 'Shaban',
    9: 'Ramadan', 10: 'Shawwal', 11: 'Dhul-Qadah', 12: 'Dhul-Hijjah'
}


ARABIC_TO_INT = {'٠': 0, '١': 1, '٢': 2, '٣': 3, '٤': 4, '٥': 5, '٦': 6, '٧': 7, '٨': 8, '٩': 9}
MONTH_AR_TO_NUM = {v: k for k, v in HIJRI_MONTHS_AR.items()}


def arabic_num_to_int(s):
    result = 0
    for char in s:
        if char in ARABIC_TO_INT:
            result = result * 10 + ARABIC_TO_INT[char]
    return result


def fetch_spa_date():
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    try:
        resp = requests.get('https://www.spa.gov.sa/', headers=headers, timeout=30)
        resp.raise_for_status()

        for month_ar, month_num in MONTH_AR_TO_NUM.items():
            pattern = rf'([٠-٩]+)\s*{month_ar}\s*([٠-٩]+)'
            match = re.search(pattern, resp.text)
            if match and arabic_num_to_int(match.group(2)) > 1440:
                day = arabic_num_to_int(match.group(1))
                year = arabic_num_to_int(match.group(2))
                return {
                    'day': day,
                    'month': month_num,
                    'year': year,
                    'month_name_ar': month_ar,
                    'month_name_en': HIJRI_MONTHS_EN[month_num]
                }

        match = re.search(r'"date_hijri":"(\d{4})-(\d{2})-(\d{2})"', resp.text)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            return {
                'day': day,
                'month': month,
                'year': year,
                'month_name_ar': HIJRI_MONTHS_AR[month],
                'month_name_en': HIJRI_MONTHS_EN[month]
            }
    except Exception as e:
        print(f"Error fetching SPA: {e}")
    return None


def main():
    data_file = Path(__file__).parent / 'api' / 'hijri.json'
    data_file.parent.mkdir(exist_ok=True)

    if data_file.exists():
        with open(data_file) as f:
            data = json.load(f)
    else:
        data = {'current': None, 'history': [], 'source': 'spa.gov.sa'}

    hijri = fetch_spa_date()
    if hijri:
        hijri['gregorian'] = datetime.now().strftime('%Y-%m-%d')
        hijri['updated_at'] = datetime.now().isoformat()

        if data['current'] != hijri.get('day') or not data['current']:
            data['current'] = hijri
            data['history'].append(hijri)
            data['history'] = data['history'][-365:]
        else:
            data['current'] = hijri

        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Updated: {hijri['day']} {hijri['month_name_en']} {hijri['year']}")
    else:
        print("Failed to fetch date")


if __name__ == '__main__':
    main()
