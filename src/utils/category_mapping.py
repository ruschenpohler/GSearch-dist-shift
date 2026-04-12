SHAPLEY_QUERIES = [
    # (Shapley_category_name, query_type, category_id_or_None, search_term)
    # query_type: "category" = use cat= with broad search term
    # query_type: "search_term" = use as free-text search term
    ("Fitness", "category", 94, "fitness"),
    ("Food & Drink", "category", 71, "food"),
    ("Unemployment benefits", "search_term", None, "Unemployment benefits"),
    ("House price index", "search_term", None, "Housing prices"),
    ("Medical Facilities & Services", "category", 256, "hospital"),
    ("Distributed & Parallel Computing", "category", 1298, "computing"),
    ("Jobs topic", "search_term", None, "Jobs"),
    ("Financial Markets", "category", 1163, "market"),
    ("Rail Transport", "category", 666, "train"),
    ("Maritime Transport", "category", 665, "shipping"),
    ("Loan", "search_term", None, "Loan"),
    ("Food Service", "category", 957, "restaurant"),
]

NON_ECONOMIC_DIAGNOSTICS = [
    # (diagnostic_name, search_term)
    ("Roleplaying", "Roleplaying"),
    ("Creative writing", "Creative writing"),
    ("Cooking recipes", "Cooking recipes"),
]

ANNEX_B_GROUPS = {
    "Crisis / Recession": [
        "Economic crisis",
        "Crisis",
        "Recession",
        "Financial crisis",
        "Krach",
    ],
    "Unemployment / unemployment benefits": [
        "Unemployment",
        "Unemployment benefits",
        "Welfare & Unemployment",
    ],
    "Credit & Loans": [
        "Student loan",
        "Credit and Lending",
        "Loan",
        "Interest",
        "Mortgage",
        "Auto Financing",
    ],
    "Consumption items": [
        "Food & Drink",
        "Travel",
        "Health",
        "Fitness",
    ],
    "Jobs": [
        "Job Listings",
        "Jobs",
        "Recruitment",
        "Job search",
    ],
    "Bankruptcy": [
        "Bankruptcy",
        "Judicial Liquidation",
    ],
    "Housing": [
        "Affordable housing",
        "House price index",
        "Apartments & Residential Rentals",
        "Home Insurance",
        "Home Improvement",
    ],
    "News & Politics": [
        "Economy News",
        "Business News",
        "World News",
        "Politics",
    ],
    "Construction": [
        "Construction Consulting & Contracting",
        "Civil Engineering",
    ],
    "Personal Finance": [
        "Investment",
        "Investing",
        "Financial Planning",
    ],
    "Business services": [
        "Accounting & Auditing",
        "Consulting",
        "Outsourcing",
    ],
    "Industrial activity": [
        "Agriculture & Forestry",
        "Aviation",
        "Freight & Trucking",
        "Maritime Transport",
        "Rail Transport",
        "Manufacturing",
    ],
}
