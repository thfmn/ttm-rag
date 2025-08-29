## Brief overview
Development workflow preferences for the Thai Traditional Medicine RAG Bot project, emphasizing the use of uv package manager and manual package installation control.

## Package management
- Always use `uv` instead of `pip` for package management
- Never execute package installation commands directly - always instruct the user to run them
- Provide clear `uv pip install` commands for the user to execute manually
- When suggesting installations, format them as: `uv pip install <package-name>`

## Development workflow
- Request user confirmation before any system-level changes
- Provide clear instructions for manual execution of commands
- Document all dependency requirements explicitly
- Let servers be started manually by the user for testing purposes

## Communication style
- Be explicit about what needs to be installed and why
- Provide step-by-step instructions for manual tasks
- Clearly separate automated code changes from manual execution steps
- Always explain the purpose of each dependency before requesting installation

## Testing approach
- Test-driven development is preferred
- Unit tests and integration tests should be comprehensive
- FastAPI, Pydantic, and PydanticAI friendly implementations
- Document every step to maintain project tracking

## Project-specific guidelines
- This is a high-stakes project requiring careful documentation
- PostgreSQL database runs in Docker
- Focus on building production-ready, scalable solutions
- Maintain thorough documentation in all development phases
