# Project

This repository contains:

- **backend/** - FastAPI Python application
- **infrastructure/** - AWS CDK Infrastructure as Code

## Getting Started

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Infrastructure
```bash
cd infrastructure
pip install -r requirements.txt
cdk synth
```
