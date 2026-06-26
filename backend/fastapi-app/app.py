import uvicorn
from src.shared.core.properties.app_properties import settings
from src.api.main import app


if __name__ == "__main__":
    # Determine reload based on local/development environment
    reload_enabled = settings.app.env == "local"
    
    # Run the application
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload_enabled
    )
