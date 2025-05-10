HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

GKG_HEADER = [
    "GKGRECORDID", "DATE", "SourceCollectionIdentifier", "SourceCommonName",
    "DocumentIdentifier", "Counts", "V2Counts", "Themes", "V2Themes", "Locations",
    "V2Locations", "Persons", "V2Persons", "Organizations", "V2Organizations",
    "V2Tone", "Dates", "GCAM", "SharingImage", "RelatedImages", "SocialImageEmbeds",
    "SocialVideoEmbeds", "Quotations", "AllNames", "Amounts", "TranslationInfo",
    "Extras"
]

CURATED_THEME_LIST = ["ECON_TAXATION", "UNEMPLOYMENT", "ECON_BANKRUPTCY", "ECON_BOYCOTT", "ECON_COST_OF_LIVING", "ECON_CUTOUTLOOK", "ECON_DEREGULATION", "ECON_EARNINGSREPORT", 
                      "ECON_ENTREPRENEURSHIP", "ECON_HOUSING_PRICES", "ECON_INFORMAL_ECONOMY", "ECON_IPO", "ECON_INTEREST_RATE", "ECON_MONOPOLY", "ECON_MOU", "ECON_NATIONALIZE", 
                      "ECON_PRICECONTROL", "ECON_REMITTANCE", "ECON_STOCKMARKET", "ECON_SUBSIDIES", "ECON_UNIONS", "SLFID_ECONOMIC_DEVELOPMENT", "SLFID_ECONOMIC_POWER", "SOC_ECONCOOP",
                      "ECON_TRADE_DISPUTE", "ECON_FOREIGNINVEST", "ECON_FREETRADE", "ECON_CURRENCY_EXCHANGE_RATE", "ECON_CURRENCY_RESERVES", "ECON_DEBT",
                      "TAX_TERROR_GROUP", "SUICIDE_ATTACK", "EXTREMISM", "JIHAD", "TERROR", "WMD", "ACT_FORCEPOSTURE", "ARMEDCONFLICT", "BLOCKADE", "CEASEFIRE", "MILITARY", "MILITARY_COOPERATION", 
                      "PEACEKEEPING", "RELEASE_HOSTAGE", "SEIGE", "SLFID_MILITARY_BUILDUP", "SLFID_MILITARY_READINESS", "SLFID_MILITARY_SPENDING", "SLFID_PEACE_BUILDING", "TAX_MILITARY_TITLE",
                      "GOV_INTERGOVERNMENTAL", "SOC_DIPLOMCOOP", "RELATIONS","BORDER", "CHECKPOINT", "DISPLACED",  "EXILE", "IMMIGRATION", "REFUGEES", "SOC_FORCEDRELOCATION", "SOC_MASSMIGRATION", 
                      "UNREST_CHECKPOINT", "UNREST_CLOSINGBORDER","GENERAL_HEALTH", "HEALTH_SEXTRANSDISEASE", "HEALTH_VACCINATION", "MEDICAL", "MEDICAL_SECURITY","FIREARM_OWNERSHIP", "MIL_SELF_IDENTIFIED_ARMS_DEAL", 
                      "MIL_WEAPONS_PROLIFERATION","CRIME_ILLEGAL_DRUGS", "DRUG_TRADE", "TAX_CARTELS", "CRIME_CARTELS","UNREST_POLICEBRUTALITY", "SECURITY_SERVICES","DISCRIMINATION", "HATE_SPEECH","GENDER_VIOLENCE", 
                      "LGBT", "MOVEMENT_SOCIAL",  "MOVEMENT_WOMENS", "SLFID_CIVIL_LIBERTIES","ENV_BIOFUEL", "ENV_CARBONCAPTURE", "ENV_CLIMATECHANGE",  "ENV_COAL", "ENV_DEFORESTATION", "ENV_FISHERY", "ENV_FORESTRY", 
                      "ENV_GEOTHERMAL", "ENV_GREEN", "ENV_HYDRO", "ENV_METALS", "ENV_MINING", "ENV_NATURALGAS", "ENV_NUCLEARPOWER", "ENV_OIL", "ENV_OVERFISH", "ENV_POACHING", "ENV_WATERWAYS ", "ENV_SOLAR", "ENV_SPECIESENDANGERED", 
                      "ENV_SPECIESEXTINCT", "ENV_WINDPOWER", "FUELPRICES", "MOVEMENT_ENVIRONMENTAL", "SELF_IDENTIFIED_ENVIRON_DISASTER", "SLFID_MINERAL_RESOURCES", "SLFID_NATURAL_RESOURCES", "WATER_SECURITY","TAX_POLITICAL_PARTY",
                      "ELECTION_FRAUD","EDUCATION","CYBER_ATTACK",  "INTERNET_BLACKOUT", "INTERNET_CENSORSHIP", "MEDIA_CENSORSHIP", "MEDIA_MSM", "MEDIA_SOCIAL", "SURVEILLANCE", "FREESPEECH"]

ISSUES_TO_GDELT_THEMES  = {"taxes" : ["ECON_TAXATION",],
"unemployment" : [ "UNEMPLOYMENT", ],
"domesticeconomy" : ["ECON_BANKRUPTCY", "ECON_BOYCOTT", "ECON_COST_OF_LIVING", "ECON_CUTOUTLOOK", "ECON_DEREGULATION", "ECON_EARNINGSREPORT", "ECON_ENTREPRENEURSHIP", "ECON_HOUSING_PRICES", "ECON_INFORMAL_ECONOMY", "ECON_IPO", "ECON_INTEREST_RATE", "ECON_MONOPOLY", "ECON_MOU", "ECON_NATIONALIZE", "ECON_PRICECONTROL", "ECON_REMITTANCE", "ECON_STOCKMARKET", "ECON_SUBSIDIES", "ECON_UNIONS", "SLFID_ECONOMIC_DEVELOPMENT", "SLFID_ECONOMIC_POWER", "SOC_ECONCOOP"],
"trade" : ["ECON_TRADE_DISPUTE", "ECON_FOREIGNINVEST", "ECON_FREETRADE", "ECON_CURRENCY_EXCHANGE_RATE", "ECON_CURRENCY_RESERVES", "ECON_DEBT"],
"terrorism" : ["TAX_TERROR_GROUP", "SUICIDE_ATTACK", "EXTREMISM", "JIHAD", "TERROR", "WMD"],
"military" : ["ACT_FORCEPOSTURE", "ARMEDCONFLICT", "BLOCKADE", "CEASEFIRE", "MILITARY", "MILITARY_COOPERATION", "PEACEKEEPING", "RELEASE_HOSTAGE", "SEIGE", "SLFID_MILITARY_BUILDUP", "SLFID_MILITARY_READINESS", "SLFID_MILITARY_SPENDING", "SLFID_PEACE_BUILDING", "TAX_MILITARY_TITLE"],
"internationalrelations" : ["GOV_INTERGOVERNMENTAL", "SOC_DIPLOMCOOP", "RELATIONS"],
"immigration/refugees" : ["BORDER", "CHECKPOINT", "DISPLACED",  "EXILE", "IMMIGRATION", "REFUGEES", "SOC_FORCEDRELOCATION", "SOC_MASSMIGRATION", "UNREST_CHECKPOINT", "UNREST_CLOSINGBORDER"],
"healthcare" : ["GENERAL_HEALTH", "HEALTH_SEXTRANSDISEASE", "HEALTH_VACCINATION", "MEDICAL", "MEDICAL_SECURITY"],
"guncontrol" : ["FIREARM_OWNERSHIP", "MIL_SELF_IDENTIFIED_ARMS_DEAL", "MIL_WEAPONS_PROLIFERATION"],
"drug" : ["CRIME_ILLEGAL_DRUGS", "DRUG_TRADE", "TAX_CARTELS", "CRIME_CARTELS"],
"policesystem" : ["UNREST_POLICEBRUTALITY", "SECURITY_SERVICES"],
"racism" : ["DISCRIMINATION", "HATE_SPEECH"],
"civilliberties" : ["GENDER_VIOLENCE", "LGBT", "MOVEMENT_SOCIAL",  "MOVEMENT_WOMENS", "SLFID_CIVIL_LIBERTIES"],
"environment" :  ["ENV_BIOFUEL", "ENV_CARBONCAPTURE", "ENV_CLIMATECHANGE",  "ENV_COAL", "ENV_DEFORESTATION", "ENV_FISHERY", "ENV_FORESTRY", "ENV_GEOTHERMAL", "ENV_GREEN", "ENV_HYDRO", "ENV_METALS", "ENV_MINING", "ENV_NATURALGAS", "ENV_NUCLEARPOWER", "ENV_OIL", "ENV_OVERFISH", "ENV_POACHING", "ENV_WATERWAYS ", "ENV_SOLAR", "ENV_SPECIESENDANGERED", "ENV_SPECIESEXTINCT", "ENV_WINDPOWER", "FUELPRICES", "MOVEMENT_ENVIRONMENTAL", "SELF_IDENTIFIED_ENVIRON_DISASTER", "SLFID_MINERAL_RESOURCES", "SLFID_NATURAL_RESOURCES", "WATER_SECURITY"],
"partypolitics" : ["TAX_POLITICAL_PARTY"],
"electionfraud" : ["ELECTION_FRAUD"],
"education" : ["EDUCATION"],
"media/internet" : ["CYBER_ATTACK",  "INTERNET_BLACKOUT", "INTERNET_CENSORSHIP", "MEDIA_CENSORSHIP", "MEDIA_MSM", "MEDIA_SOCIAL", "SURVEILLANCE", "FREESPEECH"],
"energy" : ["ENV_BIOFUEL",  "ENV_COAL", "ENV_GEOTHERMAL", "ENV_GREEN", "ENV_HYDRO", "ENV_NATURALGAS", "ENV_NUCLEARPOWER", "ENV_OIL", "ENV_SOLAR",  "ENV_WINDPOWER"]
}

ALL_THEMES_FROM_ISSUES_MAP = list(set(theme for themes_list in ISSUES_TO_GDELT_THEMES.values() for theme in themes_list))

FIPS_MANUAL_MAP = {
    # A
    "ARUBA": "AA",
    "ANTIGUA AND BARBUDA": "AC",
    "UNITED ARAB EMIRATES": "AE",
    "AFGHANISTAN": "AF",
    "ALGERIA": "AG",
    "AZERBAIJAN": "AJ",
    "ALBANIA": "AL",
    "ARMENIA": "AM",
    "ANDORRA": "AN",
    "ANGOLA": "AO",
    "AMERICAN SAMOA": "AQ", # Territory
    "ARGENTINA": "AR",
    "AUSTRALIA": "AS",
    "ASHMORE AND CARTIER ISLANDS": "AT", # Territory
    "AUSTRIA": "AU",
    "ANGUILLA": "AV", # Territory
    "AKROTIRI": "AX", # Sovereign Base Area (UK)
    "ANTARCTICA": "AY", # Continent/Treaty System

    # B
    "BAHRAIN": "BA",
    "BARBADOS": "BB",
    "BOTSWANA": "BC",
    "BERMUDA": "BD", # Territory
    "BELGIUM": "BE",
    "BAHAMAS, THE": "BF", # Note: "BAHAMAS" might be a more common input
    "BAHAMAS": "BF",      # Added common variant
    "BANGLADESH": "BG",
    "BELIZE": "BH",
    "BOSNIA AND HERZEGOVINA": "BK",
    "BOLIVIA": "BL",
    "BURMA": "BM", # Now MYANMAR, GDELT might still see "Burma"
    "MYANMAR": "BM",
    "BENIN": "BN",
    "BELARUS": "BO",
    "SOLOMON ISLANDS": "BP", # Moved from S to B due to FIPS code "BP"
    "BRAZIL": "BR",
    "BASSAS DA INDIA": "BS", # Territory
    "BHUTAN": "BT",
    "BULGARIA": "BU",
    "BOUVET ISLAND": "BV", # Territory
    "BRUNEI": "BX", # Brunei Darussalam
    "BURUNDI": "BY",

    # C
    "CAMBODIA": "CB",
    "CHAD": "CD",
    "SRI LANKA": "CE", # Moved from S to C due to FIPS code "CE"
    "CONGO, REPUBLIC OF THE": "CF", # Brazzaville
    "CONGO (BRAZZAVILLE)": "CF",
    "CONGO, DEMOCRATIC REPUBLIC OF THE": "CG", # Kinshasa
    "CONGO (KINSHASA)": "CG",
    "DR CONGO": "CG",
    "CHINA": "CH",
    "CHILE": "CI",
    "CAYMAN ISLANDS": "CJ", # Territory
    "COCOS (KEELING) ISLANDS": "CK", # Territory
    "CAMEROON": "CM",
    "COMOROS": "CN",
    "COLOMBIA": "CO",
    "NORTHERN MARIANA ISLANDS": "CQ", # Commonwealth (US)
    "CORAL SEA ISLANDS": "CR", # Territory
    "COSTA RICA": "CS",
    "CENTRAL AFRICAN REPUBLIC": "CT",
    "CUBA": "CU",
    "CABO VERDE": "CV", # Cape Verde
    "CAPE VERDE": "CV",
    "COOK ISLANDS": "CW", # Self-governing (NZ)
    "CYPRUS": "CY",

    # D
    "DENMARK": "DA",
    "DJIBOUTI": "DJ",
    "DOMINICA": "DO",
    "JARVIS ISLAND": "DQ", # Territory (US)
    "DOMINICAN REPUBLIC": "DR",
    "DHEKELIA": "DX", # Sovereign Base Area (UK)

    # E
    "ECUADOR": "EC",
    "EGYPT": "EG",
    "IRELAND": "EI",
    "EQUATORIAL GUINEA": "EK",
    "ESTONIA": "EN",
    "ERITREA": "ER",
    "EL SALVADOR": "ES",
    "ETHIOPIA": "ET",
    "EUROPA ISLAND": "EU", # Territory
    "CZECHIA": "EZ", # Czech Republic
    "CZECH REPUBLIC": "EZ",

    # F
    "FINLAND": "FI",
    "FIJI": "FJ",
    "FALKLAND ISLANDS (ISLAS MALVINAS)": "FK", # Territory
    "FALKLAND ISLANDS": "FK",
    "MICRONESIA, FEDERATED STATES OF": "FM",
    "FAROE ISLANDS": "FO", # Self-governing (Denmark)
    "FRENCH POLYNESIA": "FP", # Overseas Collectivity (France)
    "FRANCE": "FR", # Includes Metropolitan France
    "FRENCH SOUTHERN AND ANTARCTIC LANDS": "FS", # Territory

    # G
    "GABON": "GB",
    "GAMBIA, THE": "GA",
    "GAMBIA": "GA",
    "GAZA STRIP": "GZ", # Occupied Territory
    "GEORGIA": "GG",
    "GERMANY": "GM", # This is the key one for your immediate problem!
    "GHANA": "GH",
    "GIBRALTAR": "GI", # Territory
    "GRENADA": "GJ",
    "GREENLAND": "GL", # Self-governing (Denmark)
    "GUERNSEY": "GK", # Crown Dependency (UK)
    "GREECE": "GR",
    "GUATEMALA": "GT",
    "FRENCH GUIANA": "FG", # Overseas Department (France) - Note: FIPS FG
    "GUAM": "GQ", # Territory (US)
    "GUINEA": "GV",
    "GUYANA": "GY",
    "GLORIOSO ISLANDS": "GO", # Territory

    # H
    "HAITI": "HA",
    "HONG KONG": "HK", # Special Admin Region (China)
    "HEARD ISLAND AND MCDONALD ISLANDS": "HM", # Territory
    "HONDURAS": "HO",
    "HOWLAND ISLAND": "HQ", # Territory (US)
    "CROATIA": "HR",
    "HUNGARY": "HU",

    # I
    "ICELAND": "IC",
    "INDONESIA": "ID",
    "ISLE OF MAN": "IM", # Crown Dependency (UK)
    "INDIA": "IN",
    "BRITISH INDIAN OCEAN TERRITORY": "IO", # Territory
    "CLIPPERTON ISLAND": "IP", # Territory
    "IRAN": "IR", # Islamic Republic of Iran
    "ISRAEL": "IS",
    "ITALY": "IT",
    "COTE D'IVOIRE": "IV", # Ivory Coast
    "IRAQ": "IZ",

    # J
    "JAPAN": "JA",
    "JERSEY": "JE", # Crown Dependency (UK)
    "JAMAICA": "JM",
    "JAN MAYEN": "JN", # Territory (Norway)
    "JORDAN": "JO",
    "JOHNSTON ATOLL": "JQ", # Territory (US)
    "JUAN DE NOVA ISLAND": "JU", # Territory

    # K
    "KENYA": "KE",
    "KYRGYZSTAN": "KG",
    "KOREA, NORTH": "KN", # Democratic People's Republic of Korea
    "NORTH KOREA": "KN",
    "KINGMAN REEF": "KQ", # Territory (US)
    "KIRIBATI": "KR",
    "KOREA, SOUTH": "KS", # Republic of Korea
    "SOUTH KOREA": "KS",
    "CHRISTMAS ISLAND": "KT", # Territory (Australia)
    "KUWAIT": "KU",
    "KAZAKHSTAN": "KZ",

    # L
    "LAOS": "LA", # Lao People's Democratic Republic
    "LEBANON": "LE",
    "LATVIA": "LG",
    "LITHUANIA": "LH",
    "LIBERIA": "LI",
    "SLOVAKIA": "LO",
    "PALMYRA ATOLL": "LQ", # Territory (US)
    "LIECHTENSTEIN": "LS",
    "LESOTHO": "LT",
    "LUXEMBOURG": "LU",
    "LIBYA": "LY",

    # M
    "MADAGASCAR": "MA",
    "MARTINIQUE": "MB", # Overseas Department (France)
    "MACAO": "MC", # Special Admin Region (China)
    "MOLDOVA": "MD",
    "MAYOTTE": "MF", # Overseas Department (France)
    "MONGOLIA": "MG",
    "MONTSERRAT": "MH", # Territory
    "MALAWI": "MI",
    "NORTH MACEDONIA": "MK", # Formerly Macedonia
    "MACEDONIA": "MK", # Common name still
    "MALI": "ML",
    "MONACO": "MN",
    "MIDWAY ISLANDS": "MQ", # Territory (US)
    "MAURITANIA": "MR",
    "MAURITIUS": "MP",
    "MALAYSIA": "MY",
    "MOZAMBIQUE": "MZ",

    # N
    "NAMIBIA": "WA", # Moved from N to W due to FIPS code "WA"
    "NEW CALEDONIA": "NC", # Special Collectivity (France)
    "NIUE": "NE", # Associated State (NZ)
    "NORFOLK ISLAND": "NF", # Territory (Australia)
    "NIGER": "NG",
    "VANUATU": "NH", # Moved from V to N due to FIPS code "NH"
    "NIGERIA": "NI",
    "NETHERLANDS": "NL",
    "NORWAY": "NO",
    "NEPAL": "NP",
    "NAURU": "NR",
    "SURINAME": "NS", # Moved from S to N due to FIPS code "NS"
    "NETHERLANDS ANTILLES": "NT", # Former entity, GDELT might still have data
    "NICARAGUA": "NU",
    "NEW ZEALAND": "NZ",

    # O
    "OMAN": "MU", # Moved from O to M due to FIPS code "MU"

    # P
    "PANAMA": "PM", # Moved from P to PM to avoid conflict with PM (St. Pierre and Miquelon)
    "PARACEL ISLANDS": "PF", # Disputed
    "PERU": "PE",
    "SPRATLY ISLANDS": "PG", # Disputed
    "PAKISTAN": "PK",
    "POLAND": "PL",
    "SAINT PIERRE AND MIQUELON": "SB", # Moved from S to SB due to FIPS code "SB" - note Wikipedia list has PM for this, but GDELT might use SB consistently for some reason or there are multiple FIPS lists. Checking Wikipedia again for PM... FIPS 10-4 for Saint Pierre and Miquelon is SB. (PM is ISO).
    "PITCAIRN ISLANDS": "PC", # Territory
    "PUERTO RICO": "RQ", # Commonwealth (US)
    "PORTUGAL": "PO",
    "PALAU": "PS",
    "GUINEA-BISSAU": "PU",
    "PARAGUAY": "PY",

    # Q
    "QATAR": "QA",

    # R
    "REUNION": "RE", # Overseas Department (France)
    "ROMANIA": "RO",
    "RUSSIA": "RS", # Russian Federation
    "RWANDA": "RW",

    # S
    "SAUDI ARABIA": "SA",
    # "SAINT PIERRE AND MIQUELON": "SB", # Already listed
    "SAINT KITTS AND NEVIS": "SC",
    "SEYCHELLES": "SE",
    "SOUTH GEORGIA AND SOUTH SANDWICH ISLANDS": "SX", # Territory (UK)
    "SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA": "SH", # Territory (UK)
    "SAINT HELENA": "SH", # Common name
    "SLOVENIA": "SI",
    "SIERRA LEONE": "SL",
    "SAN MARINO": "SM",
    "SENEGAL": "SG",
    "SOMALIA": "SO",
    # "SRI LANKA": "CE", # Already listed
    "SAO TOME AND PRINCIPE": "TP", # Moved from S to T due to FIPS code "TP"
    "SPAIN": "SP",
    "SUDAN": "SU",
    "SWEDEN": "SW",
    "SINGAPORE": "SN",
    "SVALBARD": "SV", # Territory (Norway)
    "SYRIA": "SY",
    "SWITZERLAND": "SZ",

    # T
    "TURKS AND CAICOS ISLANDS": "TK", # Territory
    "THAILAND": "TH",
    "TAJIKISTAN": "TI",
    "TOKELAU": "TL", # Territory (NZ)
    "TONGA": "TN",
    "TOGO": "TO",
    # "SAO TOME AND PRINCIPE": "TP", # Already listed
    "TUNISIA": "TS",
    "TIMOR-LESTE": "TT", # East Timor
    "EAST TIMOR": "TT",
    "TURKEY": "TU",
    "TRINIDAD AND TOBAGO": "TD", # Moved from T to TD to avoid conflict with TD (Chad)
    "TUVALU": "TV",
    "TAIWAN": "TW", # Republic of China
    "TURKMENISTAN": "TX",
    "TANZANIA": "TZ", # United Republic of Tanzania

    # U
    "UGANDA": "UG",
    "UNITED KINGDOM": "UK",
    "UKRAINE": "UP",
    "UNITED STATES MINOR OUTLYING ISLANDS": "UM",
    "EGYPT": "EG", # FIPS is EG, already listed under E
    "BURKINA FASO": "UV",
    "URUGUAY": "UY",
    "UNITED STATES": "US",
    "UZBEKISTAN": "UZ",

    # V
    "VATICAN CITY": "VT", # Holy See
    "HOLY SEE (VATICAN CITY STATE)": "VT",
    "SAINT VINCENT AND THE GRENADINES": "VC",
    "VENEZUELA": "VE",
    "BRITISH VIRGIN ISLANDS": "VI", # Territory
    "VIETNAM": "VM",
    "VIRGIN ISLANDS (U.S.)": "VQ", # Territory
    "U.S. VIRGIN ISLANDS": "VQ",
    # "VANUATU": "NH", # Already listed

    # W
    "WAKE ISLAND": "WQ", # Territory (US)
    "WALLIS AND FUTUNA": "WF", # Territory (France)
    "WEST BANK": "WE", # Occupied Territory
    "WESTERN SAHARA": "WI",
    "SAMOA": "WS", # Independent State of Samoa

    # Y
    "YEMEN": "YM",
    "SERBIA": "RI", # Moved from S, (SR for ISO), FIPS is RI
    "MONTENEGRO": "MJ", # Moved from M, (ME for ISO), FIPS is MJ

    # Z
    "ZAMBIA": "ZA",
    "ZIMBABWE": "ZI",

    # Other / Dependencies / Specific cases from Wikipedia list
    "BAKER ISLAND": "FQ",
    "ETOROFU, HABOMAI, KUNASHIRI, AND SHIKOTAN ISLANDS": "PJ", # Disputed Kuril Islands (Russia-Japan)
    "NAVASSA ISLAND": "BQ",
    "SERRANA BANK": "BN", # (Disputed) - Note: BN also Benin, careful if names overlap
    "TROMELIN ISLAND": "TE"
}