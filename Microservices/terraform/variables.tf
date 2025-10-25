variable "resource_group_name" {
  default     = "Pwc-DevOps-Task"
  description = "Existing resource group name"
}

variable "location" {
  default     = "uaenorth"
  description = "Azure region for AKS"
}

variable "aks_cluster_name" {
  default     = "pwc-aks"
  description = "AKS cluster name"
}

variable "dns_prefix" {
  default     = "pwc-aks"
  description = "DNS prefix for AKS"
}

variable "node_count" {
  default = 3
}

variable "node_vm_size" {
  default = "Standard_B2s"
}

variable "acr_name" {
  default     = "pwcregistry"
  description = "Existing Azure Container Registry name (without .azurecr.io)"
}


