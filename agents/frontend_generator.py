"""
SystemCrafter AI - Frontend Generator Agent
Generates Next.js frontend code from OpenAPI spec.
"""
import json
from typing import Any

from agents.base import AgentConfig, BaseAgent
from orchestrator.core import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a front-end engineer. Generate a complete Next.js 14 frontend application with App Router.

Output ONLY valid JSON matching this schema:
{
  "files": {
    "path/to/file.tsx": "file content as string",
    "path/to/file.ts": "file content"
  },
  "pages": [
    {
      "path": "/route",
      "component": "ComponentName",
      "description": "What this page does"
    }
  ],
  "components": [
    {
      "name": "ComponentName",
      "path": "components/ComponentName.tsx",
      "description": "What this component does"
    }
  ],
  "dependencies": {
    "dependencies": {"package": "version"},
    "devDependencies": {"package": "version"}
  }
}

FRONTEND STRUCTURE (Next.js 14 App Router):
src/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page
│   ├── globals.css          # Global styles
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── dashboard/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   └── [entity]/
│       ├── page.tsx         # List view
│       └── [id]/page.tsx    # Detail view
├── components/
│   ├── ui/                  # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── Modal.tsx
│   ├── forms/               # Form components
│   └── layout/              # Layout components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── lib/
│   ├── api.ts               # API client
│   ├── auth.ts              # Auth utilities
│   └── utils.ts             # Utility functions
├── hooks/
│   ├── useAuth.ts
│   └── useApi.ts
├── types/
│   └── index.ts             # TypeScript types from OpenAPI
└── styles/
    └── *.css

REQUIREMENTS:
- Use Next.js 14 App Router with Server Components where appropriate
- Use TypeScript throughout
- Style with Tailwind CSS
- Generate API client from OpenAPI spec using fetch
- Implement authentication with JWT stored in httpOnly cookies or localStorage
- Use React Hook Form for forms with zod validation
- Include loading states and error handling
- Create responsive layouts (mobile-first)
- Include proper TypeScript types
- Add basic E2E test setup with Playwright
- Use shadcn/ui style components (but generate inline, don't import)
- Include proper meta tags and SEO

PAGES TO INCLUDE:
- Landing/Home page
- Login and Register pages
- Dashboard (authenticated)
- CRUD pages for each entity (list, detail, create, edit)
- 404 and error pages

Generate modern, clean, production-ready React code."""


class FrontendGeneratorAgent(BaseAgent):
    """
    Agent that generates Next.js frontend code.
    """
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="Frontend Generator",
            description="Generates Next.js frontend code from OpenAPI specifications",
            temperature=0.2,
            max_tokens=16384,  # Large output for complete frontend
        )
        super().__init__(config)
    
    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT
    
    def build_user_prompt(self, input_data: dict) -> str:
        """Build prompt from OpenAPI spec."""
        openapi_yaml = input_data.get("openapi_yaml", "")
        ui_preferences = input_data.get("ui_preferences", {})
        
        prompt = f"OpenAPI Specification:\n```yaml\n{openapi_yaml}\n```"
        
        if ui_preferences:
            prompt += f"\n\nUI Preferences:\n{json.dumps(ui_preferences, indent=2)}"
        
        return prompt
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate that OpenAPI is provided."""
        if "openapi_yaml" not in input_data:
            logger.error("Missing required field: openapi_yaml")
            return False
        return True
    
    def validate_output(self, output: dict) -> bool:
        """Validate output has required fields."""
        if "files" not in output:
            logger.error("Missing required output field: files")
            return False
        if "pages" not in output:
            logger.error("Missing required output field: pages")
            return False
        return True
    
    def parse_response(self, response: str) -> dict:
        """Parse JSON response from LLM."""
        try:
            return self._safe_json_parse(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
