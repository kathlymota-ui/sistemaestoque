#!/usr/bin/env python3
"""Sistema de Estoque - cadastro de produtos e movimentação (entrada/saída)
com leitura de código de barras (leitor USB funciona como teclado)."""
import sqlite3
from datetime import datetime

DB = "estoque.db"


def conectar():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("""CREATE TABLE IF NOT EXISTS produtos (
        codigo_barras TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        preco REAL NOT NULL DEFAULT 0,
        quantidade INTEGER NOT NULL DEFAULT 0,
        estoque_minimo INTEGER NOT NULL DEFAULT 0)""")
    con.execute("""CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_barras TEXT NOT NULL REFERENCES produtos(codigo_barras),
        tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA','SAIDA')),
        quantidade INTEGER NOT NULL CHECK (quantidade > 0),
        data_hora TEXT NOT NULL)""")
    return con


def ler_int(msg, minimo=0):
    while True:
        try:
            v = int(input(msg).strip())
            if v >= minimo:
                return v
        except ValueError:
            pass
        print(f"  Valor inválido (inteiro >= {minimo}).")


def ler_float(msg):
    while True:
        try:
            v = float(input(msg).strip().replace(",", "."))
            if v >= 0:
                return v
        except ValueError:
            pass
        print("  Valor inválido.")


def cadastrar(con):
    codigo = input("Código de barras: ").strip()
    if not codigo:
        return print("  Código obrigatório.")
    if con.execute("SELECT 1 FROM produtos WHERE codigo_barras=?", (codigo,)).fetchone():
        return print("  Produto já cadastrado.")
    nome = input("Nome: ").strip()
    if not nome:
        return print("  Nome obrigatório.")
    preco = ler_float("Preço (R$): ")
    minimo = ler_int("Estoque mínimo: ")
    con.execute("INSERT INTO produtos VALUES (?,?,?,0,?)", (codigo, nome, preco, minimo))
    con.commit()
    print(f"  ✔ '{nome}' cadastrado.")


def movimentar(con, tipo):
    codigo = input("Bipe o código de barras: ").strip()
    p = con.execute("SELECT nome, quantidade, estoque_minimo FROM produtos WHERE codigo_barras=?",
                    (codigo,)).fetchone()
    if not p:
        return print("  Produto não encontrado. Cadastre primeiro.")
    nome, saldo, minimo = p
    qtd = ler_int(f"Quantidade de {tipo.lower()} de '{nome}': ", 1)
    if tipo == "SAIDA" and qtd > saldo:
        return print(f"  ✖ Saldo insuficiente (disponível: {saldo}).")
    novo = saldo + qtd if tipo == "ENTRADA" else saldo - qtd
    con.execute("UPDATE produtos SET quantidade=? WHERE codigo_barras=?", (novo, codigo))
    con.execute("INSERT INTO movimentacoes (codigo_barras,tipo,quantidade,data_hora) VALUES (?,?,?,?)",
                (codigo, tipo, qtd, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    con.commit()
    print(f"  ✔ {tipo} registrada. Saldo de '{nome}': {novo}")
    if novo <= minimo:
        print(f"  ⚠ ALERTA: estoque baixo (mínimo: {minimo}).")


def listar(con):
    linhas = con.execute("SELECT codigo_barras,nome,preco,quantidade,estoque_minimo "
                         "FROM produtos ORDER BY nome").fetchall()
    if not linhas:
        return print("  Nenhum produto cadastrado.")
    print(f"\n{'CÓDIGO':<15}{'NOME':<25}{'PREÇO':>10}{'QTD':>6}  STATUS")
    for c, n, pr, q, m in linhas:
        status = "BAIXO" if q <= m else "ok"
        print(f"{c:<15}{n[:24]:<25}{pr:>10.2f}{q:>6}  {status}")


def historico(con):
    linhas = con.execute("""SELECT m.data_hora, p.nome, m.tipo, m.quantidade
                            FROM movimentacoes m JOIN produtos p USING (codigo_barras)
                            ORDER BY m.id DESC LIMIT 15""").fetchall()
    if not linhas:
        return print("  Sem movimentações.")
    print(f"\n{'DATA/HORA':<21}{'PRODUTO':<25}{'TIPO':<9}QTD")
    for d, n, t, q in linhas:
        print(f"{d:<21}{n[:24]:<25}{t:<9}{q}")


def main():
    con = conectar()
    acoes = {"1": lambda: cadastrar(con), "2": lambda: movimentar(con, "ENTRADA"),
             "3": lambda: movimentar(con, "SAIDA"), "4": lambda: listar(con),
             "5": lambda: historico(con)}
    while True:
        print("\n=== SISTEMA DE ESTOQUE ===\n1 Cadastrar produto\n2 Entrada de mercadoria\n"
              "3 Saída de mercadoria\n4 Consultar estoque\n5 Histórico\n0 Sair")
        op = input("Opção: ").strip()
        if op == "0":
            break
        acoes.get(op, lambda: print("  Opção inválida."))()


if __name__ == "__main__":
    main()
