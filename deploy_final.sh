#!/bin/bash
# --- THE STUDENT-READY CONFIG ---
UNIQUE_ID=$((1000 + RANDOM % 9000))
RESOURCE_GROUP="Hydrogen_Final_Project_RG_$UNIQUE_ID" 
LOCATION="westus2" 
ACR_NAME="abdulhydrogen$UNIQUE_ID" 
CONTAINER_IMAGE="hydrogen-agent:v1"
DNS_LABEL="hydrogen-ai-agent-$UNIQUE_ID"

echo "🔐 Step 1: Logging into Azure..."
az login

echo "📁 Step 2: Creating Resource Group in $LOCATION..."
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "📦 Step 3: Creating Registry ($ACR_NAME)..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true --location $LOCATION

if [ $? -ne 0 ]; then
    echo "❌ ACR Failed. Your student sub has a very strict regional lock."
    exit 1
fi

echo "🏗️ Step 4: Building Image in the Cloud (This takes 3-5 mins)..."
az acr build --registry $ACR_NAME --image $CONTAINER_IMAGE .

echo "🔑 Step 5: Fetching Credentials..."
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)

echo "🚀 Step 6: Deploying Container Instance..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name hydrogen-agent-service \
    --image $ACR_NAME.azurecr.io/$CONTAINER_IMAGE \
    --cpu 1 --memory 1.5 \
    --registry-login-server $ACR_NAME.azurecr.io \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --environment-variables OPENAI_API_KEY=$OPENAI_API_KEY \
    --ip-address Public \
    --ports 8000 \
    --dns-name-label $DNS_LABEL \
    --location $LOCATION

echo "⏳ Step 7: Final Status Check..."
sleep 20
az container show --resource-group $RESOURCE_GROUP --name hydrogen-agent-service --query "{URL:ipAddress.fqdn, State:instanceView.state}" --output table
