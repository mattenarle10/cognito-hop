# SSO Backend

This is the SSO backend for the Cognito SSO project. It handles user authentication, session management, and application authorization.

## Architecture

The SSO backend follows a clean, modular architecture with the following components:

- **Handlers**: Lambda function entry points
  - **Triggers**: Cognito triggers (e.g., post-confirmation)
  - **HTTP**: API Gateway endpoints
- **Domains**: Business logic
- **Services**: External service integrations
  - **AWS**: AWS service wrappers
  - **Repositories**: Data access layer
- **Utils**: Utility functions

## Environment Setup

1. Create a `.env.dev.yml` file with the following environment variables:
   ```yaml
   MAIN_TABLE: ur main db table name
   COGNITO_USER_POOL_ID: user pool id
   COGNITO_APP_CLIENT_ID: ur client id
   ```

## Deployment

### Prerequisites
- Node.js and npm installed
- Serverless Framework v4 installed: `npm install -g serverless`
- AWS CLI configured with appropriate credentials

### Deploy to AWS
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Serverless plugins
npm install

# Deploy to dev environment
serverless deploy --stage dev
```

