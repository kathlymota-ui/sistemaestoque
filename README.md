# Sistema de Estoque

Sistema de linha de comando para controle de entrada e saída de mercadorias com leitura de código de barras (o leitor USB age como um teclado: basta "bipar" no campo de código).

## Funcionalidades
- Cadastro de produtos (código de barras, nome, preço, estoque mínimo)
- Entrada de mercadoria
- Saída de mercadoria (bloqueia se o saldo for insuficiente)
- Alerta de estoque baixo
- Consulta do estoque atual
- Histórico das últimas movimentações

## Tecnologias
Python 3 e SQLite (nenhuma dependência externa).

## Como executar
```bash
git clone https://github.com/k41h/sistemaestoque.git
cd sistemaestoque
python3 estoque.py
```
O banco `estoque.db` é criado automaticamente na primeira execução.

## Autora
Kathly Victoria Marçal da Mota - ADS 5A, FIT
