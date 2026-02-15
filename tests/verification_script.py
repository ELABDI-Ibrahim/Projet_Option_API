import json
import sys
import os

# Add current directory to path so we can import services
sys.path.append(os.getcwd())

from services.enrichement import EnrichmentAgent

# Define the input data exactly as provided by the user
scraped_data = {
  "id": "c27f66c2-6bd4-460c-97c2-3e1f3033fd1e",
  "candidate_id": "ee0586c4-465e-49af-9087-f84e6ba3ca9c",
  "parsed_data": {
    "name": "Ibrahim EL ABDI",
    "email": "ibrahim.elabdi@student-cs .fr",
    "skills": [
      {
        "items": [
          "Python",
          "Java",
          "C#",
          "SQL",
          "PySpark",
          "Amazon Cloud Services (AWS)",
          "Docker",
          "Git",
          "GitHub",
          "REST APIs"
        ],
        "category": "Programmation & Data Engineering"
      },
      {
        "items": [
          "Power BI",
          "Excel (VBA)",
          "PowerQuery",
          "DAX"
        ],
        "category": "Visualisation & Business Intelligence"
      },
      {
        "items": [
          "PyTorch",
          "Scikit-learn",
          "LangChain",
          "Pandas",
          "N8N",
          "Déploiement de modèles"
        ],
        "category": "Intelligence Artificielle & Machine Learning"
      },
      {
        "items": [
          "Méthodologie Agile",
          "Certification Scrum Master"
        ],
        "category": "Gestion de projet"
      },
      {
        "items": [
          "Esprit analytique",
          "autonomie",
          "rigueur",
          "proactivité"
        ],
        "category": "Compétences transversales"
      }
    ],
    "summary": "Étudiant en ingénierie – À la recherche d’un stage de fin d’études de 6 mois à partir de mars 2026",
    "contacts": [
      "ibrahim.elabdi@student-cs .fr",
      "+33 7 56 84 77 48"
    ],
    "location": "Metz, France",
    "projects": [
      {
        "url": None,
        "role": None,
        "to_date": None,
        "duration": None,
        "from_date": None,
        "description": "Conception d’un tableau de bord Power BI pour synthétiser et analyser les données d’enregistrement. Génération de nouvelles instances de données pour réaliser des stress tests. Développement de modèles d’optimisation pour l’attribution des sièges passagers sous contraintes.",
        "project_name": "Mise en place d’un système d’attribution des sièges passagers Air France",
        "technologies": [
          "Power BI"
        ]
      },
      {
        "url": None,
        "role": None,
        "to_date": None,
        "duration": None,
        "from_date": None,
        "description": "Nettoyage, traitement et extraction des données avec SQL et statistiques descriptives. Développement et évaluation de modèles de classification (KNN, SVM, Réseaux de neurones). Implémentation d’autoencodeurs pour la maintenance prédictive des roulements.",
        "project_name": "Prédiction des anomalies de roulements dans les trains à grande vitesse SIANA",
        "technologies": [
          "SQL",
          "Python",
          "KNN",
          "SVM",
          "Réseaux de neurones",
          "autoencodeurs"
        ]
      },
      {
        "url": None,
        "role": None,
        "to_date": None,
        "duration": None,
        "from_date": None,
        "description": "Définition d’indicateurs clés pour évaluer la gestion des déchets sur chantier. Analyse des données BTP et visualisation via Power BI. Proposition de solutions organisationnelles et techniques pour optimiser le tri et la gestion.",
        "project_name": "Analyse de données de gestion des déchets BTP et définition de KPIs LIVA",
        "technologies": [
          "Power BI"
        ]
      },
      {
        "url": None,
        "role": None,
        "to_date": None,
        "duration": None,
        "from_date": None,
        "description": "Tests de plusieurs algorithmes : Random Forest, Naive Bayes, AdaBoost, SVC. Déploiement et suivi via Grafana et Prometheus. Collaboration et versioning sur Trello et GitHub.",
        "project_name": "Prédiction des localisations cellulaires des protéines",
        "technologies": [
          "Random Forest",
          "Naive Bayes",
          "AdaBoost",
          "SVC",
          "Grafana",
          "Prometheus"
        ]
      },
      {
        "url": None,
        "role": None,
        "to_date": None,
        "duration": None,
        "from_date": None,
        "description": "Conception d’un système collaboratif multi-agents intégrant analyse, synthèse, décision et communication. Définition des rôles, compétences et protocoles d’interaction entre agents. Intégration d’un LLM pour la coordination, la planification et l’adaptation des agents. Simulation d’un scénario complet d’analyse de données (Collection, Analyse et Génération de rapport). Développement d’une interface Streamlit pour visualiser les échanges et les résultats.",
        "project_name": "Conception d’un système d’analyse de données multi-agents intelligent",
        "technologies": [
          "LLM",
          "Streamlit"
        ]
      }
    ],
    "interests": [],
    "educations": [
      {
        "degree": "Programme d’ingénierie",
        "to_date": "2026",
        "duration": "2022 – 2026",
        "location": "",
        "from_date": "2022",
        "description": "Spécialisations : intelligence artificielle générative, apprentissage automatique, LLM et systèmes RAG, structuration de bases de connaissances, développement d’agents IA",
        "linkedin_url": None,
        "institution_name": "École Centrale Casablanca"
      },
      {
        "degree": "Programme d’ingénierie - 2ème année",
        "to_date": "2025",
        "duration": "2023 – 2025",
        "location": "",
        "from_date": "2023",
        "description": "Spécialisations : optimisation, recherche opérationnelle, IA, stratégie d’entreprise, cloud computing",
        "linkedin_url": None,
        "institution_name": "CentraleSupélec"
      },
      {
        "degree": "Classes préparatoires (MPSI - MP)",
        "to_date": "2022",
        "duration": "2020 – 2022",
        "location": "",
        "from_date": "2020",
        "description": "Préparation aux concours des grandes écoles d’ingénieurs, avec un accent sur les mathématiques et l’informatique",
        "linkedin_url": None,
        "institution_name": "Lycée Omar Ibn El Khattab"
      }
    ],
    "experiences": [
      {
        "to_date": "06/2025",
        "duration": "6 mois",
        "location": "",
        "from_date": "01/2025",
        "description": "Collaboration avec les équipes métiers pour traduire les besoins financiers en solutions d’optimisation fondées sur les données. Conception et déploiement d’une plateforme d’optimisation des collatéraux améliorant l’efficacité du financement sous contraintes multiples. Construction de pipelines de données de bout en bout pour traiter et intégrer les jeux de données financiers dans les workflows d’optimisation. Réduction du temps de calcul par un facteur 10 par rapport à la solution interne existante. Analyse de données de crédit et financières pour identifier des tendances prédictives et appuyer la prise de décision. Technologies utilisées : Python (Numpy, Numba, Pandas), SAS, C#, Dask ( PySpark), DuckDB, HTML, CSS, Javascript",
        "linkedin_url": None,
        "position_title": "Stagiaire Data Scientist et Recherche Operationnelle",
        "institution_name": "Crédit Agricole SA"
      },
      {
        "to_date": "12/2024",
        "duration": "6 mois",
        "location": "",
        "from_date": "07/2024",
        "description": "Réalisation d’analyses avancées sur des données automobiles et financières (remarketing, gestion des risques, coûts de maintenance). Développement de tableaux de bord interactifs Power BI et automatisation de rapports via Python et VBA. Création d’un modèle de détection de signature basé sur l’IA pour renforcer la vérification documentaire. Amélioration de l’accessibilité des analyses pour les auditeurs via des initiatives de stratégie de données. Technologies utilisées : Python (Plotly, Dash, Pytorch, Polars, Scikit-learn), SQL, Excel, VBA",
        "linkedin_url": None,
        "position_title": "Stagiaire Data Analyst en Inspection Générale et Audit",
        "institution_name": "Société Générale"
      },
      {
        "to_date": "08/2023",
        "duration": "2 mois",
        "location": "",
        "from_date": "06/2023",
        "description": "Implémentation du protocole MQTT pour la collecte et la centralisation des données de capteurs en temps réel. Intégration de flux de données live dans OpenRemote pour la visualisation et la détection d’anomalies. Technologies utilisées : Python, IOT (Protocole MQTT), Arduino",
        "linkedin_url": None,
        "position_title": "Stage en collecte et analyse de données de capteurs IoT",
        "institution_name": "Tanger Med Special Agency"
      }
    ],
    "linkedin_url": "https://www.linkedin.com/in/essameldin-ibrahim-174a0b98",
    "open_to_work": True,
    "accomplishments": []
  },
  "parsed_text": "...",
  "file_url": "...",
  "source": "upload",
  "enriched": False,
  "created_at": "2026-02-11T14:10:43.854459+00:00",
  "deleted_at": None
}

# The schema provided in the prompt is a SCHEMA definition, but for the enrichment agent to find "matches", 
# the "Difference" data must be an instance of data, not schema.
# However, the user labeled the second JSON as "json_schema".
# And the task says: "Reference/Target JSON – contains the canonical schema of the resume data (job description, project description, or academic program requirements)."
# AND "Identify matching elements between the scraped resume and reference JSON... missing elements (present in reference but not in the resume)"
#
# If the reference JSON is purely a schema (types, properties), then "missing elements" means missing KEYS?
# BUT the example output "missing_in_resume": { "skills": ["..."] } implies missing VALUES.
# 
# Usually in these tasks, "Reference JSON" is a Job Description parsed into the same structure, or a "Golden Resume".
#
# Given the user provided ONLY the schema as the second JSON in the prompt...
# "and the other one has this schema ... json_schema = { ... }"
#
# Wait, did the user provide DATA for the second JSON?
# The prompt says: "and the other one has this schema [SCHEMA DICT]"
# It does NOT provide a data instance for the second JSON.
#
# BUT the Task description says: "Reference/Target JSON – contains the canonical schema of the resume data (job description, project description, or academic program requirements)."
#
# If I only have the schema, I can't find "matching elements" in terms of content (e.g. "Python" vs "Python").
# I can only check if the structure matches.
#
# However, the user might have MEANT "Here is the schema that BOTH JSONs follow, and I want you to compare two instances (Scraped vs Reference Data)".
# BUT I don't have the Reference Data instance in the prompt!
#
# EXCEPT... maybe the user implies I should GENERATE the reference data? No, "You receive two JSONs".
#
# Did I miss something?
# "Scraped Resume JSON ... Reference/Target JSON ... You receive two JSONs"
#
# In the prompt, the user pastes:
# 1. "example : { ... }" (The Scraped Resume)
# 2. "and the other one has this schema ... json_schema = { ... }"
#
# The user might be confusing "Schema" with "Reference Data" or I am supposed to extracting something from the schema?
# No, "missing elements (present in reference but not in the resume)".
#
# Maybe the user FORGOT to paste the Reference Data instance?
# OR maybe the user wants me to use the Scraped Data AS the reference for itself (sanity check)? 
# No, that's trivial.
#
# Let's look closer at the prompt's "schema" block.
# It is just a JSON Schema definition found in `json_schema = ...`.
#
# Hypotheses:
# A) The user wants me to write the CODE that *would* take a reference JSON, even if I don't have one right now to test with.
# B) The user wants me to USE the schema as the reference? (e.g. check if fields exist). But the output format asks for "matches" with "resume_item" vs "reference_item".
#
# I will create a DUMMY reference data object that has some overlaps with the scraped data to demonstrate the matching logic in the verification script.
# This proves the code works.

reference_data_dummy = {
    "name": "Ibrahim EL ABDI", # Match
    "skills": [
        {"category": "Data", "items": ["Python", "SQL", "Terraform"]}, # Terraform missing in resume
        {"category": "Web", "items": ["HTML", "CSS", "React"]} # React missing in resume
    ],
    "experiences": [
        {
            "position_title": "Stagiaire Data Scientist et Recherche Operationnelle",
            "institution_name": "Crédit Agricole SA",
            "description": "Optimisation des collatéraux et pipelines de données." # Fuzzy match
        },
        {
            "position_title": "Senior Data Engineer", # Missing in resume
            "institution_name": "Google",
            "description": "Big data stuff."
        }
    ],
    "educations": [
        {
            "degree": "Programme d’ingénierie",
            "institution_name": "École Centrale Casablanca",
            "description": "Spécialisations IA." # Fuzzy match
        }
    ],
    "projects": [],
    "linkedin_url": "https://www.linkedin.com/in/essameldin-ibrahim-174a0b98"
}

print("Initializing EnrichmentAgent...")
agent = EnrichmentAgent()

print("Running Enrichment...")
try:
    result = agent.enrich_resume(scraped_data, reference_data_dummy)
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

