#!/bin/bash

# Define a matrícula como uma constante

# Executa o programa Python com a matrícula e armazena a saída na variável OUTPUT
gas=$(./TP0/generate_gas.sh)

OUTPUT=$(python3 testes/send_first_gas.py rubick.snes.2advanced.dev 51564 "$gas")

# Imprime a saída
echo "$OUTPUT"