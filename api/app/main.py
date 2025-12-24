"""Main FastAPI application factory and configuration."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import hash_password
from app.models.database import User, FileShare, AccessLog
from app.routes import auth, files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def seed_demo_user():
    """Create demo user if it does not already exist."""
    demo_email = "demo@secureshare.com"
    demo_username = "demo"
    demo_password = "DemoPass123!"

    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(
            (User.email == demo_email) | (User.username == demo_username)
        ).first()

        if existing_user:
            logger.info("Demo user already exists")
            return

        db_user = User(
            username=demo_username,
            email=demo_email,
            hashed_password=hash_password(demo_password)
        )
        db.add(db_user)
        db.commit()
        logger.info("Seeded demo user for quick access")
    except Exception as exc:  # pragma: no cover - startup guardrail
        logger.error("Failed to seed demo user: %s", exc)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    seed_demo_user()
    logger.info("Application started")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description="Secure Document & Link Sharing Platform API",
        lifespan=lifespan
    )
    
    # CORS middleware for frontend integration
    cors_kwargs = {
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    if settings.ALLOW_ALL_CORS:
        cors_kwargs["allow_origins"] = ["*"]
    else:
        # Include explicit origins (e.g., localhost) and allow common public hosts via regex
        cors_kwargs["allow_origins"] = settings.ALLOWED_ORIGINS + (
            [settings.FRONTEND_URL] if settings.FRONTEND_URL else []
        )
        cors_kwargs["allow_origin_regex"] = settings.ALLOWED_ORIGIN_REGEX

    app.add_middleware(CORSMiddleware, **cors_kwargs)
    
    # Include routers
    app.include_router(auth.router)
    app.include_router(files.router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for deployment monitoring."""
        return {
            "status": "healthy",
            "version": settings.API_VERSION
        }
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Root: redirect to frontend if configured, else show a simple landing."""
        if settings.FRONTEND_URL:
            return RedirectResponse(url=settings.FRONTEND_URL, status_code=307)
        # Fallback lightweight landing page
        html = f"""
        <!DOCTYPE html>
        <html lang=\"en\">
        <head>
            <meta charset=\"UTF-8\" />
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
            <title>{settings.API_TITLE}</title>
            <style>
                body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial; margin: 40px; color: #222; }}
                .card {{ max-width: 680px; margin: 0 auto; padding: 28px; border: 1px solid #eee; border-radius: 12px; box-shadow: 0 6px 24px rgba(0,0,0,0.06); }}
                h1 {{ margin: 0 0 8px; font-size: 24px; }}
                .muted {{ color: #666; margin: 0 0 20px; }}
                a.btn {{ display: inline-block; background: #5b6ef5; color: #fff; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-weight: 600; }}
                .links a {{ margin-right: 16px; }}
            </style>
        </head>
        <body>
            <div class=\"card\">
                <h1>{settings.API_TITLE}</h1>
                <p class=\"muted\">API is running (v{settings.API_VERSION}).</p>
                <div class=\"links\">
                    <a class=\"btn\" href=\"/docs\">Open API Docs</a>
                    <a href=\"/health\">Health</a>
                    <a href=\"/openapi.json\">OpenAPI</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    
    return app


# Create application instance
app = create_app()
