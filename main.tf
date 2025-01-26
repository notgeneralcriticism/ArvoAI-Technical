
        provider "google" {
            project = "arvoaitechnical"
            region  = "us-central1-a"
            credentials = file("application_default_credentials.json")
        }

        resource "google_compute_instance" "app" {
            name         = "arvoaitech"
            machine_type = "e2-micro"
            zone         = "us-central1-a"

            boot_disk {
                initialize_params {
                    image = "projects/debian-cloud/global/images/family/debian-11"
                }
            }

            network_interface {
                network = "default"
                access_config {}
            }

            metadata_startup_script = <<-EOT
            #!/bin/bash
            apt-get update
            apt-get install -y python3-pip git
            git clone https://github.com/Arvo-AI/hello_world.git /app
            cd /app
            pip3 install -r requirements.txt
            python3 app.py

            # Serve HTML/CSS files
            # cp -r /app/static/* /var/www/html/
            # systemctl restart nginx
            
            EOT
        }
            output "vm_public_ip" {
                value = google_compute_instance.app.network_interface[0].access_config[0].nat_ip
            }
        