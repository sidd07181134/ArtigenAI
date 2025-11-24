# Azure Web App Setup Guide

## Prerequisites

1. **Quota Increase**: Your Azure student account needs App Service quota. Request it here:
   - https://portal.azure.com → Subscriptions → Your Subscription → Usage + quotas → App Service → Request increase

2. **Service Principal**: You need Azure credentials for GitHub Actions (see instructions below)

## Method 1: Create via Azure Portal (Recommended if quota is available)

### Step 1: Create App Service Plan

1. Go to: https://portal.azure.com
2. Search for "App Service plans" → Create
3. Configure:
   - **Subscription**: Your subscription
   - **Resource Group**: `aigov_group`
   - **Name**: `aigov-app-plan`
   - **Operating System**: Linux
   - **Region**: West US 2 (or your preferred region)
   - **Pricing tier**: Basic B1 (or Free F1 if available)
4. Click "Review + create" → "Create"

### Step 2: Create Web App

1. Go to: https://portal.azure.com/#create/Microsoft.WebSite
2. Configure:
   - **Subscription**: Your subscription
   - **Resource Group**: `aigov_group`
   - **Name**: `aigov-webapp` (must be globally unique, try variations like `aigov-webapp-2024`)
   - **Publish**: Docker Container
   - **Operating System**: Linux
   - **Region**: West US 2
   - **App Service Plan**: Select `aigov-app-plan` (created in Step 1)
3. Click "Next: Docker"
4. Configure Docker:
   - **Options**: Single Container
   - **Image Source**: Docker Hub or other registries
   - **Access Type**: Public
   - **Full Image Name and Tag**: `ghcr.io/sidd07181134/artigenai/aigov-app:latest`
     - Note: Update this with your actual GitHub Container Registry path after first deployment
5. Click "Review + create" → "Create"

### Step 3: Configure Environment Variables

1. Go to your Web App → Configuration → Application settings
2. Add these environment variables:
   - `DATABASE_URL`: Your database connection string
   - `SECRET_KEY`: Generate with `openssl rand -hex 32`
   - `GROQ_API_KEY`: Your Groq API key
   - `QDRANT_URL`: Your Qdrant URL
   - `QDRANT_API_KEY`: Your Qdrant API key (if using Qdrant Cloud)
   - `CORS_ORIGINS`: `*` (or specific origins)
   - `ENVIRONMENT`: `production`
3. Click "Save"

### Step 4: Configure Container Registry (if using private registry)

1. Go to your Web App → Deployment Center
2. Configure:
   - **Source**: Container Registry
   - **Registry**: GitHub Container Registry
   - **Image**: `ghcr.io/sidd07181134/artigenai/aigov-app:latest`
   - **Tag**: `latest` or specific tag
3. For authentication, you may need to set up managed identity or registry credentials

## Method 2: Create via Azure CLI (After quota increase)

Run the provided PowerShell script:

```powershell
.\create-azure-webapp.ps1
```

Or manually:

```bash
# Create App Service Plan
az appservice plan create \
  --name aigov-app-plan \
  --resource-group aigov_group \
  --location westus2 \
  --is-linux \
  --sku B1

# Create Web App
az webapp create \
  --name aigov-webapp \
  --resource-group aigov_group \
  --plan aigov-app-plan \
  --deployment-container-image-name ghcr.io/sidd07181134/artigenai/aigov-app:latest
```

## Configure GitHub Secrets

After creating the Web App, set these secrets in GitHub:

1. Go to: https://github.com/sidd07181134/ArtigenAI/settings/secrets/actions

2. Add `AZURE_WEBAPP_NAME`:
   - Value: Your Web App name (e.g., `aigov-webapp`)

3. Add `AZURE_CREDENTIALS`:
   - See service principal setup instructions below

## Service Principal Setup

Since CLI creation failed due to permissions, use Azure Portal:

1. Go to: https://portal.azure.com → Azure Active Directory → App registrations
2. Click "New registration"
3. Name: `aigov-github-actions`
4. Click "Register"
5. Note the **Application (client) ID** and **Directory (tenant) ID**
6. Go to "Certificates & secrets" → "New client secret"
7. Create a secret and **copy the value immediately**
8. Go to "Subscriptions" → Your subscription → "Access control (IAM)"
9. Click "Add role assignment"
10. Role: **Contributor**
11. Assign to: **aigov-github-actions** (the app you just created)
12. Create the `AZURE_CREDENTIALS` secret in GitHub with:

```json
{
  "clientId": "your-application-client-id",
  "clientSecret": "your-client-secret-value",
  "subscriptionId": "06659840-49e8-4bfb-8538-f2c65ea30fcd",
  "tenantId": "fa6944af-cc7c-4cd8-9154-c01132798910"
}
```

## Verify Deployment

After setting up everything:

1. Push to `Version-0.1` branch
2. Check GitHub Actions: https://github.com/sidd07181134/ArtigenAI/actions
3. Once deployed, access: `https://your-webapp-name.azurewebsites.net`

## Troubleshooting

### Quota Issues
- Request quota increase in Azure Portal
- Try different regions
- Use Free tier if available

### Container Issues
- Check Web App logs: Portal → Your Web App → Log stream
- Verify image exists in GitHub Container Registry
- Check environment variables are set correctly

### Permission Issues
- Ensure service principal has Contributor role
- Verify GitHub secrets are set correctly
- Check Azure subscription is active

