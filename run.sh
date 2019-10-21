echo "Iniciando novo log" > log
for y in instances/*.stp;
do
  echo "Teste: Instancia $y" >> log
  date >> log
  python3 main.py "$y" >> log
  date >>  log
 done;