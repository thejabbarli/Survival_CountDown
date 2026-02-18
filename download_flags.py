import urllib.request
from pathlib import Path

# 100 country codes
COUNTRIES = {
    "us": "United States", "br": "Brazil", "de": "Germany", "jp": "Japan",
    "fr": "France", "it": "Italy", "gb": "United Kingdom", "ca": "Canada",
    "au": "Australia", "in": "India", "cn": "China", "ru": "Russia",
    "mx": "Mexico", "es": "Spain", "ar": "Argentina", "kr": "South Korea",
    "nl": "Netherlands", "be": "Belgium", "se": "Sweden", "no": "Norway",
    "dk": "Denmark", "fi": "Finland", "pl": "Poland", "pt": "Portugal",
    "at": "Austria", "ch": "Switzerland", "ie": "Ireland", "nz": "New Zealand",
    "za": "South Africa", "eg": "Egypt", "ng": "Nigeria", "ke": "Kenya",
    "ma": "Morocco", "gh": "Ghana", "tz": "Tanzania", "et": "Ethiopia",
    "tr": "Turkey", "sa": "Saudi Arabia", "ae": "UAE", "il": "Israel",
    "ir": "Iran", "pk": "Pakistan", "bd": "Bangladesh", "id": "Indonesia",
    "th": "Thailand", "vn": "Vietnam", "ph": "Philippines", "my": "Malaysia",
    "sg": "Singapore", "tw": "Taiwan", "hk": "Hong Kong", "gr": "Greece",
    "cz": "Czech Republic", "hu": "Hungary", "ro": "Romania", "ua": "Ukraine",
    "co": "Colombia", "cl": "Chile", "pe": "Peru", "ve": "Venezuela",
    "ec": "Ecuador", "cu": "Cuba", "pa": "Panama", "cr": "Costa Rica",
    "gt": "Guatemala", "uy": "Uruguay", "py": "Paraguay", "bo": "Bolivia",
    "do": "Dominican Republic", "jm": "Jamaica", "ht": "Haiti", "pr": "Puerto Rico",
    "is": "Iceland", "lu": "Luxembourg", "mt": "Malta", "cy": "Cyprus",
    "ee": "Estonia", "lv": "Latvia", "lt": "Lithuania", "si": "Slovenia",
    "hr": "Croatia", "rs": "Serbia", "bg": "Bulgaria", "sk": "Slovakia",
    "np": "Nepal", "lk": "Sri Lanka", "mm": "Myanmar", "kh": "Cambodia",
    "qa": "Qatar", "kw": "Kuwait", "om": "Oman", "jo": "Jordan",
    "lb": "Lebanon", "iq": "Iraq", "af": "Afghanistan", "dz": "Algeria"
}

output_dir = Path("assets/countries")
output_dir.mkdir(parents=True, exist_ok=True)

for code, name in COUNTRIES.items():
    url = f"https://flagcdn.com/w320/{code}.png"
    path = output_dir / f"{code}.png"
    print(f"Downloading {name}...")
    urllib.request.urlretrieve(url, path)

print(f"\nDone! {len(COUNTRIES)} flags in {output_dir}")

# Generate manifest
import json
manifest = {
    "name": "Countries",
    "description": "World flags",
    "entities": [
        {"id": code, "name": name, "image": f"{code}.png", "color": "#333333"}
        for code, name in COUNTRIES.items()
    ]
}
with open(output_dir / "manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("manifest.json created!")
