DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export AI_STACK_DIR="$DIR"

SOFTWARE=(
    "ollama" "Install Ollama" OFF
    "sglang" "Install SGLang" OFF
    "vllm" "Install vLLM" OFF
    "litellm" "Install LiteLLM" OFF
    "open-webui" "Install Open WebUI" OFF
)

install_docker() {
    # Add Docker's official GPG key:
    apt update
    apt install -y ca-certificates curl
    install -m 0755 -d /etc/apt/keyrings
    if [ ! -f /etc/apt/keyrings/docker.asc ]; then
        curl -fsSL https://download.docker.com/linux/debian/gpg \
            -o /etc/apt/keyrings/docker.asc
        chmod a+r /etc/apt/keyrings/docker.asc
    fi

    # Add the repository to Apt sources:
    if [ ! -f /etc/apt/sources.list.d/docker.sources ]; then
        tee /etc/apt/sources.list.d/docker.sources <<EOF
        Types: deb
        URIs: https://download.docker.com/linux/debian
        Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
        Components: stable
        Architectures: $(dpkg --print-architecture)
        Signed-By: /etc/apt/keyrings/docker.asc
EOF
    fi

    apt update

    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    systemctl enable --now docker
}

select_software() {
    SELECTION=$(whiptail \
        --title "AI Stack Setup" \
        --checklist "Select software to install:" \
        20 70 10 \
        "${SOFTWARE[@]}" \
        3>&1 1>&2 2>&3)

    if [ $? -ne 0 ]; then
        echo "Installation cancelled."
        exit 1
    fi

    SERVICES=()

    for service in $SELECTION; do
        SERVICES+=("${service//\"/}")
    done

    if [ "${#SERVICES[@]}" -eq 0 ]; then
        echo "No software selected."
        exit 1
    fi

    for service in "${SERVICES[@]}"; do
        if ! install_service "$service"; then
            echo "Failed installing $service"
            exit 1
        fi
    done

    mkdir -p /var/lib/ai-stack
    printf "%s\n" "${SERVICES[@]}" > /var/lib/ai-stack/services
}

select_architecture() {
    read -p "Architecture [NVIDIA/amd/intel/cpu]: " ARCHITECTURE
    ARCHITECTURE=${ARCHITECTURE:-nvidia}
    ARCHITECTURE=$(echo "$ARCHITECTURE" | tr '[:upper:]' '[:lower:]')
}

check_compose_file() {
    if [ ! -f "$service_dir/docker-compose.yml" ]; then
        echo "No docker-compose.yml found for $service"
        return 1
    fi
}

install_service() {
    local service="$1"

    echo
    echo "================================"
    echo "Installing: $service"
    echo "================================"

    case "$service" in
        ollama)
            install_ollama
            ;;

        sglang|vllm)
            select_architecture
            install_docker_container "$service" "$ARCHITECTURE"
            ;;

        litellm|open-webui|searxng)
            install_docker_container "$service"
            ;;

        *)
            echo "Unknown service: $service"
            return 1
            ;;
    esac
}

install_docker_container() {
    local service="$1"
    local profile="$2"

    local service_dir="$AI_STACK_DIR/services/$service"

    if [ ! -d "$service_dir" ]; then
        echo "Service directory not found: $service_dir"
        return 1
    fi

    cd "$service_dir" || return 1

    check_compose_file || return 1

    if [ -n "$profile" ]; then
        local env_file="${profile}.env"
        local compose_args=(-f docker-compose.yml)

        if [ ! -f "$env_file" ]; then
            echo "Missing environment file: $env_file"
            return 1
        fi

        if [ -f "docker-compose.${profile}.yml" ]; then
            compose_args+=(-f "docker-compose.${profile}.yml")
        fi

        docker compose \
            "${compose_args[@]}" \
            --env-file "$env_file" \
            up -d
    else
        docker compose up -d
    fi
}

install_ollama() {
    /bin/bash "$AI_STACK_DIR/services/ollama/install.sh"
}

main() {
    # Ensure Root
    if [ "$EUID" -ne 0 ]; then
      echo "Run as root (su)"
      exit 1
    fi

    # Check Docker and install if not already
    if command -v docker >/dev/null 2>&1; then
        echo "Docker already installed."
    else
        install_docker
    fi

    systemctl is-active --quiet docker || systemctl start docker

    docker info >/dev/null || {
        echo "Docker is installed but not working."
        exit 1
    }

    # Create hf_cache
    docker volume create hf_cache

    # Software selection
    select_software
}

main "$@"
