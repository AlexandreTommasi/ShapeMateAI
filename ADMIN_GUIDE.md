# 🔧 Como Gerenciar Contas de Usuários - ShapeMateAI

## 📋 Ferramenta de Administração

Para gerenciar as contas cadastradas no sistema, você pode usar a ferramenta administrativa incluída no projeto.

### 🚀 Como Executar

```bash
cd "c:\Users\CODE-DATA-09\Desktop\faculdade\ShapeMateAI"
python admin_tools.py
```

### 📋 Funcionalidades Disponíveis

#### 1. **📋 Listar Usuários**
- Mostra todos os usuários cadastrados
- Exibe: ID, Email, Nome e Data de Criação
- Útil para ver quem está cadastrado no sistema

#### 2. **📊 Estatísticas do Banco**
- Contador de usuários, perfis, sessões e mensagens
- Visão geral do uso do sistema

#### 3. **🗑️ Remover Usuário por Email**
- Remove uma conta específica pelo email
- **CUIDADO**: Operação irreversível!
- Remove todos os dados associados (perfil, chats, mensagens)

#### 4. **🗑️ Remover Usuário por ID**
- Remove uma conta específica pelo ID
- Mesma funcionalidade do item 3, mas busca por ID

#### 5. **☢️ Remover TODOS os Usuários**
- **PERIGO MÁXIMO**: Remove todas as contas do sistema
- Requer dupla confirmação
- Use apenas para limpar o banco em desenvolvimento

### ⚠️ Importante

- **Todas as exclusões são PERMANENTES**
- Sempre faça backup do banco antes de remover dados
- Em produção, considere desativar contas ao invés de removê-las

### 💾 Backup do Banco de Dados

Antes de remover contas, faça backup do arquivo:
```
database/shapemate.db
```

### 🔒 Segurança

- A ferramenta deve ser usada apenas por administradores
- Nunca execute em produção sem backup
- Confirme sempre antes de executar operações destrutivas

---

**Exemplo de Uso:**

1. Execute: `python admin_tools.py`
2. Digite `1` para listar usuários
3. Digite `3` para remover por email
4. Insira o email: `usuario@exemplo.com`
5. Digite `CONFIRMAR` para prosseguir

✅ **Usuário removido com sucesso!**
