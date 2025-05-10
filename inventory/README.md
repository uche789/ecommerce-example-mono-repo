# Product data

Commands: 
```bash
# Install requirements
pip install -r requirements.txt

# Save requirements
pip freeze > requirements.txt

# run
fastapi dev main.py
```

## Things to improve
- Crud operations

## API key
An API key is required to context to the api. Generate API key using `openssl rand -hex 32` (unix systems) and add the new key to `.env` file