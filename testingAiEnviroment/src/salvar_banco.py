# Arquivo criado para designar todas as responsabilidades de salvar as mensagens no banco de dados,
# assim, desacoplando o codigo do arquivo app.py deixando apenas os chamados das funçoes
# codigo limpo, matheus feliz :)
import os
import sqlite3
import logging

class DatabaseGerenciador:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.inicializar_banco()

    def _conectar(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    def inicializar_banco(self):
        if os.path.exists(self.db_path):
            logging.info("Banco já existe em %s. Pulando criação.", self.db_path)
            return
        
        logging.info("Banco de dados não encontrado em %s. Criando...", self.db_path)
        try:
            conn = self._conectar()
            cur = conn.cursor()

            cur.executescript("""
                CREATE TABLE IF NOT EXISTS estados (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    estado        TEXT UNIQUE,
                    mensagem      TEXT,
                    link_tutorial TEXT
                );
                CREATE TABLE IF NOT EXISTS opcoes (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    estado_origem TEXT,
                    opcao         TEXT,
                    estado_destino TEXT
                );
                CREATE TABLE IF NOT EXISTS avaliacoes (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    estrelas_avaliacao REAL,
                    mensagem          TEXT,
                    data_criacao      DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS links (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_tutorial TEXT,
                    url          TEXT
                );
            """) 

            conn.commit()
            conn.close()
            os.chmod(self.db_path, 0o666)
            logging.info("Banco de dados inicializado com sucesso.")
        except Exception as e:
            logging.error("Erro ao inicializar o banco de dados: %s", e)

#metodos

    def buscar_mensagem(self, estado: str) -> tuple[str, str | None]:    
        conn = self._conectar()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT e.mensagem, l.url
            FROM estados e
            LEFT JOIN links l on l.nome_tutorial = e.link_tutorial
            WHERE e.estado = ?
            ORDER BY e.id DESC limit 1
            """, 
            (estado,),
        )

        res = cur.fetchone()
        conn.close()
        return (res[0], res[1]) if res else ("Erro: estado não encontrado", None)
    
    def buscar_transicao(self, estado: str, opcao: str) -> str | None:
        conn = self._conectar()
        cur = conn.cursor()
        cur.execute(
            "SELECT estado_destino FROM opcoes "
            "WHERE estado_origem = ? AND opcao = ? ORDER BY id DESC LIMIT 1",
            (estado, opcao),
        )
        res = cur.fetchone()
        conn.close()
        return res[0] if res else None
    
    def listar_opcoes(self, estado: str) -> list[str]:
        conn = self._conectar()
        cur = conn.cursor()
        cur.execute(
            "SELECT opcao FROM opcoes WHERE estado_origem = ? ORDER BY id ASC",
            (estado,),
        )

        opcoes = [row[0] for row in cur.fetchall()]
        conn.close()
        return opcoes
    
    def salvar_avaliacao(self, estrelas: float, mensagem: str | None):
        conn = self._conectar()
        cur = conn.cursor()
        cur.execute (
            "INSERT INTO avaliacoes (estrelas_avaliacao, mensagem) VALUES (?, ?)",
            (float(estrelas), mensagem or None),
        )

        conn.commit()
        conn.close()


    def update_mensagem_humanizada(self, estado: str, nova_mensagem: str):
        conn = self._conectar()
        cur = conn.cursor()
        cur.execute(
            "UPDATE estados SET mensagem_humanizada = ? WHERE estado = ?",
            (nova_mensagem, estado)
        )
        conn.commit()
        conn.close()

    #TESTAR SE O UPDATE FUNCIONA, SE NAO FUNCIONAR, TENTAR A POSSIBILIDADE DE UM PROMPT MELHOR PARA CORREÇÃO DE ERROS AUTOMATICAS
    #COMANDO A SER EXECUTADO PARA DAR UPDATE NO BANCO DE DADOS: python salvar_banco.py --update-mensagem-humanizada "estado" "nova_mensagem"
    