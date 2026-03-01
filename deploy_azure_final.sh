#!/bin/bash
# --- SETTINGS ---
UNIQUE_ID=$((1000 + RANDOM % 9000))
RESOURCE_GROUP="Hydrogen_Final_Project_RG"
LOCATION="westeurope" 
ACR_NAME="abdulreg$UNIQUE_ID"
WEB_APP_NAME="hydrogen-agent-$UNIQUE_ID"
PLAN_NAME="hydrogen-plan-$UNIQUE_ID"

echo "🔐 Step 1: Login..."
az login

echo "📁 Step 2: Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "📦 Step 3: Creating Registry..."
# We use 'Basic' SKU which is the cheapest/easiest for students
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true --location $LOCATION

echo "🏗️ Step 4: Building Image (Cloud-side)..."
# This sends your code and PDFs to Azure to build the Docker image
az acr build --registry $ACR_NAME --image hydrogen-agent:v1 .

echo "🚀 Step 5: Deploying as a Web App..."
# Create a Linux Service Plan (B1 is usually included in Student credits)
az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku B1 --is-linux --location $LOCATION

# Create the Web App using your new image
az webapp create --resource-group $RESOURCE_GROUP --plan $PLAN_NAME --name $WEB_APP_NAME --deployment-container-image-name $ACR_NAME.azurecr.io/hydrogen-agent:v1

# Set the Port and API Key
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --settings WEBSITES_PORT=8000 OPENAI_API_KEY=$OPENAI_API_KEY

echo "✅ SUCCESS! Your URL is: https://$WEB_APP_NAME.azurewebsites.net/docs"
