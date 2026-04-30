# open-data-ai-analytics

## Мета проєкту
Проєкт для лабораторної роботи з дисципліни «Середовище та компоненти розробки у моделюванні і аналізі даних».
Мета: завантажити відкриті дані, перевірити їх якість, провести дослідження та побудувати візуалізації.

## Джерело даних
Набір даних: «Дані щодо кількості зареєстрованих безробітних та кількості зареєстрованих вакансій за окремими характеристиками» (data.gov.ua).
Посилання: https://data.gov.ua/dataset/333

## Питання/гіпотези для аналізу (версія А + B)
1. Чи є суттєва різниця в кількості зареєстрованих безробітних між регіонами України?
2. Які види економічної діяльності найбільше представлені у структурі зареєстрованого безробіття в різних регіонах?
3. Чи існує зв’язок між загальною кількістю зареєстрованих безробітних у регіоні та чисельністю безробітних, які раніше працювали в окремих галузях економіки?

## Структура проєкту
- data/raw — вхідний Excel-файл
- db — SQLite база даних
- reports — згенеровані звіти
- reports/figures — графіки
- src/data_load — сервіс завантаження даних у SQLite
- src/data_quality_analysis — сервіс перевірки якості
- src/data_research — сервіс дослідження даних
- src/visualization — сервіс побудови графіків
- web — веб-інтерфейс
- compose.yaml — спільний запуск усіх сервісів

## Сервіси
- data_load: читає Excel і записує таблиці в SQLite
- data_quality_analysis: перевіряє якість даних і формує звіт
- data_research: виконує базове дослідження та формує аналітичні файли
- visualization: будує графіки
- web: показує результати в браузері

## Запуск
```bash
docker compose up --build


## Azure deployment with Terraform

This project can be deployed to Microsoft Azure using Terraform, Azure Cloud Shell and cloud-init.

The deployment is based on the Docker Compose project prepared in the previous laboratory work. Terraform creates the Azure infrastructure, and cloud-init automatically configures the Linux virtual machine during its first boot.

### Project infrastructure

Terraform creates the following Azure resources:

- Resource Group
- Virtual Network
- Subnet
- Public IP
- Network Security Group
- Network Interface
- Linux Virtual Machine

The Linux VM is configured automatically using cloud-init. During the first boot, cloud-init performs the following actions:

- updates system packages;
- installs Docker;
- installs Docker Compose plugin;
- clones this GitHub repository;
- starts the application using Docker Compose.

The application is available through the public IP address of the virtual machine on port `8000`.

### Requirements

Before running the deployment, the following requirements must be met:

- active Microsoft Azure subscription;
- Azure Cloud Shell opened in Bash mode;
- Terraform configuration files located in `infra/terraform`;
- public GitHub repository with the project source code.

### Run deployment

Open Azure Portal and start Azure Cloud Shell in Bash mode.

Clone the repository:

```bash
git clone https://github.com/MariaBrychko/open-data-ai-analytics.git
cd open-data-ai-analytics/infra/terraform
```

Create an SSH key if it does not already exist:

```bash
test -f ~/.ssh/id_rsa.pub || ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```

Create the `terraform.tfvars` file:

```bash
cat > terraform.tfvars <<EOF
subscription_id = "$(az account show --query id -o tsv)"
repo_url = "https://github.com/MariaBrychko/open-data-ai-analytics.git"
resource_group_name = "rg-open-data-ai-analytics-lab4"
location = "northeurope"
project_name = "odaia"
web_port = 8000
EOF
```

Initialize Terraform:

```bash
terraform init
```

Format Terraform files:

```bash
terraform fmt
```

Validate the configuration:

```bash
terraform validate
```

Preview the infrastructure plan:

```bash
terraform plan
```

Apply the Terraform configuration:

```bash
terraform apply
```

When Terraform asks for confirmation, type:

```text
yes
```

After successful deployment, Terraform outputs the public IP address and the web application URL.

### Check deployment result

Get the public web URL:

```bash
terraform output -raw web_url
```

Check the web application from Cloud Shell:

```bash
curl -I "$(terraform output -raw web_url)"
```

Open the application in a browser:

```text
http://PUBLIC_IP:8000
```

The page should display the web interface of the analytical application.

### Check Docker containers on the VM

To check that Docker Compose is running on the Azure VM, connect through SSH:

```bash
PUBLIC_IP=$(terraform output -raw public_ip)
ssh -o StrictHostKeyChecking=no azureuser@$PUBLIC_IP
```

Go to the project directory:

```bash
cd /opt/open-data-ai-analytics
```

Check running containers:

```bash
sudo docker compose ps
```

The `web_service` container should be running. Other analytical containers may have the `Exited (0)` status, because they execute data processing tasks and finish successfully.

Exit the VM:

```bash
exit
```

### Destroy infrastructure

After the demonstration, remove all Azure resources:

```bash
terraform destroy
```

When Terraform asks for confirmation, type:

```text
yes
```

After that, check that the resource group was removed:

```bash
az group exists --name rg-open-data-ai-analytics-lab4
```

The expected result is:

```text
false
```

This step is important because Azure resources may consume free trial credits while they exist.

## Monitoring with Prometheus and Grafana

The project includes a monitoring stack for the Azure Docker deployment.

The monitoring stack contains:

- Prometheus
- Grafana
- Node Exporter
- cAdvisor

Prometheus collects metrics from:

- Prometheus itself
- Azure Linux VM through Node Exporter
- Docker containers through cAdvisor
- Flask web application through the `/metrics` endpoint

The monitoring configuration is located in:

```text
monitoring/
├── prometheus/
│   └── prometheus.yml
└── docker-compose.monitoring.yml
```

### Open ports

The following ports are used:

- `8000` — web application
- `3000` — Grafana
- `9090` — Prometheus
- `22` — SSH access

### Start monitoring on the VM

Connect to the Azure VM:

```bash
ssh azureuser@PUBLIC_IP
```

Go to the project directory:

```bash
cd /opt/open-data-ai-analytics/monitoring
```

Start the monitoring services:

```bash
sudo docker compose -f docker-compose.monitoring.yml up -d
```

Check all containers:

```bash
sudo docker ps -a
```

### Open services

Web application:

```text
http://PUBLIC_IP:8000
```

Prometheus:

```text
http://PUBLIC_IP:9090
```

Prometheus targets:

```text
http://PUBLIC_IP:9090/targets
```

Grafana:

```text
http://PUBLIC_IP:3000
```

Default Grafana login:

```text
admin
admin
```

In Grafana, Prometheus is added as a data source with the following internal URL:

```text
http://prometheus:9090
```

### Dashboard panels

The Grafana dashboard contains panels for:

- VM CPU usage
- VM memory usage
- Docker containers state
- web container resource usage
- Flask application request metrics