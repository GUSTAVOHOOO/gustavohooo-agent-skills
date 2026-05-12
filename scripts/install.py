import os
import sys
import urllib.request
import zipfile
import io
import shutil

def install_skill(skill_path):
    repo_url = "https://github.com/GUSTAVOHOOO/gustavohooo-agent-skills/archive/refs/heads/main.zip"
    base_folder_in_zip = "gustavohooo-agent-skills-main/"
    
    print(f"🚀 Preparando para instalar: {skill_path}")
    
    try:
        # Baixa o repositório como ZIP em memória para ser rápido
        print("📥 Baixando biblioteca (apenas as partes necessárias)...")
        with urllib.request.urlopen(repo_url) as response:
            zip_data = response.read()
        
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            # Filtra os arquivos que pertencem à pasta da skill solicitada
            target_prefix = base_folder_in_zip + skill_path.replace('\\', '/')
            if not target_prefix.endswith('/'):
                target_prefix += '/'
                
            skill_files = [f for f in z.namelist() if f.startswith(target_prefix)]
            
            if not skill_files:
                print(f"❌ Erro: Skill '{skill_path}' não encontrada no repositório.")
                print("💡 Dica: Verifique o caminho no CATALOG.md (ex: cloud/azure/azure-ai-projects)")
                return

            print(f"📦 Extraindo {len(skill_files)} arquivos...")
            
            # Pega o nome da pasta final (ex: azure-ai-projects)
            skill_name = os.path.basename(skill_path.rstrip('/\\'))
            
            if os.path.exists(skill_name):
                print(f"⚠️  A pasta '{skill_name}' já existe. Deseja sobrescrever? (s/n)")
                if input().lower() != 's':
                    print("Instalação cancelada.")
                    return
                shutil.rmtree(skill_name)

            os.makedirs(skill_name)

            for file_info in z.infolist():
                if file_info.filename.startswith(target_prefix) and not file_info.is_dir():
                    # Extrai o arquivo removendo o prefixo do caminho original
                    relative_path = file_info.filename[len(target_prefix):]
                    target_path = os.path.join(skill_name, relative_path)
                    
                    # Cria subpastas se necessário
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    with z.open(file_info) as source, open(target_path, "wb") as target:
                        shutil.copyfileobj(source, target)

            print(f"✅ Sucesso! Skill '{skill_name}' instalada na pasta atual.")
            print(f"📂 Caminho: {os.path.abspath(skill_name)}")

    except Exception as e:
        print(f"💥 Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❓ Uso: python install.py <caminho/da/skill>")
        print("📖 Exemplo: python install.py cloud/azure/azure-ai-projects")
    else:
        install_skill(sys.argv[1])
