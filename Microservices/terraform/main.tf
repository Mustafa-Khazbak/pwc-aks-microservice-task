# Reference existing resource group
data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

# Reference existing ACR
data "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = data.azurerm_resource_group.rg.name
}

# Get info about the logged-in Azure user 
data "azurerm_client_config" "current" {}

# Create the AKS cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_cluster_name
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  dns_prefix          = var.dns_prefix

  default_node_pool {
    name       = "systempool"
    node_count = var.node_count
    vm_size    = var.node_vm_size
  }

  # Enable managed identity 
  identity {
    type = "SystemAssigned"
  }

  linux_profile {
    admin_username = "azureuser"

    ssh_key {
      key_data = azapi_resource_action.ssh_public_key_gen.output.publicKey
    }
  }

  # Network configuration
  network_profile {
    network_plugin = "azure"
  }

  # Enable RBAC 
   role_based_access_control_enabled = true

  tags = {
    environment = "prod"
    owner       = "mustafa"
    project     = "pwc-microservice"
  }
}

# Grant AKS permission to pull from your ACR
resource "azurerm_role_assignment" "acr_pull" {
  scope                = data.azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id

  depends_on = [azurerm_kubernetes_cluster.aks]
}
