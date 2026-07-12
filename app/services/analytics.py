import random
import http.client
import json
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.analytics import VisitorLog

# Mock lists for localhost / fallback
MOCK_LOCATIONS = [
    "New York, United States",
    "London, United Kingdom",
    "Berlin, Germany",
    "Tokyo, Japan",
    "Yaoundé, Cameroon",
    "Toronto, Canada",
    "Paris, France",
    "Sydney, Australia",
    "San Francisco, United States",
    "Douala, Cameroon"
]

MOCK_ISPS = [
    "Comcast Cable",
    "Verizon Fios",
    "BT Broadband",
    "Deutsche Telekom",
    "Camtel",
    "Orange Cameroun",
    "Rogers Communications",
    "Softbank Corp",
    "AT&T Internet",
    "MTN Cameroon"
]

MOCK_REFERRERS = [
    "https://github.com",
    "https://linkedin.com",
    "https://google.com",
    "https://twitter.com",
    "Direct",
    "Direct",
    "https://news.ycombinator.com"
]

MOCK_PATHS = [
    "/",
    "/",
    "/about",
    "/projects",
    "/projects/portfolio-platform",
    "/blog",
    "/blog/building-useful-software",
    "/gallery",
    "/contact"
]


def parse_user_agent(ua_string: str):
    """
    Simple rule-based parser for user agent to identify device, OS, and browser.
    """
    if not ua_string:
        return "Desktop", "Unknown", "Unknown"

    ua = ua_string.lower()

    # Device type
    if "ipad" in ua:
        device = "Tablet"
    elif "mobile" in ua or "android" in ua or "iphone" in ua:
        device = "Mobile"
    else:
        device = "Desktop"

    # OS
    if "windows" in ua:
        os = "Windows"
    elif "macintosh" in ua or "mac os" in ua:
        os = "MacOS"
    elif "iphone" in ua or "ipad" in ua:
        os = "iOS"
    elif "android" in ua:
        os = "Android"
    elif "linux" in ua:
        os = "Linux"
    else:
        os = "Unknown"

    # Browser
    if "edg/" in ua or "edge" in ua:
        browser = "Edge"
    elif "chrome" in ua or "crios" in ua:
        # Chrome contains 'safari' and 'chrome', so check chrome first
        browser = "Chrome"
    elif "safari" in ua:
        browser = "Safari"
    elif "firefox" in ua or "fxios" in ua:
        browser = "Firefox"
    else:
        browser = "Unknown"

    return device, os, browser


def get_ip_info(ip: str):
    """
    Get location and ISP from ip-api.com. Fallback to mock data for local IPs or errors.
    """
    if not ip or ip in ("127.0.0.1", "::1", "localhost") or ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
        return random.choice(MOCK_LOCATIONS), random.choice(MOCK_ISPS)

    try:
        # Use http.client for a no-dependency request with a timeout
        conn = http.client.HTTPConnection("ip-api.com", timeout=1.5)
        conn.request("GET", f"/json/{ip}?fields=status,country,city,isp")
        response = conn.getresponse()
        if response.status == 200:
            data = json.loads(response.read().decode())
            if data.get("status") == "success":
                city = data.get("city", "")
                country = data.get("country", "")
                location = f"{city}, {country}" if city and country else (country or city or "Unknown")
                isp = data.get("isp", "Unknown")
                return location, isp
    except Exception:
        pass

    return random.choice(MOCK_LOCATIONS), random.choice(MOCK_ISPS)


def log_visitor(db: Session, ip_address: str, path: str, referrer: str, user_agent: str) -> VisitorLog:
    device_type, os, browser = parse_user_agent(user_agent)
    location, isp = get_ip_info(ip_address)

    log = VisitorLog(
        ip_address=ip_address,
        path=path,
        referrer=referrer or "Direct",
        user_agent=user_agent or "",
        device_type=device_type,
        os=os,
        browser=browser,
        location=location,
        isp=isp
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_analytics_stats(db: Session):
    """
    Fetch analytics aggregated statistics for dashboard charts and cards.
    """
    total_views = db.query(VisitorLog).count()
    unique_visitors = db.query(func.count(func.distinct(VisitorLog.ip_address))).scalar() or 0

    # Device type breakdown
    devices = (
        db.query(VisitorLog.device_type, func.count(VisitorLog.id))
        .group_by(VisitorLog.device_type)
        .all()
    )
    device_stats = {d: count for d, count in devices}

    # Browser breakdown
    browsers = (
        db.query(VisitorLog.browser, func.count(VisitorLog.id))
        .group_by(VisitorLog.browser)
        .order_by(func.count(VisitorLog.id).desc())
        .limit(5)
        .all()
    )
    browser_stats = {b: count for b, count in browsers}

    # Location breakdown
    locations = (
        db.query(VisitorLog.location, func.count(VisitorLog.id))
        .group_by(VisitorLog.location)
        .order_by(func.count(VisitorLog.id).desc())
        .limit(5)
        .all()
    )
    location_stats = {loc: count for loc, count in locations}

    # ISP breakdown
    isps = (
        db.query(VisitorLog.isp, func.count(VisitorLog.id))
        .group_by(VisitorLog.isp)
        .order_by(func.count(VisitorLog.id).desc())
        .limit(5)
        .all()
    )
    isp_stats = {isp: count for isp, count in isps}

    # Referrer breakdown
    referrers = (
        db.query(VisitorLog.referrer, func.count(VisitorLog.id))
        .group_by(VisitorLog.referrer)
        .order_by(func.count(VisitorLog.id).desc())
        .limit(5)
        .all()
    )
    referrer_stats = {ref: count for ref, count in referrers}

    # Views per path
    paths = (
        db.query(VisitorLog.path, func.count(VisitorLog.id))
        .group_by(VisitorLog.path)
        .order_by(func.count(VisitorLog.id).desc())
        .limit(5)
        .all()
    )
    path_stats = {path: count for path, count in paths}

    # Views over last 7 days (by date)
    # Since we are using SQLite, we can extract the date from created_at
    # Let's aggregate views per day
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    views_by_date = (
        db.query(func.date(VisitorLog.created_at), func.count(VisitorLog.id))
        .filter(VisitorLog.created_at >= seven_days_ago)
        .group_by(func.date(VisitorLog.created_at))
        .order_by(func.date(VisitorLog.created_at).asc())
        .all()
    )
    views_over_time = [{"date": date_str, "views": count} for date_str, count in views_by_date]

    return {
        "total_views": total_views,
        "unique_visitors": unique_visitors,
        "device_stats": device_stats,
        "browser_stats": browser_stats,
        "location_stats": location_stats,
        "isp_stats": isp_stats,
        "referrer_stats": referrer_stats,
        "path_stats": path_stats,
        "views_over_time": views_over_time
    }


def seed_mock_analytics(db: Session, count: int = 150):
    """
    Generate realistic analytics visitor logs for the past 30 days.
    """
    # Check if we already have logs
    if db.query(VisitorLog).count() > 10:
        return

    now = datetime.now(timezone.utc)
    devices_pool = ["Desktop"] * 60 + ["Mobile"] * 30 + ["Tablet"] * 10
    os_pool = {
        "Desktop": ["Windows", "MacOS", "Linux"],
        "Mobile": ["Android", "iOS"],
        "Tablet": ["iOS", "Android"]
    }
    browser_pool = {
        "Desktop": ["Chrome", "Firefox", "Safari", "Edge"],
        "Mobile": ["Chrome", "Safari"],
        "Tablet": ["Safari", "Chrome"]
    }

    # Create logs distributed over the past 30 days
    for _ in range(count):
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        log_time = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

        # Generate fake IP
        ip_parts = [str(random.randint(1, 254)) for _ in range(4)]
        ip_address = ".".join(ip_parts)

        device = random.choice(devices_pool)
        os = random.choice(os_pool[device])
        browser = random.choice(browser_pool[device])

        log = VisitorLog(
            ip_address=ip_address,
            path=random.choice(MOCK_PATHS),
            referrer=random.choice(MOCK_REFERRERS),
            user_agent=f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) {browser}",
            device_type=device,
            os=os,
            browser=browser,
            location=random.choice(MOCK_LOCATIONS),
            isp=random.choice(MOCK_ISPS),
            created_at=log_time
        )
        db.add(log)

    db.commit()
