terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "~> 0.84"
    }
  }
}

# Провайдер - Yandex Cloud
provider "yandex" {
  service_account_key_file = "/home/diana/terraform-key.json"
  folder_id                = var.folder_id
  zone                     = "ru-central1-a"
}

# Образ - Ubuntu 22.04
data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

# Создаём виртуальную сеть
resource "yandex_vpc_network" "network" {
  name = "task-manager-network"
}

# Создаём подсеть
resource "yandex_vpc_subnet" "subnet" {
  name           = "task-manager-subnet"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.network.id
  v4_cidr_blocks = ["10.0.1.0/24"]
}

# Создаём виртуальную машину
resource "yandex_compute_instance" "vm" {
  name        = "task-manager-vm"
  platform_id = "standard-v3"  
  zone        = "ru-central1-a"

  resources {
    cores  = 2  
    memory = 4     
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = 20 
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet.id
    nat       = true   # У VM будет публичный IP
  }

  metadata = {
    ssh-keys = "ubuntu:${file(var.ssh_public_key_path)}"
  }
}
