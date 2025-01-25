provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_compute_instance" "vm_instance" {
  name         = "multi-cloud-gcp-vm"
  machine_type = var.vm_size

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y python3 python3-pip
    pip3 install flask
    echo "Hello from GCP!" > /var/www/html/index.html
    nohup python3 -m flask run --host=0.0.0.0 --port=80 &
  EOF
}