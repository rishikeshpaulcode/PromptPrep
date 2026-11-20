# Feature: Migrate from Gemini API to NVIDIA NIM API

## Requirement
Currently, the app internally uses the Google Gemini chatmodel to generate questions and session feedback. Problem is that its free tier is limited to a maximum of 20 API calls per day. This will later cause scalability issues. Hence, migrate to a more generous alternative: NVIDIA NIM API.


## Design
### New components:
No new components are required. The existing components will be updated to use NVIDIA NIM API instead of Gemini API.

### Components affected:
- **.env**: Update the .env file to include a template where i can include my NVIDIA NIM API credentials.
- **requirements**: Update the requirements.txt to include NVIDIA NIM API SDK and remove Google Gemini API SDK.
- **models**: Update the models to use NVIDIA NIM API instead of Gemini API. Use the "mistralai/mistral-large-4-1t-a52b" model.


## Out of scope
- Do not change the existing API endpoints or their functionality.
- Do not change the existing Pydantic data models or their structure.
- Do not change the existing Prompt Templates.