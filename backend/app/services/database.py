from app.core.config import settings


def get_database_mode() -> str:
    uri = settings.SQLALCHEMY_DATABASE_URI
    if uri.startswith("sqlite"):
        return "sqlite"
    if "supabase.co" in uri:
        return "supabase"
    if uri.startswith("postgresql"):
        return "postgresql"
    return "unknown"
