# CareerVoice AI Deployment

This repository assembles the complete CareerVoice AI application for cloud deployment.

The original CareerVoice AI repositories remain separate development and portfolio repositories. This deployment repository contains clean, tested package snapshots required to run the complete application in one hosted environment.

## Intended deployment

The initial deployment target is Streamlit Community Cloud.

The first release will be used as a private supervisor demonstration.

## Components

The deployed application will include:

- career-profile extraction;
- voice and document processing;
- current job collection;
- preference-aware job recommendations;
- workflow coordination;
- the Streamlit web interface.

## Repository role

This repository is an assembly and hosting repository.

Feature development and bug fixes should normally be completed in the relevant original repository first. Approved versions are then synchronized into this deployment repository.

## Security

Never commit:

- `.env`;
- `.streamlit/secrets.toml`;
- API keys;
- virtual environments;
- runtime user files;
- generated outputs;
- caches;
- local IDE files.

## Current status

Step 15C: career-profile extractor, job-recommender, and job-collector deployment snapshots imported.