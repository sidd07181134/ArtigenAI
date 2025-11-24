# Script to create Azure Web App for Containers
# Run this after your quota is increased or if you have sufficient permissions

$resourceGroup = "aigov_group"
$location = "westus2"
$appServicePlanName = "aigov-app-plan"
$webAppName = "aigov-webapp"  # Change this to your preferred name (must be globally unique)
$dockerImage = "ghcr.io/sidd07181134/artigenai/aigov-app:latest"  # Update with your actual image path

Write-Host "Creating App Service Plan..." -ForegroundColor Green
az appservice plan create `
    --name $appServicePlanName `
    --resource-group $resourceGroup `
    --location $location `
    --is-linux `
    --sku B1 `
    --output json

if ($LASTEXITCODE -eq 0) {
    Write-Host "App Service Plan created successfully!" -ForegroundColor Green
    
    Write-Host "Creating Web App for Containers..." -ForegroundColor Green
    az webapp create `
        --name $webAppName `
        --resource-group $resourceGroup `
        --plan $appServicePlanName `
        --deployment-container-image-name $dockerImage `
        --output json
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Web App created successfully!" -ForegroundColor Green
        
        Write-Host "Configuring container settings..." -ForegroundColor Green
        az webapp config container set `
            --name $webAppName `
            --resource-group $resourceGroup `
            --docker-custom-image-name $dockerImage `
            --output json
        
        Write-Host "`n=== Web App Details ===" -ForegroundColor Cyan
        Write-Host "Web App Name: $webAppName" -ForegroundColor Yellow
        Write-Host "URL: https://$webAppName.azurewebsites.net" -ForegroundColor Yellow
        Write-Host "`nNext steps:" -ForegroundColor Green
        Write-Host "1. Set GitHub secret AZURE_WEBAPP_NAME = $webAppName" -ForegroundColor White
        Write-Host "2. Configure environment variables in Azure Portal" -ForegroundColor White
        Write-Host "3. Push to Version-0.1 branch to trigger deployment" -ForegroundColor White
    }
} else {
    Write-Host "Failed to create App Service Plan. Check your quota limits." -ForegroundColor Red
}

