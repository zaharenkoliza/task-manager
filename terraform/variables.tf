variable "folder_id" {
  description = "Yandex Cloud folder ID"
  type        = string
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key"
  type        = string
  default     = "~/.ssh/yc_vm.pub"
}