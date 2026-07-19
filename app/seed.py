from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_password_hash, verify_password
from app.models.admin import AdminUser
from app.models.content import ContentItem
from app.services.analytics import seed_mock_analytics


SEED_CONTENT = [
    {
        "module": "projects",
        "title": "Open Source Portfolio Platform",
        "slug": "portfolio-platform",
        "summary": "A modular portfolio with a FastAPI backend, SQLite content storage, and Next.js admin management.",
        "body": "This platform gives me a structured way to manage profile content, projects, writing, gallery entries, and contact messages from one dashboard.",
        "sort_order": 1,
        "tags": '["FastAPI", "Next.js", "SQLite"]',
    },
    {
        "module": "blog",
        "title": "Building Useful Software One Layer at a Time",
        "slug": "building-useful-software",
        "summary": "Notes on how I think about shipping software that remains practical after the first release.",
        "body": "I care about software that is maintainable, testable, and understandable. My approach is to design each layer so it can evolve without making the whole product fragile.",
        "sort_order": 1,
        "tags": '["Engineering", "Product"]',
    },
    {
        "module": "articles",
        "title": "Why Data Thinking Makes Better Products",
        "slug": "data-thinking-products",
        "summary": "A short article on bringing measurement and experimentation into product engineering.",
        "body": "Data thinking helps me ask sharper questions, measure outcomes, and turn product assumptions into signals that guide better engineering decisions.",
        "sort_order": 1,
        "tags": '["Data", "Product", "AI"]',
    },
    {
        "module": "gallery",
        "title": "Workspace Snapshot",
        "slug": "workspace-snapshot",
        "summary": "A placeholder gallery entry for screenshots, profile photos, certificates, or product images.",
        "body": "Use the admin dashboard to replace this with real gallery content and images.",
        "image_url": "/images/gallery/workspace.jpg",
        "sort_order": 1,
        "tags": '["Gallery"]',
    },
    {
        "module": "experience",
        "title": "Software Developer",
        "slug": "skye8",
        "summary": "Current",
        "body": "I am publicly listed as a Software Developer at SKYE8.\nI build across software engineering, data science, backend APIs, AI experiments, and mobile apps.",
        "sort_order": 1,
        "tags": '[]',
    },
    {
        "module": "experience",
        "title": "Software Engineer and Data Scientist",
        "slug": "public-github-bio",
        "summary": "Profile",
        "body": "My GitHub bio describes my combined software engineering and data science focus.\nI connect practical product delivery with AI and data-oriented systems.",
        "sort_order": 2,
        "tags": '[]',
    },
    {
        "module": "experience",
        "title": "Public Repository Builder",
        "slug": "github-bld237",
        "summary": "Open Source",
        "body": "I maintain 27 public repositories with Python, Dart, and HTML represented in recent work.\nMy recent repositories include Chatbot, BiteRush, event_api-fastapi, task_api, Agent, and taskplus.",
        "sort_order": 3,
        "tags": '[]',
    },
    {
        "module": "skills",
        "title": "Languages",
        "slug": "languages",
        "summary": "Core programming languages",
        "body": "TypeScript, JavaScript, Python, Dart, SQL",
        "sort_order": 1,
        "tags": '["TypeScript", "JavaScript", "Python", "Dart", "SQL"]',
    },
    {
        "module": "skills",
        "title": "Frontend",
        "slug": "frontend",
        "summary": "Interface development technologies",
        "body": "HTML, React, Next.js, Responsive UI, SEO",
        "sort_order": 2,
        "tags": '["HTML", "React", "Next.js", "Responsive UI", "SEO"]',
    },
    {
        "module": "skills",
        "title": "Backend",
        "slug": "backend",
        "summary": "Server-side services and APIs",
        "body": "Python APIs, FastAPI, Task APIs, Event APIs, Services",
        "sort_order": 3,
        "tags": '["Python APIs", "FastAPI", "Task APIs", "Event APIs", "Services"]',
    },
    {
        "module": "skills",
        "title": "AI & Data",
        "slug": "ai-data",
        "summary": "Data pipelines and intelligent components",
        "body": "Data Science, Chatbots, Agents, Automation",
        "sort_order": 4,
        "tags": '["Data Science", "Chatbots", "Agents", "Automation"]',
    },
    {
        "module": "skills",
        "title": "Mobile",
        "slug": "mobile",
        "summary": "Native mobile experiences",
        "body": "Dart, Flutter-style Apps, Mobile UX, Performance",
        "sort_order": 5,
        "tags": '["Dart", "Flutter-style Apps", "Mobile UX", "Performance"]',
    },
    {
        "module": "skills",
        "title": "Delivery",
        "slug": "delivery",
        "summary": "CI/CD, version control, and deployment",
        "body": "Git, CI/CD, Testing, Documentation, Deployment",
        "sort_order": 6,
        "tags": '["Git", "CI/CD", "Testing", "Documentation", "Deployment"]',
    },
    {
        "module": "services",
        "title": "Backend API Buildout",
        "slug": "backend-api-buildout",
        "summary": "Design and ship production-minded APIs, admin workflows, and database-backed services.",
        "body": "FastAPI and Python service delivery with clean route contracts, authentication, admin surfaces, uploads, reporting, and deployment-ready structure.",
        "sort_order": 1,
        "tags": '["FastAPI", "Python", "Admin Systems"]',
        "metadata_json": '{"timeline": "1-3 weeks", "deliverable": "Working backend and admin-ready API"}',
    },
    {
        "module": "services",
        "title": "AI and Automation Prototypes",
        "slug": "ai-automation-prototypes",
        "summary": "Turn AI ideas into usable assistants, agents, and workflow automations.",
        "body": "Prototype chatbots, recommendation bridges, data-assisted workflows, and deterministic fallback logic that can later connect to stronger AI engines.",
        "sort_order": 2,
        "tags": '["AI", "Agents", "Automation"]',
        "metadata_json": '{"timeline": "1-2 weeks", "deliverable": "Demo-ready prototype"}',
    },
    {
        "module": "services",
        "title": "Portfolio and Product Frontends",
        "slug": "portfolio-product-frontends",
        "summary": "Build polished Next.js interfaces for portfolios, dashboards, and product validation.",
        "body": "Responsive public pages, content-managed dashboards, forms, analytics hooks, and product-focused UI that is ready for deployment.",
        "sort_order": 3,
        "tags": '["Next.js", "React", "Product UI"]',
        "metadata_json": '{"timeline": "1-3 weeks", "deliverable": "Live frontend experience"}',
    },
    {
        "module": "testimonials",
        "title": "Operational Admin Work",
        "slug": "operational-admin-work",
        "summary": "Belmond thinks through the admin workflow, not just the screen.",
        "body": "The strongest part of the work is turning rough operational needs into usable management surfaces with real data, clear actions, and deployment-minded structure.",
        "sort_order": 1,
        "tags": '["Admin UX", "Backend", "Delivery"]',
        "metadata_json": '{"person": "Product collaborator", "role": "Operations-focused software"}',
    },
    {
        "module": "testimonials",
        "title": "Practical AI Delivery",
        "slug": "practical-ai-delivery",
        "summary": "AI features are framed as working product behavior first.",
        "body": "Instead of stopping at a concept, the implementation keeps the current app useful while leaving a clean path for stronger AI engines to connect later.",
        "sort_order": 2,
        "tags": '["AI", "Product", "Architecture"]',
        "metadata_json": '{"person": "Engineering collaborator", "role": "AI product build"}',
    },
    {
        "module": "credentials",
        "title": "Software Engineering",
        "slug": "software-engineering",
        "summary": "Backend services, frontend delivery, and product-focused implementation.",
        "body": "Practical software engineering across APIs, admin dashboards, content systems, integrations, and deployment workflows.",
        "sort_order": 1,
        "tags": '["Backend", "Frontend", "Full Stack"]',
        "metadata_json": '{"issuer": "Portfolio evidence", "year": "2026"}',
    },
    {
        "module": "credentials",
        "title": "Data Science and AI Systems",
        "slug": "data-science-ai-systems",
        "summary": "Applied data thinking, automation, agents, and AI-assisted product flows.",
        "body": "Experience shaping data and AI ideas into understandable, testable, and usable product features.",
        "sort_order": 2,
        "tags": '["Data Science", "AI", "Automation"]',
        "metadata_json": '{"issuer": "Portfolio evidence", "year": "2026"}',
    },
    {
        "module": "profile",
        "title": "Mufor Belmond Piannow",
        "slug": "main",
        "summary": "Software Engineer and Data Scientist",
        "body": "I build software, data systems, AI workflows, backend APIs, and mobile products from Cameroon with a practical, product-focused engineering style.",
        "image_url": "https://avatars.githubusercontent.com/u/161585619?v=4",
        "external_url": "info@muforbelmond.tech",
        "sort_order": 1,
        "tags": '[]',
    },
]


def seed_admin_user(db: Session) -> AdminUser:
    """Create or synchronize the configured admin account.

    This is committed separately from optional demo content so a failure while
    seeding that content cannot roll back the account needed to sign in.
    """
    settings = get_settings()
    email = settings.admin_email.strip().lower()
    if not email or not settings.admin_password:
        raise RuntimeError("ADMIN_EMAIL and ADMIN_PASSWORD must be configured")

    admin = (
        db.query(AdminUser)
        .filter(func.lower(AdminUser.email) == email)
        .first()
    )
    if not admin:
        admin = AdminUser(
            email=email,
            name="Mufor Belmond Piannow",
            hashed_password=get_password_hash(settings.admin_password),
        )
        db.add(admin)
    else:
        admin.email = email
        admin.name = admin.name or "Mufor Belmond Piannow"
        admin.is_active = True
        if not verify_password(settings.admin_password, admin.hashed_password):
            admin.hashed_password = get_password_hash(settings.admin_password)

    db.commit()
    db.refresh(admin)
    return admin


def seed_database(db: Session) -> None:
    seed_admin_user(db)

    for item in SEED_CONTENT:
        exists = (
            db.query(ContentItem)
            .filter(ContentItem.module == item["module"], ContentItem.slug == item["slug"])
            .first()
        )
        if not exists:
            row = {"status": "published", "metadata_json": "{}", "external_url": "", "image_url": "", **item}
            db.add(ContentItem(**row))
        elif (
            item["module"] == "profile"
            and item["slug"] == "main"
            and exists.external_url == "muforbelmond20@gmail.com"
        ):
            exists.external_url = "info@muforbelmond.tech"

    # Seed mock analytics data
    seed_mock_analytics(db, count=200)

    db.commit()
