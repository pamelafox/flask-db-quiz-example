targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Id of the user or app to assign application roles')
param principalId string

@description('Whether the deployment is running on GitHub Actions')
param runningOnGh string = ''

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

var prefix = '${name}-${resourceToken}'

var postgresServerName = '${prefix}-postgresql'
var postgresDatabaseName = 'flask'
var postgresEntraAdministratorObjectId = principalId
var postgresEntraAdministratorType = empty(runningOnGh) ? 'User' : 'ServicePrincipal'
var postgresEntraAdministratorName = 'admin${uniqueString(resourceGroup.id, principalId)}'

module postgresServer 'core/database/postgresql/flexibleserver.bicep' = {
  name: 'postgresql'
  scope: resourceGroup
  params: {
    name: postgresServerName
    location: location
    tags: tags
    sku: {
      name: 'Standard_B1ms'
      tier: 'Burstable'
    }
    storage: {
      storageSizeGB: 32
    }
    version: '13'
    authType: 'EntraOnly'
    entraAdministratorName: postgresEntraAdministratorName
    entraAdministratorObjectId: postgresEntraAdministratorObjectId
    entraAdministratorType: postgresEntraAdministratorType
    databaseNames: [postgresDatabaseName]
    allowAzureIPsFirewall: true
    allowAllIPsFirewall: true // Necessary for post-provision script, can be disabled after
  }
}

var webAppName = '${prefix}-appservice'
module web 'core/host/appservice.bicep' = {
  name: 'appservice'
  scope: resourceGroup
  params: {
    name: webAppName
    location: location
    tags: union(tags, { 'azd-service-name': 'web' })
    appServicePlanId: appServicePlan.outputs.id
    runtimeName: 'python'
    runtimeVersion: '3.11'
    scmDoBuildDuringDeployment: true
    ftpsState: 'Disabled'
    appCommandLine: 'startup.sh'
    managedIdentity: true
    use32BitWorkerProcess: true
    alwaysOn: false
    appSettings: {
      DBHOST: postgresServerName
      DBNAME: postgresDatabaseName
      DBUSER: webAppName
    }
  }
}

module appServicePlan 'core/host/appserviceplan.bicep' = {
  name: 'serviceplan'
  scope: resourceGroup
  params: {
    name: '${prefix}-serviceplan'
    location: location
    tags: tags
    sku: {
      name: 'B1'
    }
    reserved: true
  }
}

module logAnalyticsWorkspace 'core/monitor/loganalytics.bicep' = {
  name: 'loganalytics'
  scope: resourceGroup
  params: {
    name: '${prefix}-loganalytics'
    location: location
    tags: tags
  }
}

output WEB_APP_NAME string = webAppName
output WEB_URI string = web.outputs.uri
output AZURE_LOCATION string = location

output POSTGRES_DOMAIN_NAME string = postgresServer.outputs.POSTGRES_DOMAIN_NAME
output POSTGRES_ADMIN_USERNAME string = postgresEntraAdministratorName
