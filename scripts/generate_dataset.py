import json
import os

def generate_catalog():
    tracks = {
        "DE": ("Data Engineering", [
            ("Python for Data Science", "Beginner", 10, [], ["Python"]),
            ("Relational Databases & SQL", "Beginner", 15, [], ["SQL", "PostgreSQL"]),
            ("Data Warehousing Fundamentals", "Intermediate", 20, ["DE101", "DE102"], ["ETL", "Data Warehousing", "Snowflake"]),
            ("Distributed Computing with PySpark", "Intermediate", 25, ["DE103"], ["PySpark", "Hadoop", "Spark"]),
            ("Real-Time Streaming with Apache Kafka", "Advanced", 30, ["DE104"], ["Kafka", "Event Streaming"]),
            ("Data Mesh Architecture", "Advanced", 20, ["DE105"], ["Data Governance", "System Architecture"]),
            ("Data Orchestration with Airflow", "Intermediate", 18, ["DE102"], ["Airflow", "Orchestration"]),
            ("Cloud Data Lakes on AWS S3", "Intermediate", 22, ["DE102"], ["AWS", "Data Lakes"]),
            ("BigData Querying with Trino & Presto", "Advanced", 25, ["DE104"], ["Trino", "Distributed Querying"]),
            ("Data Quality & Testing with Great Expectations", "Intermediate", 15, ["DE101"], ["Data Quality", "Testing"]),
            ("NoSQL Systems with MongoDB & Cassandra", "Intermediate", 20, ["DE102"], ["MongoDB", "NoSQL"]),
            ("Data Governance & Cataloging", "Advanced", 15, ["DE103"], ["Data Governance", "Metadata"]),
            ("dbt for Analytics Engineering", "Intermediate", 18, ["DE102"], ["dbt", "SQL", "Analytics Engineering"]),
            ("Advanced ETL Pipeline Design", "Advanced", 28, ["DE103", "DE107"], ["ETL", "Pipeline Design"]),
            ("Delta Lake & Databricks Architecture", "Advanced", 25, ["DE104"], ["Databricks", "Delta Lake"]),
            ("Columnar Storage with Apache Parquet & Arrow", "Intermediate", 16, ["DE101"], ["Parquet", "PyArrow"]),
            ("Data Security & Compliance (GDPR/HIPAA)", "Advanced", 14, ["DE106"], ["Data Security", "Compliance"]),
            ("Graph Databases with Neo4j", "Intermediate", 20, ["DE102"], ["Graph Databases", "Neo4j"]),
            ("Real-Time Analytics with Apache Pinot", "Advanced", 24, ["DE105"], ["Pinot", "Real-Time Analytics"]),
            ("Cloud Data Engineering on GCP BigQuery", "Intermediate", 22, ["DE102"], ["GCP", "BigQuery"]),
            ("Data Reliability Engineering", "Advanced", 20, ["DE107", "DE110"], ["Data Quality", "Observability"]),
            ("Scalable Batch Processing with Beam", "Advanced", 26, ["DE104"], ["Apache Beam", "Batch Processing"]),
            ("Time-Series Storage with InfluxDB", "Intermediate", 18, ["DE102"], ["InfluxDB", "Time-Series"]),
            ("Infrastructure as Code for Data Platforms (Terraform)", "Advanced", 22, ["DE108"], ["Terraform", "DevOps"]),
            ("Vector Databases for Data Engineers", "Advanced", 20, ["DE111"], ["Vector Search", "ChromaDB", "Pinecone"]),
            ("Data Observability & Lineage", "Advanced", 18, ["DE121"], ["Data Observability", "OpenLineage"])
        ]),
        "ML": ("Machine Learning & AI", [
            ("Linear Algebra & Calculus for ML", "Beginner", 12, [], ["Math", "Linear Algebra", "Calculus"]),
            ("Applied Machine Learning with Scikit-Learn", "Intermediate", 18, ["ML101"], ["Machine Learning", "Scikit-Learn"]),
            ("Deep Learning & Neural Networks", "Intermediate", 25, ["ML102"], ["PyTorch", "Deep Learning"]),
            ("Natural Language Processing with Transformers", "Advanced", 30, ["ML103"], ["NLP", "Transformers", "LLMs"]),
            ("MLOps: Deployment & Monitoring", "Advanced", 22, ["ML103"], ["MLOps", "Docker", "FastAPI"]),
            ("Computer Vision with OpenCV & PyTorch", "Intermediate", 24, ["ML103"], ["Computer Vision", "PyTorch"]),
            ("Reinforcement Learning Foundations", "Advanced", 28, ["ML103"], ["Reinforcement Learning", "RL"]),
            ("Retrieval-Augmented Generation (RAG) Architecture", "Advanced", 25, ["ML104"], ["RAG", "LangChain", "Vector Search"]),
            ("Fine-Tuning Large Language Models", "Advanced", 30, ["ML104"], ["LLMs", "PEFT", "LoRA"]),
            ("AI Ethics & Governance", "Beginner", 10, [], ["AI Ethics", "Governance"]),
            ("Feature Engineering & Selection", "Intermediate", 15, ["ML102"], ["Feature Engineering", "Python"]),
            ("Time Series Forecasting with ML", "Intermediate", 20, ["ML102"], ["Time Series", "Prophet"]),
            ("Graph Neural Networks (GNNs)", "Advanced", 26, ["ML103"], ["GNNs", "PyTorch Geometric"]),
            ("Generative AI & Diffusion Models", "Advanced", 28, ["ML103"], ["GenAI", "Diffusion Models"]),
            ("Hyperparameter Optimization with Optuna", "Intermediate", 14, ["ML102"], ["Hyperparameter Tuning", "Optuna"]),
            ("Explainable AI (XAI) with SHAP & LIME", "Advanced", 18, ["ML102"], ["XAI", "SHAP", "Model Interpretability"]),
            ("Speech Recognition & Audio Processing", "Advanced", 24, ["ML104"], ["Audio Processing", "Whisper"]),
            ("Edge AI & Model Quantization (TensorRT)", "Advanced", 22, ["ML103", "ML105"], ["Edge AI", "TensorRT", "Quantization"]),
            ("Recommendation Systems Design", "Advanced", 25, ["ML102"], ["Recommender Systems", "Collaborative Filtering"]),
            ("Bayesian Machine Learning", "Advanced", 20, ["ML101"], ["Bayesian ML", "Probabilistic Programming"]),
            ("Prompt Engineering & LLM Agents", "Intermediate", 16, ["ML104"], ["Prompt Engineering", "Agents"]),
            ("Multi-Modal AI Systems", "Advanced", 28, ["ML104", "ML106"], ["Multi-Modal AI", "CLIP"]),
            ("AI Model Evaluation & Benchmarking", "Intermediate", 15, ["ML102"], ["Model Evaluation", "Benchmarking"]),
            ("AutoML with H2O & Auto-Sklearn", "Intermediate", 16, ["ML102"], ["AutoML", "H2O"]),
            ("Scalable Distributed ML Training (Ray/Horovod)", "Advanced", 30, ["ML103", "ML105"], ["Distributed Training", "Ray"]),
            ("ML Model Security & Adversarial Attacks", "Advanced", 20, ["ML103"], ["AI Security", "Adversarial Machine Learning"])
        ]),
        "CL": ("Cloud Computing & DevOps", [
            ("Cloud Fundamentals (AWS/Azure/GCP)", "Beginner", 12, [], ["Cloud", "AWS", "Azure"]),
            ("Linux Systems & Shell Scripting", "Beginner", 15, [], ["Linux", "Bash"]),
            ("Containerization with Docker", "Beginner", 15, ["CL102"], ["Docker", "Containers"]),
            ("Container Orchestration with Kubernetes", "Intermediate", 25, ["CL103"], ["Kubernetes", "K8s"]),
            ("Infrastructure as Code with Terraform", "Intermediate", 20, ["CL101"], ["Terraform", "IaC"]),
            ("CI/CD Automation with GitHub Actions", "Intermediate", 18, ["CL102"], ["CI/CD", "GitHub Actions"]),
            ("Cloud Security & IAM Best Practices", "Intermediate", 18, ["CL101"], ["Cloud Security", "IAM"]),
            ("Site Reliability Engineering (SRE) Principles", "Advanced", 22, ["CL104"], ["SRE", "Observability"]),
            ("Serverless Architecture on AWS Lambda", "Intermediate", 20, ["CL101"], ["Serverless", "AWS Lambda"]),
            ("Monitoring & Alerting with Prometheus & Grafana", "Intermediate", 16, ["CL103"], ["Prometheus", "Grafana"]),
            ("Service Mesh Architecture with Istio", "Advanced", 24, ["CL104"], ["Istio", "Service Mesh"]),
            ("Cloud Financial Operations (FinOps)", "Intermediate", 14, ["CL101"], ["FinOps", "Cost Optimization"]),
            ("Networking & VPC Design in Cloud", "Intermediate", 20, ["CL101"], ["Cloud Networking", "VPC"]),
            ("Hybrid Cloud Architecture", "Advanced", 25, ["CL101", "CL104"], ["Hybrid Cloud", "Enterprise Architecture"]),
            ("DevSecOps Integration", "Advanced", 20, ["CL106"], ["DevSecOps", "Security Automation"]),
            ("Cloud Native Storage Solutions", "Intermediate", 18, ["CL104"], ["Cloud Storage", "Ceph"]),
            ("Chaos Engineering with Chaos Mesh", "Advanced", 20, ["CL108"], ["Chaos Engineering", "Resilience"]),
            ("Multi-Cloud Management Strategies", "Advanced", 22, ["CL101"], ["Multi-Cloud", "Cloud Governance"]),
            ("Edge Computing Architecture", "Advanced", 24, ["CL101", "CL103"], ["Edge Computing", "IoT"]),
            ("Disaster Recovery & Business Continuity in Cloud", "Advanced", 18, ["CL101"], ["Disaster Recovery", "Cloud Operations"]),
            ("Immutable Infrastructure Practices", "Advanced", 20, ["CL105"], ["IaC", "Packer"]),
            ("GitOps Operations with ArgoCD", "Intermediate", 18, ["CL104"], ["GitOps", "ArgoCD"]),
            ("Log Aggregation with ELK Stack", "Intermediate", 18, ["CL102"], ["ELK Stack", "Elasticsearch"]),
            ("Cloud Compliance & Audit Automation", "Advanced", 16, ["CL107"], ["Compliance", "Audit"]),
            ("Microservices API Gateways (Kong/Envoy)", "Intermediate", 20, ["CL103"], ["API Gateway", "Envoy"]),
            ("Cloud Backup & Migration Strategies", "Intermediate", 18, ["CL101"], ["Cloud Migration", "Backup"])
        ]),
        "MOB": ("Mobile Development", [
            ("Mobile UI Design & UX Fundamentals", "Beginner", 10, [], ["UI/UX", "Mobile Design"]),
            ("iOS App Development with Swift & SwiftUI", "Intermediate", 25, ["MOB101"], ["Swift", "SwiftUI", "iOS"]),
            ("Android Development with Kotlin & Jetpack Compose", "Intermediate", 25, ["MOB101"], ["Kotlin", "Android", "Jetpack Compose"]),
            ("Cross-Platform Apps with Flutter & Dart", "Intermediate", 22, ["MOB101"], ["Flutter", "Dart", "Cross-Platform"]),
            ("React Native Development", "Intermediate", 22, ["MOB101"], ["React Native", "JavaScript"]),
            ("Mobile App Architecture (MVVM/Clean)", "Intermediate", 18, ["MOB102"], ["Mobile Architecture", "MVVM"]),
            ("Mobile Performance Optimization", "Advanced", 20, ["MOB102"], ["Mobile Performance", "Profiling"]),
            ("Mobile Application Security", "Advanced", 20, ["MOB102"], ["Mobile Security", "Encryption"]),
            ("Mobile Analytics & Crash Reporting", "Beginner", 12, [], ["Firebase", "Crashlytics"]),
            ("CI/CD Pipelines for Mobile (Fastlane)", "Intermediate", 16, ["MOB102"], ["Fastlane", "Mobile CI/CD"]),
            ("Offline-First Mobile Architecture", "Advanced", 22, ["MOB102"], ["SQLite", "Realm", "Offline Sync"]),
            ("Push Notifications & Messaging Systems", "Intermediate", 14, ["MOB102"], ["Push Notifications", "APNs", "FCM"]),
            ("Mobile Augmented Reality (ARKit/ARCore)", "Advanced", 26, ["MOB102"], ["ARKit", "ARCore", "Augmented Reality"]),
            ("Mobile Payments Integration (Stripe/Apple Pay)", "Intermediate", 15, ["MOB102"], ["Stripe", "In-App Purchases"]),
            ("Bluetooth Low Energy (BLE) App Development", "Advanced", 24, ["MOB102"], ["BLE", "IoT Mobile"]),
            ("Mobile App Automated Testing (Appium)", "Intermediate", 18, ["MOB102"], ["Appium", "Automated Testing"]),
            ("Accessibility in Mobile Apps", "Beginner", 10, [], ["Accessibility", "WCAG"]),
            ("Wearable App Development (WatchOS/Wear OS)", "Advanced", 20, ["MOB102"], ["WatchOS", "Wear OS"]),
            ("Mobile Database Systems (Room/CoreData)", "Intermediate", 16, ["MOB102"], ["CoreData", "Room Database"]),
            ("GraphQL for Mobile Clients", "Intermediate", 16, ["MOB102"], ["GraphQL", "Apollo Mobile"]),
            ("Mobile Machine Learning (CoreML/MLKit)", "Advanced", 22, ["MOB102"], ["CoreML", "MLKit", "On-Device ML"]),
            ("Internationalization & Localization", "Beginner", 10, [], ["i18n", "Localization"]),
            ("Progressive Web Apps (PWA) Development", "Intermediate", 18, ["MOB101"], ["PWA", "Service Workers"]),
            ("App Store Optimization (ASO) & Publishing", "Beginner", 10, [], ["ASO", "App Store Publishing"]),
            ("Mobile Video & Audio Streaming Integration", "Advanced", 20, ["MOB102"], ["ExoPlayer", "AVFoundation"]),
            ("Location Services & Geofencing Apps", "Intermediate", 16, ["MOB102"], ["CoreLocation", "Geofencing"])
        ])
    }

    courses = []
    for prefix, (domain_name, module_list) in tracks.items():
        for idx, item in enumerate(module_list, start=101):
            title, diff, hours, prereqs, skills = item
            cid = f"{prefix}{idx}"
            courses.append({
                "course_id": cid,
                "title": title,
                "provider": "Coursera / edX",
                "domain": domain_name,
                "description": f"Comprehensive hands-on training in {title}. Key skills covered: {', '.join(skills)}.",
                "skills_covered": skills,
                "prerequisites": prereqs,
                "difficulty": diff,
                "est_hours": hours
            })

    os.makedirs("data", exist_ok=True)
    with open("data/full_courses.json", "w") as f:
        json.dump(courses, f, indent=2)

    print(f"Successfully generated {len(courses)} courses in data/full_courses.json!")

if __name__ == "__main__":
    generate_catalog()