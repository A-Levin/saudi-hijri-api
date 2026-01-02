# Saudi Hijri API

Free Hijri date API based on Saudi Arabia's official calendar from [SPA.gov.sa](https://spa.gov.sa).

## Usage

```bash
curl https://A-Levin.github.io/saudi-hijri-api/api/hijri.json
```

## Response

```json
{
  "current": {
    "day": 13,
    "month": 7,
    "year": 1447,
    "month_name_ar": "رجب",
    "month_name_en": "Rajab",
    "gregorian": "2026-01-02",
    "updated_at": "2026-01-02T12:00:00"
  },
  "history": [...],
  "source": "spa.gov.sa"
}
```

## How it works

GitHub Actions scrapes spa.gov.sa every 6 hours and updates the JSON file.
GitHub Pages serves it as a static API.
