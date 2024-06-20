#!/bin/bash

# Define a matrícula como uma constante

# Executa o programa Python com a matrícula e armazena a saída na variável OUTPUT
sas1=$(python3 TP0/main.py rubick.snes.2advanced.dev 51001 itr 2021032218 0)

# Executa o programa Python com a matrícula e armazena a saída na variável OUTPUT
sas2=$(python3 TP0/main.py rubick.snes.2advanced.dev 51001 itr 2021031947 0)

# Executa o programa Python com a matrícula e armazena a saída na variável OUTPUT
OUTPUT=$(python3 TP0/main.py rubick.snes.2advanced.dev 51001 gtr 2 "$sas1" "$sas2")

# Imprime a saída
echo "$OUTPUT"
echo "$OUTPUT" > TP0/gas.txt