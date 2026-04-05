with open('docker-compose.yml', 'r') as f:
    content = f.read()

# O código do nosso novo painel
pgadmin_service = """
  pgadmin:
    image: dpage/pgadmin4
    container_name: enem-brasil-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@provapop.com.br
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    networks:
      - enem-network
    depends_on:
      - db
"""

# Procurar onde terminam os serviços e inserir o pgadmin
if 'volumes:' in content:
    content = content.replace('volumes:', pgadmin_service + '\nvolumes:')
    with open('docker-compose.yml', 'w') as f:
        f.write(content)
    print("✅ Painel pgAdmin configurado com sucesso na infraestrutura!")
else:
    print("❌ Ops, algo deu errado. Me avise no chat.")
