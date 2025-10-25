terraform {
  required_version = ">= 1.4.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0.0"
    }

    azapi = {
      source  = "Azure/azapi"
      version = "~> 1.5"
    }
  }
}

provider "azurerm" {
  features {}
  
}
