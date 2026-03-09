# 📌 Sticky Desktop

Post-it multiplataforma para área de trabalho — Python + PyQt6.

---

## ⚡ Instalação rápida (Debian/Ubuntu + GNOME)

```bash
bash install.sh
```

O script instala o PyQt6, copia os arquivos, cria o atalho no menu do GNOME
e pergunta se deve iniciar com o sistema.

---

## 🖐 Instalação manual

```bash
# 1. Instalar dependência
pip3 install PyQt6 --break-system-packages

# 2. Rodar
python3 main.py
```

---

## 🎮 Como usar

| Ação | Como |
|------|------|
| Criar nota | Clique no ícone 📝 na barra do sistema → **Novo Post-it** |
| Mover nota | Arraste pelo cabeçalho colorido |
| Editar título | Clique no texto do título |
| Adicionar conteúdo | Botão **＋** no canto inferior direito |
| Mudar cor | Botão 🎨 no cabeçalho |
| Fechar nota | Botão **✕** (nota fica salva) |
| Mostrar/ocultar todas | Menu do ícone na barra |

### Tipos de bloco disponíveis
- 📝 **Texto livre** — anotação simples
- ☑ **Checklist** — tarefa com checkbox
- 🔗 **Link** — URL clicável
- 💬 **Comentário** — observação

---

## 🗂 Estrutura do projeto

```
sticky-desktop/
├── main.py                 # Ponto de entrada
├── ui/
│   ├── app.py              # App + System Tray
│   └── postit_window.py    # Janela do Post-it
├── core/
│   └── postit_manager.py   # Lógica de negócio
├── models/
│   ├── postit.py           # Modelo PostIt
│   └── block.py            # Modelo Block
├── storage/
│   └── database.py         # Leitura/escrita JSON
├── data/
│   └── postits.json        # Dados persistidos
└── install.sh              # Instalador Linux
```

---

## 💾 Onde ficam os dados

As notas são salvas automaticamente em:
```
sticky-desktop/data/postits.json
```

---

## 🚀 Próximas evoluções planejadas

- [ ] Atalho global verdadeiro (python-xlib)
- [ ] Exportar notas como PDF/TXT
- [ ] Sincronização em nuvem
- [ ] Notificações com lembrete
- [ ] Tema escuro
- [ ] Empacotar com PyInstaller
