# cognito-hop
🐇 Vue + Vite ,  Serverless + Python equipped for AWS Cognito SSO Implementation starter template 


## Project Structure

```
/cognito-hop/
├── backend/
│   ├── sso_backend/         # SSO backend services
│   |── admin_backend/       # Admin-specific APIs
│   └── client_backend/      # Client application backend
└── frontend/
    ├── sso_frontend/        # SSO interface (Vue.js)
    ├── admin_portal/        # Admin portal (Vue 3 + Vite)
    └── client_app/          # Client application UI (Vue.js)
```

### Backend Setup

```bash
# SSO Backend, Client Backend, Admin Portal, 
cd backend/sso_backend, client_backend, admin_backend
export AWS_PROFILE={your-profile}
npm install
sls deploy
```

### Frontend Setup

```bash
# SSO Frontend
cd frontend/sso_frontend, client_app, admin_portal
npm install
npm run dev
```


## AWS Resources

- **Cognito User Pool** - Authentication management
- **DynamoDB Tables** - Data storage
- **Lambda Functions** - Serverless computing
- **API Gateway** - API management
