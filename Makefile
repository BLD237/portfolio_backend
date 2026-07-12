.PHONY: deploy-nginx install-ssl deploy-all

deploy-nginx:
	@echo "Deploying Nginx configurations..."
	sudo cp nginx/muforbelmond.tech.conf /etc/nginx/sites-available/
	sudo cp nginx/admin.muforbelmond.tech.conf /etc/nginx/sites-available/
	sudo cp nginx/api.muforbelmond.tech.conf /etc/nginx/sites-available/
	sudo ln -sf /etc/nginx/sites-available/muforbelmond.tech.conf /etc/nginx/sites-enabled/
	sudo ln -sf /etc/nginx/sites-available/admin.muforbelmond.tech.conf /etc/nginx/sites-enabled/
	sudo ln -sf /etc/nginx/sites-available/api.muforbelmond.tech.conf /etc/nginx/sites-enabled/
	sudo nginx -t
	sudo systemctl reload nginx

install-ssl:
	@echo "Installing SSL certificates via Certbot..."
	sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx
	sudo certbot --nginx -d muforbelmond.tech -d www.muforbelmond.tech -d admin.muforbelmond.tech -d api.muforbelmond.tech --non-interactive --agree-tos --redirect -m muforbelmond20@gmail.com

deploy-all: deploy-nginx install-ssl
	@echo "Nginx configurations and SSL certificates successfully deployed!"
