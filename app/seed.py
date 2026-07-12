from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_password_hash
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
        "module": "profile",
        "title": "Mufor Belmond Piannow",
        "slug": "main",
        "summary": "Software Engineer and Data Scientist",
        "body": "I build software, data systems, AI workflows, backend APIs, and mobile products from Cameroon with a practical, product-focused engineering style.",
        "image_url": "https://avatars.githubusercontent.com/u/161585619?v=4",
        "external_url": "muforbelmond20@gmail.com",
        "sort_order": 1,
        "tags": '[]',
    },
]


def seed_database(db: Session) -> None:
    settings = get_settings()
    admin = db.query(AdminUser).filter(AdminUser.email == settings.admin_email).first()
    if not admin:
        db.add(
            AdminUser(
                email=settings.admin_email,
                name="Mufor Belmond Piannow",
                hashed_password=get_password_hash(settings.admin_password),
            )
        )

    for item in SEED_CONTENT:
        exists = (
            db.query(ContentItem)
            .filter(ContentItem.module == item["module"], ContentItem.slug == item["slug"])
            .first()
        )
        if not exists:
            row = {"status": "published", "metadata_json": "{}", "external_url": "", "image_url": "", **item}
            db.add(ContentItem(**row))

    # Seed mock analytics data
    seed_mock_analytics(db, count=200)

    db.commit()
